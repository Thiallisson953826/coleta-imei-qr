import streamlit as st
import qrcode
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

# Diretório e nome do PDF final
PDF_FILE = "qrcodes_todas_caixas.pdf"

# Inicializa variáveis de sessão
if "caixas" not in st.session_state:
    st.session_state.caixas = {}
if "caixa_atual" not in st.session_state:
    st.session_state.caixa_atual = ""
if "imeis_atual" not in st.session_state:
    st.session_state.imeis_atual = []

# Título do app
st.title("📦 Coletor de IMEIs por Caixa com QR Code")

# Campo para bipar código master da caixa
caixa_input = st.text_input("🔢 Bipar código master da caixa", key="caixa_input")
if caixa_input:
    st.session_state.caixa_atual = caixa_input
    st.session_state.imeis_atual = []
    st.session_state.caixas[caixa_input] = []
    st.experimental_rerun()

# Exibe caixa atual
if st.session_state.caixa_atual:
    st.subheader(f"📦 Caixa atual: {st.session_state.caixa_atual}")

    # Campo para adicionar IMEI
    imei_input = st.text_input("📱 Digite IMEI", key="imei_input")
    if imei_input:
        st.session_state.imeis_atual.append(imei_input)
        st.session_state.caixas[st.session_state.caixa_atual] = st.session_state.imeis_atual
        st.experimental_rerun()

    # Lista de IMEIs adicionados
    st.write("📋 IMEIs adicionados:")
    for imei in st.session_state.imeis_atual:
        st.write(f"- {imei}")

    # Botão para finalizar caixa
    if st.button("✅ Finalizar Caixa"):
        st.session_state.caixa_atual = ""
        st.session_state.imeis_atual = []
        st.experimental_rerun()

# Função para gerar QR Code como imagem
def gerar_qr_code(data):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# Função para gerar PDF com QR Codes
def gerar_pdf(caixas):
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    x, y = 50, height - 100
    count = 0

    for caixa, imeis in caixas.items():
        qr_data = "\n".join(imeis)
        qr_img = gerar_qr_code(qr_data)
        c.drawImage(qr_img, x, y, width=100, height=100)
        c.drawString(x, y - 15, f"Caixa: {caixa}")
        x += 150
        count += 1
        if count % 5 == 0:
            x = 50
            y -= 150
        if count % 10 == 0:
            c.showPage()
            x, y = 50, height - 100

    c.save()
    buffer.seek(0)
    return buffer

# Botão para gerar PDF com todos os QR Codes
if st.button("📄 Gerar PDF com todos os QR Codes"):
    pdf_buffer = gerar_pdf(st.session_state.caixas)
    st.download_button("📥 Baixar PDF", data=pdf_buffer, file_name=PDF_FILE, mime="application/pdf")

