import streamlit as st
import qrcode
import pandas as pd
from io import BytesIO
import os
import zipfile

# Garante pasta de QR Codes
os.makedirs("qrcodes", exist_ok=True)

st.set_page_config(page_title="📱 Coleta IMEI - QR Codes Múltiplos", layout="centered")
st.title("📦 Coleta de IMEIs - QR Codes Automáticos")

# Sessão para armazenar caixas e IMEIs temporariamente
if "caixas" not in st.session_state:
    st.session_state["caixas"] = {}
if "caixa_atual" not in st.session_state:
    st.session_state["caixa_atual"] = None

# Bipar Código Master para criar nova caixa
codigo_master = st.text_input("📌 Bipar Código Master da Caixa")
if codigo_master and st.button("📦 Criar/Selecionar Caixa"):
    st.session_state["caixa_atual"] = codigo_master
    if codigo_master not in st.session_state["caixas"]:
        st.session_state["caixas"][codigo_master] = []
        st.success(f"✅ Nova caixa criada: {codigo_master}")
    else:
        st.info(f"📌 Caixa selecionada: {codigo_master}")

# Adicionar IMEIs
if st.session_state["caixa_atual"]:
    st.subheader(f"📋 Caixa ativa: {st.session_state['caixa_atual']}")
    imei = st.text_input("📲 Digite ou bipar IMEI")
    if st.button("➕ Adicionar IMEI"):
        if imei and imei not in st.session_state["caixas"][st.session_state["caixa_atual"]]:
            st.session_state["caixas"][st.session_state["caixa_atual"]].append(imei)
            st.success(f"📲 IMEI {imei} adicionado")
        else:
            st.warning("⚠️ IMEI inválido ou já adicionado!")

    # Mostrar lista de IMEIs da caixa atual
    st.write(st.session_state["caixas"][st.session_state["caixa_atual"]])

    # Finalizar Caixa: gera QR Code automaticamente
    if st.button("✅ Finalizar Caixa (Gerar QR Code)"):
        dados = "\n".join(st.session_state["caixas"][st.session_state["caixa_atual"]])
        if dados:
            # Gerar QR Code
            img = qrcode.make(dados)
            file_path = os.path.join("qrcodes", f"{st.session_state['caixa_atual']}.png")
            img.save(file_path)
            st.success(f"🎯 QR Code gerado e salvo em 'qrcodes/{st.session_state['caixa_atual']}.png'")
            st.session_state["caixa_atual"] = None
        else:
            st.warning("⚠️ Nenhum IMEI para gerar QR Code!")

# Mostrar todas as caixas já finalizadas
if st.session_state["caixas"]:
    st.subheader("📦 Caixas finalizadas / QR Codes gerados")
    finalized = [c for c in st.session_state["caixas"] if os.path.exists(os.path.join("qrcodes", f"{c}.png"))]
    st.write(finalized)

    # Botão para baixar todos os QR Codes em ZIP
    if st.button("📥 Baixar todos os QR Codes em ZIP"):
        zip_buffer = BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zipf:
            for caixa in finalized:
                file_path = os.path.join("qrcodes", f"{caixa}.png")
                zipf.write(file_path, arcname=f"{caixa}.png")
        st.download_button("📥 Baixar ZIP", zip_buffer.getvalue(), file_name="qrcodes_todas_caixas.zip")

