# ============================================
# TH PROGRAMAÇÃO
# Sistema de Coleta de IMEI com QR Code
# Produzido por Thiallisson
# ============================================

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

st.set_page_config(
    page_title="TH PROGRAMAÇÃO | Coleta IMEI",
    layout="centered"
)

# ====== MARCA NO TOPO ======
st.markdown(
    """
    <div style="text-align:center; padding:10px;">
        <h2 style="margin-bottom:0;">TH PROGRAMAÇÃO</h2>
        <span style="font-size:14px; color:#666;">
            Produzido por Thiallisson
        </span>
        <hr>
    </div>
    """,
    unsafe_allow_html=True
)

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
    st.session_state["nce"] = st.text_input(
        "📋 NCE do Produto",
        value=st.session_state["nce"]
    )
with col_nota:
    st.session_state["nota"] = st.text_input(
        "🧾 Nota Fiscal",
        value=st.session_state["nota"]
    )

# Função para limpar IMEIs
def limpar_imei(raw):
    return re.findall(r'\d+', raw)

# ----- BOTÃO PDF + ZIP -----
if st.session_state["caixas"]:
    left_col, _ = st.columns([1, 8])
    with left_col:
        if st.button("📄 Gerar PDF + ZIP"):
            imagens_qr = []

            for caixa, imeis in st.session_state["caixas"].items():
                if not imeis:
                    continue
                dados = "\n".join(imeis)
                img = qrcode.make(dados)
                img_path = f"qrcodes/{caixa}.png"
                img.save(img_path)

                imagens_qr.append(
                    (img_path, caixa, len(imeis), imeis[-1])
                )

            # ===== CRIAR PDF =====
            pdf = FPDF("P", "mm", "A4")
            pdf.set_auto_page_break(auto=False)

            def add_header():
                pdf.set_font("Arial", "B", 12)
                pdf.cell(
                    0,
                    8,
                    f"NCE: {st.session_state['nce']}    Nota: {st.session_state['nota']}",
                    0,
                    1,
                    "C"
                )
                pdf.set_font("Arial", "I", 8)
                pdf.cell(
                    0,
                    6,
                    "TH PROGRAMAÇÃO - Produzido por Thiallisson",
                    0,
                    1,
                    "C"
                )
                pdf.ln(3)

            pdf.add_page()
            add_header()

            qr_size = 55
            margin_x = 20
            margin_y = 25
            gap_x = 25
            gap_y = 40
            positions = [(0,0),(1,0),(0,1),(1,1),(0,2),(1,2)]

            count = 0
            for img_path, caixa, qtd, ultimo in imagens_qr:
                if count % 6 == 0 and count > 0:
                    pdf.add_page()
                    add_header()

                pos = positions[count % 6]
                x = margin_x + pos[0] * (qr_size + gap_x)
                y = margin_y + pos[1] * (qr_size + gap_y)

                pdf.image(img_path, x=x, y=y, w=qr_size)
                pdf.set_xy(x, y + qr_size + 2)
                pdf.set_font("Arial", "B", 9)
                pdf.multi_cell(
                    qr_size,
                    5,
                    f"{caixa}\nQtd: {qtd}\nÚlt: {ultimo}",
                    align="C"
                )

                count += 1

            # Rodapé fixo
            pdf.set_y(-15)
            pdf.set_font("Arial", "I", 8)
            pdf.cell(
                0,
                10,
                "TH PROGRAMAÇÃO © Produzido por Thiallisson",
                0,
                0,
                "C"
            )

            pdf_bytes = pdf.output(dest="S").encode("latin1")

            # ===== ZIP =====
            zip_buffer = BytesIO()
            with ZipFile(zip_buffer, "w") as zipf:
                zipf.writestr(
                    "TH_PROGRAMACAO_QRCODES.pdf",
                    pdf_bytes
                )
                for img_path, _, _, _ in imagens_qr:
                    with open(img_path, "rb") as f:
                        zipf.writestr(
                            os.path.basename(img_path),
                            f.read()
                        )

            zip_buffer.seek(0)

            st.download_button(
                "📦 Baixar ZIP",
                zip_buffer.getvalue(),
                file_name="TH_PROGRAMACAO_QRCODES_IMEI.zip"
            )

st.divider()

# ----- ENTRADA IMEI -----
imei_raw = st.text_area(
    "📲 Digite ou cole IMEIs (um por linha ou todos juntos)"
)

if st.button("➕ Adicionar IMEIs"):
    if imei_raw:
        novos_imeis = limpar_imei(imei_raw)
        for imei in novos_imeis:
            caixa = f"Caixa_{st.session_state['contador_caixa']}"
            st.session_state["caixas"].setdefault(caixa, []).append(imei)
            if len(st.session_state["caixas"][caixa]) >= 50:
                st.session_state["contador_caixa"] += 1

        st.success(f"{len(novos_imeis)} IMEIs adicionados com sucesso!")
        st.rerun()

# ----- EXIBIR CAIXAS -----
for caixa, imeis in st.session_state["caixas"].items():
    st.subheader(f"📦 {caixa} ({len(imeis)} IMEIs)")
    st.text("\n".join(imeis))

# ----- EXCEL -----
if st.session_state["caixas"] and st.button("📊 Exportar Excel"):
    linhas = []
    for caixa, imeis in st.session_state["caixas"].items():
        for imei in imeis:
            linhas.append({
                "NCE": st.session_state["nce"],
                "Nota Fiscal": st.session_state["nota"],
                "Caixa": caixa,
                "IMEI": imei,
                "Sistema": "TH PROGRAMAÇÃO - Produzido por Thiallisson"
            })

    df = pd.DataFrame(linhas)
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False)

    buffer.seek(0)
    st.download_button(
        "📥 Baixar Excel",
        buffer.getvalue(),
        file_name="TH_PROGRAMACAO_IMEIS.xlsx"
    )
