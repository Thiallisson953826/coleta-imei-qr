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

st.title("📦 Coleta de IMEIs e Geração de QR Code")

# Função para limpar IMEI (ignora prefixos, pega só números)
def limpar_imei(raw):
    # Remove tudo que não seja número
    numeros = re.findall(r'\d+', raw)
    return numeros  # Retorna lista de números

# Bipar código master para iniciar nova caixa
codigo_master = st.text_input("📌 Bipar Código Master da Caixa")
if codigo_master:
    if codigo_master not in st.session_state["caixas"]:
        st.session_state["caixas"][codigo_master] = []
        st.success(f"✅ Nova caixa criada: {codigo_master}")

# Selecionar caixa ativa
caixas_disponiveis = list(st.session_state["caixas"].keys())
caixa_atual = st.selectbox("📦 Selecione a caixa", caixas_disponiveis) if caixas_disponiveis else None

# Adicionar IMEIs
if caixa_atual:
    imei_raw = st.text_area("📲 Digite ou bipar IMEIs (um por linha ou todos juntos)")
    if st.button("➕ Adicionar IMEIs"):
        if imei_raw:
            # Limpar e separar IMEIs
            novos_imeis = limpar_imei(imei_raw)
            adicionados = 0
            for imei in novos_imeis:
                if imei not in st.session_state["caixas"][caixa_atual]:
                    st.session_state["caixas"][caixa_atual].append(imei)
                    adicionados += 1
            st.success(f"📲 {adicionados} IMEIs adicionados na {caixa_atual}")

    # Mostrar lista de IMEIs, um por linha
    st.subheader(f"📋 IMEIs da {caixa_atual}")
    st.text("\n".join(st.session_state["caixas"][caixa_atual]))

# Gerar QR Code da caixa
if caixa_atual and st.button("🎯 Gerar QR Code da Caixa"):
    if st.session_state["caixas"][caixa_atual]:
        texto_qr = "\n".join(st.session_state["caixas"][caixa_atual])
        img = qrcode.make(texto_qr)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        st.image(buffer, caption=f"QR Code - {caixa_atual}")
        st.download_button("📥 Baixar QR Code", buffer.getvalue(), file_name=f"{caixa_atual}.png")
    else:
        st.warning("⚠️ Nenhum IMEI na caixa para gerar QR Code!")

# Exportar todas as caixas para Excel
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

# Gerar PDF + ZIP
if st.session_state["caixas"] and st.button("📄 Gerar PDF + ZIP com QR Codes"):
    caixas_selecionadas = list(st.session_state["caixas"].items())
    imagens_qr = []

    # Gerar imagens dos QR Codes
    for caixa, imeis in caixas_selecionadas:
        if not imeis:
            continue
        dados = "\n".join(imeis)  # Cada IMEI em linha separada
        img = qrcode.make(dados)
        img_path = f"qrcodes/{caixa}.png"
        img.save(img_path)
        imagens_qr.append((img_path, caixa))

    # Criar PDF com ReportLab
    pdf_buffer = BytesIO()
    c = canvas.Canvas(pdf_buffer, pagesize=A4)
    width, height = A4
    for img_path, caixa_nome in imagens_qr:
        c.setFont("Helvetica-Bold", 16)
        c.drawString(100, height - 100, f"Caixa: {caixa_nome}")
        c.drawImage(img_path, 100, height - 500, width=300, height=300)
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
