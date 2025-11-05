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
if "nce" not in st.session_state:
    st.session_state["nce"] = ""
if "nota" not in st.session_state:
    st.session_state["nota"] = ""

st.title("📦 Coleta de IMEIs e Geração de QR Code")

# ----- CAMPOS NCE E NOTA -----
col_nce, col_nota = st.columns(2)
with col_nce:
    st.session_state["nce"] = st.text_input("📋 NCE do Produto", value=st.session_state["nce"])
with col_nota:
    st.session_state["nota"] = st.text_input("🧾 Nota Fiscal", value=st.session_state["nota"])

# Função para limpar IMEIs
def limpar_imei(raw):
    numeros = re.findall(r'\d+', raw)
    return numeros

# --- BOTÃO PDF/ZIP FIXO NO TOPO ESQUERDO (visível se houver IMEIs) ---
if st.session_state["caixas"]:
    left_col, _ = st.columns([1, 8])
    with left_col:
        if st.button("📄 Gerar PDF + ZIP com QR Codes", key="btn_pdf_topo"):
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

                qtd = len(imeis)
                ultimo = imeis[-1] if imeis else ""
                imagens_qr.append((img_path, caixa, qtd, ultimo))

            # Criar PDF
            pdf = FPDF("P", "mm", "A4")
            pdf.set_auto_page_break(auto=False)
            pdf.add_page()

            # Cabeçalho com NCE e Nota
            def add_header():
                pdf.set_font("Arial", "B", 12)
                header_text = f"NCE: {st.session_state['nce']}    Nota: {st.session_state['nota']}"
                pdf.cell(0, 10, header_text, 0, 1, "C")
                pdf.ln(5)
            add_header()

            qr_size = 55
            margin_x = 20
            margin_y = 20
            gap_x = 25
            gap_y = 40
            positions = [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2)]

            count = 0
            for img_path, caixa_nome, qtd, ultimo in imagens_qr:
                if count % 6 == 0 and count > 0:
                    pdf.add_page()
                    add_header()
                pos = positions[count % 6]
                x = margin_x + pos[0] * (qr_size + gap_x)
                y = margin_y + pos[1] * (qr_size + gap_y)

                pdf.image(img_path, x=x, y=y, w=qr_size, h=qr_size)
                pdf.set_xy(x, y + qr_size + 2)
                pdf.set_font("Arial", "B", 9)
                pdf.multi_cell(qr_size, 5, f"{caixa_nome}\nQtd: {qtd}\nÚlt: {ultimo}", align="C")

                count += 1

            # Gerar PDF em memória
            pdf_bytes = pdf.output(dest="S").encode("latin1")
            pdf_buffer = BytesIO(pdf_bytes)

            # Criar ZIP
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zipf:
                zipf.writestr("qrcodes.pdf", pdf_buffer.getvalue())
                for img_path, _, _, _ in imagens_qr:
                    with open(img_path, "rb") as f:
                        zipf.writestr(os.path.basename(img_path), f.read())
            zip_buffer.seek(0)

            st.download_button(
                "📦 Baixar ZIP com QR Codes e PDF",
                zip_buffer.getvalue(),
                file_name="qrcodes_caixas.zip",
            )

st.divider()

# Entrada de IMEIs
imei_raw = st.text_area("📲 Digite ou cole IMEIs (um por linha ou todos juntos)")
if st.button("➕ Adicionar IMEIs", key="btn_add_imeis"):
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
        st.rerun()  # <-- faz o botão de gerar PDF aparecer imediatamente

# Mostrar caixas e IMEIs
for caixa, imeis in st.session_state["caixas"].items():
    st.subheader(f"📦 {caixa} ({len(imeis)} IMEIs)")
    st.text("\n".join(imeis))

# Exportar para Excel
if st.session_state["caixas"] and st.button("📊 Exportar todas as caixas para Excel", key="btn_excel"):
    linhas = []
    for caixa, imeis in st.session_state["caixas"].items():
        for imei in imeis:
            linhas.append({
                "NCE": st.session_state["nce"],
                "Nota Fiscal": st.session_state["nota"],
                "Caixa": caixa,
                "IMEI": imei
            })
    df = pd.DataFrame(linhas)
    excel_buffer = BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="IMEIs")
    excel_buffer.seek(0)
    st.download_button("📥 Baixar Excel", excel_buffer.getvalue(), file_name="imeis_coletados.xlsx")
