import streamlit as st
import qrcode
import pandas as pd
from io import BytesIO
import zipfile
from fpdf import FPDF
import os
import tempfile

st.set_page_config(page_title="📱 Coleta IMEI - QR Code", layout="centered")
st.title("📱 Gerador de QR Code para IMEIs")

# Upload de arquivo Excel
uploaded_file = st.file_uploader("📂 Envie sua planilha com IMEIs", type=["xlsx"])

if uploaded_file:
    df = pd.read_excel(uploaded_file)

    if "IMEI" not in df.columns:
        st.error("A planilha deve conter uma coluna chamada 'IMEI'")
    else:
        st.success("Planilha carregada com sucesso ✅")

        qr_codes = []
        zip_buffer = BytesIO()
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=10)
        pdf.add_page()

        # Posições para 6 QR Codes por página
        x_positions = [20, 110]  # 2 colunas
        y_positions = [20, 100, 180]  # 3 linhas

        i = 0
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for idx, imei in enumerate(df["IMEI"]):
                if pd.isna(imei):
                    continue

                # Gera QR Code
                img = qrcode.make(str(imei))
                img_buffer = BytesIO()
                img.save(img_buffer, format="PNG")
                img_buffer.seek(0)

                # Salva no ZIP
                zip_file.writestr(f"{imei}.png", img_buffer.getvalue())

                # Salva temporariamente para o PDF
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmpfile:
                    tmpfile.write(img_buffer.getvalue())
                    tmp_path = tmpfile.name

                # Adiciona ao PDF
                x = x_positions[i % 2]
                y = y_positions[(i // 2) % 3]
                pdf.image(tmp_path, x=x, y=y, w=80, h=80)

                i += 1

                # Nova página a cada 6 QR Codes
                if i % 6 == 0 and idx + 1 < len(df["IMEI"]):
                    pdf.add_page()

                # Remove imagem temporária
                os.remove(tmp_path)

        # Exporta PDF
        pdf_buffer = BytesIO()
        pdf.output(pdf_buffer, "F")
        pdf_buffer.seek(0)

        # Download ZIP
        st.download_button(
            label="📥 Baixar todas as imagens em ZIP",
            data=zip_buffer,
            file_name="qrcodes.zip",
            mime="application/zip",
        )

        # Download PDF
        st.download_button(
            label="📥 Baixar PDF com QR Codes (6 por página)",
            data=pdf_buffer,
            file_name="qrcodes.pdf",
            mime="application/pdf",
        )
