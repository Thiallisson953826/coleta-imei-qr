import streamlit as st
import qrcode
from fpdf import FPDF
import os
import tempfile

# Função para gerar o PDF com até 8 QR Codes por página (caixas diferentes)
def gerar_pdf(qrcodes, caixas):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    qr_size = 60   # tamanho do QR Code em mm (maior)
    margin = 20    # margem entre QR Codes
    colunas = 4    # até 4 colunas por página
    linhas = 2     # até 2 linhas por página (8 QR Codes)

    for i, (qr_img, caixa) in enumerate(zip(qrcodes, caixas)):
        if i % 8 == 0:  # nova página a cada 8 QR Codes
            pdf.add_page()

        # posição (coluna e linha) dentro da página
        x = margin + (i % colunas) * (qr_size + margin)
        y = margin + ((i % 8) // colunas) * (qr_size + margin + 10)

        # salvar imagem temporária do QR
        temp_qr = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        qr_img.save(temp_qr.name)

        # adicionar QR Code
        pdf.image(temp_qr.name, x, y, qr_size, qr_size)

        # legenda com número da caixa
        pdf.set_xy(x, y + qr_size + 2)
        pdf.set_font("Arial", size=10)
        pdf.cell(qr_size, 8, f"Caixa: {caixa}", align="C")

        # excluir imagem temporária
        os.unlink(temp_qr.name)

    return pdf

# Interface Streamlit
st.title("📦 Gerador de QR Codes por Caixa")

st.write("Digite o número das caixas, um por linha. O sistema vai gerar até **8 QR Codes por página**, cada um de uma caixa diferente.")

# Entrada de dados
caixas_input = st.text_area("Números das caixas (um por linha):")

if st.button("Gerar QR Codes em PDF"):
    if caixas_input.strip():
        caixas = [c.strip() for c in caixas_input.split("\n") if c.strip()]

        qrcodes = []
        for caixa in caixas:
            qr = qrcode.make(caixa)
            qrcodes.append(qr)

        pdf = gerar_pdf(qrcodes, caixas)

        # salvar PDF temporário
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
        pdf.output(temp_pdf.name)

        with open(temp_pdf.name, "rb") as f:
            st.download_button(
                label="📥 Baixar PDF com QR Codes",
                data=f,
                file_name="qrcodes_caixas.pdf",
                mime="application/pdf"
            )

        os.unlink(temp_pdf.name)
    else:
        st.warning("⚠️ Digite pelo menos uma caixa.")
