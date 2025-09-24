import streamlit as st
import qrcode
import pandas as pd
from io import BytesIO
import os
from zipfile import ZipFile
from fpdf import FPDF
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
            nome_caixa = f"Caixa_{st.session_state['contador_caixa']}"
            if nome_caixa not in st.session_state["caixas"]:
                st.session_state["caixas"][nome_caixa] = []
            
            st.session_state["caixas"][nome_caixa].append(imei)

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
    excel_buffer.seek(0)
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

    # Criar PDF com FPDF
    pdf = FPDF("P", "mm", "A4")
    pdf.set_auto_page_break(auto=False)
    pdf.add_page()

    qr_size = 60  # tamanho do QR
    margin_x = 20
    margin_y = 20
    gap_x = 20
    gap_y = 30

    positions = [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2),(0,3),(1,3)]  # até 8 por página

    count = 0
    for img_path, caixa_nome in imagens_qr:
        if count % 8 == 0 and count > 0:
            pdf.add_page()
        pos = positions[count % 8]
        x = margin_x + pos[0] * (qr_size + gap_x)
        y = margin_y + pos[1] * (qr_size + gap_y)
        pdf.image(img_path, x=x, y=y, w=qr_size, h=qr_size)
        pdf.set_xy(x, y + qr_size + 2)
        pdf.set_font("Arial", "B", 10)
        pdf.cell(qr_size, 6, caixa_nome, align="C")
        count += 1

    pdf_buffer = BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    # Criar ZIP
    zip_buffer = BytesIO()
    with ZipFile(zip_buffer, "w") as zipf:
        zipf.writestr("qrcodes.pdf", pdf_buffer.getvalue())
        for img_path, _ in imagens_qr:
            with open(img_path, "rb") as f:
                zipf.writestr(os.path.basename(img_path), f.read())
    zip_buffer.seek(0)

    st.download_button(
        "📦 Baixar ZIP com QR Codes e PDF",
        zip_buffer.getvalue(),
        file_name="qrcodes_caixas.zip",
    )
