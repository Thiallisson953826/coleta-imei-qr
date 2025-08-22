import streamlit as st
import qrcode
import os
import re
from io import BytesIO
from fpdf import FPDF

# Pastas de saída
os.makedirs("qrcodes", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

st.set_page_config(page_title="📱 Coleta IMEI - QR Code", layout="centered")

# Inicializar sessão
if "caixas" not in st.session_state:
    st.session_state["caixas"] = {}

st.title("📦 Coleta de IMEIs e Geração de QR Code")

# Função para limpar IMEI (remove prefixos e pega só números)
def limpar_imei(raw):
    return re.sub(r"\D", "", raw)

# Função para gerar QR Code
def gerar_qrcode(texto, filename):
    qr = qrcode.QRCode(version=1, box_size=6, border=4)
    qr.add_data(texto)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(filename)

# Função para gerar PDF com 10 QR Codes por página (2 col x 5 lin)
def gerar_pdf(caixas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for caixa, imeis in caixas.items():
        if not imeis:
            continue
        for i, imei in enumerate(imeis):
            # Nova página a cada 10 QR Codes
            if i % 10 == 0:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(200, 10, f"Caixa {caixa}", ln=True, align="C")

            filename = f"qrcodes/{caixa}_{imei}.png"
            texto_qr = "\n".join([imei])  # cada IMEI em linha separada
            gerar_qrcode(texto_qr, filename)

            # Posicionamento 2 col x 5 linhas
            col = (i % 10) % 2
            row = (i % 10) // 2
            x = 25 + col * 90
            y = 30 + row * 50

            pdf.image(filename, x=x, y=y, w=40, h=40)
            pdf.set_xy(x, y + 42)
            pdf.set_font("Arial", size=8)
            pdf.multi_cell(40, 5, f"{caixa}\n{imei}", align="C")

    pdf_output = "pdfs/qrcodes_final.pdf"
    pdf.output(pdf_output)
    return pdf_output

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

    # Mostrar IMEIs, um por linha
    st.subheader(f"📋 IMEIs da {caixa_atual}")
    st.text("\n".join(st.session_state["caixas"][caixa_atual]))

# Gerar QR Code de uma caixa
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
    import pandas as pd
    df = pd.DataFrame(linhas)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="IMEIs")
    st.download_button("📥 Baixar Excel", excel_buffer.getvalue(), file_name="imeis_coletados.xlsx")

# Gerar PDF com todos os QR Codes
if st.session_state["caixas"] and st.button("📄 Gerar PDF com QR Codes"):
    pdf_path = gerar_pdf(st.session_state["caixas"])
    with open(pdf_path, "rb") as f:
        st.download_button("⬇️ Baixar PDF Final", f, file_name="qrcodes_final.pdf")
