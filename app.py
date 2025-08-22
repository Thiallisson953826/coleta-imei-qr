import streamlit as st
import qrcode
import os
import re
from fpdf import FPDF

# Criar pastas se não existirem
os.makedirs("qrcodes", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

st.set_page_config(page_title="Gerador de QR Codes de IMEIs", layout="centered")

# Função para limpar IMEI (remove prefixos, mantém só números)
def limpar_imei(raw):
    return re.sub(r"\D", "", raw)

# Função para gerar QR Code
def gerar_qrcode(texto, filename):
    qr = qrcode.QRCode(version=1, box_size=6, border=4)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

# Função para gerar PDF com 10 QR Codes por página
def gerar_pdf(caixas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for caixa, imeis in caixas.items():
        if not imeis:
            continue
        for i, imei in enumerate(imeis):
            if i % 10 == 0:  # Nova página a cada 10 QR Codes
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(200, 10, f"Caixa {caixa}", ln=True, align="C")

            filename = f"qrcodes/{caixa}_{imei}.png"
            texto_qr = f"Caixa: {caixa}\n{imei}"
            gerar_qrcode(texto_qr, filename)

            x = 20 + ((i % 2) * 90)   # duas colunas
            y = 30 + ((i % 10) // 2) * 50
            pdf.image(filename, x=x, y=y, w=40, h=40)
            pdf.set_xy(x, y + 42)
            pdf.set_font("Arial", size=8)
            pdf.cell(40, 10, imei, align="C")

    pdf_output = "pdfs/qrcodes_final.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Inicializar sessão
if "caixas" not in st.session_state:
    st.session_state["caixas"] = {}

st.title("📦 Gerador de QR Codes por Caixa")

# Campo para digitar caixa
caixa_atual = st.text_input("Digite o nome da caixa (ex: Caixa 1)")
if caixa_atual and caixa_atual not in st.session_state["caixas"]:
    st.session_state["caixas"][caixa_atual] = []

# Adicionar IMEIs
if caixa_atual:
    imei_raw = st.text_input("📲 Digite ou bipar IMEI")
    if st.button("➕ Adicionar IMEI"):
        imei = limpar_imei(imei_raw)
        if imei and imei not in st.session_state["caixas"][caixa_atual]:
            st.session_state["caixas"][caixa_atual].append(imei)
            st.success(f"📲 IMEI {imei} adicionado na {caixa_atual}")
        else:
            st.warning("⚠️ IMEI inválido ou já adicionado!")

    # Mostrar lista vertical
    st.subheader(f"📋 IMEIs da {caixa_atual}")
    st.text("\n".join(st.session_state["caixas"][caixa_atual]))

# Gerar todos os QR Codes em PDF
if st.button("📄 Gerar PDF com QR Codes"):
    if any(st.session_state["caixas"].values()):
        pdf_path = gerar_pdf(st.session_state["caixas"])
        with open(pdf_path, "rb") as f:
            st.download_button("⬇️ Baixar PDF Final", f, file_name="qrcodes_final.pdf")
    else:
        st.error("Nenhum IMEI adicionado!")

