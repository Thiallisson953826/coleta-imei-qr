import streamlit as st
import qrcode
import pandas as pd
from io import BytesIO
import os
from zipfile import ZipFile
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Garante que a pasta 'qrcodes' exista
os.makedirs("qrcodes", exist_ok=True)

st.set_page_config(page_title="📱 Coleta IMEI - QR Code", layout="centered")

# Sessão para armazenar dados
if "caixas" not in st.session_state:
    st.session_state["caixas"] = {}

st.title("📦 Coleta de IMEIs e Geração de QR Code")

# Bipar código master para iniciar nova caixa
codigo_master = st.text_input("📌 Bipar Código Master da Caixa")

if codigo_master:
    if codigo_master not in st.session_state["caixas"]:
        st.session_state["caixas"][codigo_master] = []
        st.success(f"✅ Nova caixa criada: {codigo_master}")

# Selecionar caixa ativa
caixas_disponiveis = list(st.session_state["caixas"].keys())
if caixas_disponiveis:
    caixa_atual = st.selectbox("📦 Selecione a caixa", caixas_disponiveis)
else:
    caixa_atual = None

# Adicionar IMEIs
if caixa_atual:
    imei = st.text_input("📲 Digite ou bipar IMEI")
    if st.button("➕ Adicionar IMEI"):
        if imei and imei not in st.session_state["caixas"][caixa_atual]:
            st.session_state["caixas"][caixa_atual].append(imei)
            st.success(f"📲 IMEI {imei} adicionado na caixa {caixa_atual}")
        else:
            st.warning("⚠️ IMEI inválido ou já adicionado!")

    # Mostrar lista
    st.subheader(f"📋 IMEIs da {caixa_atual}")
    st.write(st.session_state["caixas"][caixa_atual])

    # Gerar QR Code
    if st.button("🎯 Gerar QR Code da Caixa"):
        dados = "\n".join(st.session_state["caixas"][caixa_atual])
        if not dados:
            st.warning("⚠️ Nenhum IMEI na caixa para gerar QR Code!")
        else:
            img = qrcode.make(dados)
            buffer = BytesIO()
            img.save(buffer, format="PNG")

            st.image(buffer, caption=f"QR Code - {caixa_atual}")
            st.download_button("📥 Baixar QR Code", buffer.getvalue(), file_name=f"{caixa_atual}.png")

# Exportar todas as caixas para Excel
if st.session_state["caixas"]:
    if st.button("📊 Exportar todas as caixas para Excel"):
        linhas = []
        for caixa, imeis in st.session_state["caixas"].items():
            for imei in imeis:
                linhas.append({"Caixa": caixa, "IMEI": imei})
        df = pd.DataFrame(linhas)

        excel_buffer = BytesIO()
        with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False, sheet_name="IMEIs")
        st.download_button(
            "📥 Baixar Excel",
            excel_buffer.getvalue(),
            file_name="imeis_coletados.xlsx",
        )

    # Gerar PDF + ZIP
    if st.button("📄 Gerar PDF + ZIP com QR Codes"):
        caixas_selecionadas = list(st.session_state["caixas"].items())[:10]
        imagens_qr = []

        # Gerar imagens dos QR Codes
        for caixa, imeis in caixas_selecionadas:
            dados = "\n".join(imeis)
            img = qrcode.make(dados)
            img_path = f"qrcodes/{caixa}.png"
            img.save(img_path)
            imagens_qr.append(img_path)

        # Criar PDF com ReportLab
        pdf_buffer = BytesIO()
        c = canvas.Canvas(pdf_buffer, pagesize=A4)
        width, height = A4

        for img_path in imagens_qr:
            caixa_nome = os.path.splitext(os.path.basename(img_path))[0]
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, height - 100, f"Caixa: {caixa_nome}")
            c.drawImage(img_path, 100, height - 500, width=300, height=300)
            c.showPage()

        c.save()

        # Criar ZIP
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "w") as zipf:
            zipf.writestr("qrcodes.pdf", pdf_buffer.getvalue())
            for img_path in imagens_qr:
                with open(img_path, "rb") as f:
                    zipf.writestr(os.path.basename(img_path), f.read())

        st.download_button(
            "📦 Baixar ZIP com QR Codes e PDF",
            zip_buffer.getvalue(),
            file_name="qrcodes_caixas.zip",
        )
