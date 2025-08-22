import streamlit as st
import qrcode
import pandas as pd
from io import BytesIO
import os
from zipfile import ZipFile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import re

# Pastas de saída
os.makedirs("qrcodes", exist_ok=True)

st.set_page_config(page_title="📱 Coleta IMEI - QR Code", layout="centered")

# Inicializar sessão
if "caixas" not in st.session_state:
    st.session_state["caixas"] = {}
if "contador_caixa" not in st.session_state:
    st.session_state["contador_caixa"] = 1

st.title("📦 Coleta de IMEIs e Geração de QR Code")

# Função para limpar IMEIs
def limpar_imei(raw):
    numeros = re.findall(r'\d+', raw)
    return numeros

# Entrada de IMEIs
imei_raw = st.text_area("📲 Digite ou cole IMEIs (um por linha ou todos juntos)")
if st.button("➕ Adicionar IMEIs"):
    if imei_raw:
        novos_imeis = limpar_imei(imei_raw)
        for imei in novos_imeis:
            # Verifica se já existe a caixa atual
            nome_caixa = f"Caixa_{st.session_state['contador_caixa']}"
            if nome_caixa not in st.session_state["caixas"]:
                st.session_state["caixas"][nome_caixa] = []
            
            # Adiciona IMEI na caixa atual
            st.session_state["caixas"][nome_caixa].append(imei)

            # Se a caixa atingir 50 IMEIs, abre nova
            if len(st.session_state["caixas"][nome_caixa]) >= 50:
                st.session_state["contador_caixa"] += 1
        st.success(f"📲 {len(novos_imeis)} IMEIs adicionados com sucesso!")

# Mostrar caixas e IMEIs
for caixa, imeis in st.session_state["caixas"].items():
    st.subheader(f"📦 {caixa} ({len(imeis)} IMEIs)")
    st.text("\n".join(imeis))

# Exportar para Excel
if st.session_state["caixas"] and st.button("📊 Exportar todas as caixas para Excel"):
    linhas = []
    for caixa, imeis in st.session_state["caixas"].items():
        for imei in imeis:
            linhas.append({"Caixa": caixa, "IMEI": imei})
    df = pd.DataFrame(linhas)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="IMEIs")
    st.download_button("📥 Baixar Excel", excel_buffer.getvalue(), file_name="imeis_coletados.xlsx")

# Gerar PDF + ZIP com até 8 QR codes por página
if st.session_state["caixas"] and st.button("📄 Gerar PDF + ZIP com QR Codes"):
    caixas_selecionadas = list(st.session_state["caixas"].items())
    imagens_qr = []

    # Gerar imagens QR
    for caixa, imeis in caixas_selecionadas:
        if not imeis:
            continue
        dados = "\n".join(imeis)
        img = qrcode.make(dados)
        img_path = f"qrcodes/{caixa}.png"
        img.save(img_path)
        imagens_qr.append((img_path, caixa))

    # Criar PDF
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4

    qr_width = 200
    qr_height = 200
    margin_x = 60
    margin_y = 60
    gap_x = 80
    gap_y = 60

    positions = [(0,0),(1,0),(0,1),(1,1)]  # 2 colunas x 2 linhas por "bloco"
    positions = [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2),(0,3),(1,3)]  # até 8 por página

    count = 0
    for img_path, caixa_nome in imagens_qr:
        pos = positions[count % 8]
        x = margin_x + pos[0] * (qr_width + gap_x)
        y = height - margin_y - (pos[1]+1)*(qr_height + gap_y)
        c.drawImage(img_path, x, y, width=qr_width, height=qr_height)
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(x + qr_width/2, y - 15, f"{caixa_nome}")
        count += 1
        if count % 8 == 0:
            c.showPage()
    if count % 8 != 0:
        c.showPage()

    c.save()

    # Criar ZIP
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("qrcodes.pdf", pdf_buffer.getvalue())
        for img_path, _ in imagens_qr:
            with open(img_path, "rb") as f:
                zipf.writestr(os.path.basename(img_path), f.read())

    st.download_button(
        "📦 Baixar ZIP com QR Codes e PDF",
        zip_buffer.getvalue(),
        file_name="qrcodes_caixas.zip",
    )
