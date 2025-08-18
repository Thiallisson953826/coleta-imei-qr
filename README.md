# 📱 Coleta de IMEIs e Geração de QR Codes

Sistema simples em **Python + Streamlit** para coletar IMEIs de caixas, organizar por código master e gerar QR Codes.

---

## 🚀 Como rodar localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/SEU_USUARIO/coleta-imei-qr.git
   cd coleta-imei-qr
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Rode a aplicação:
   ```bash
   streamlit run app.py
   ```

4. Abra no navegador:
   ```
   http://localhost:8501
   ```

---

## 🌍 Rodando online no Streamlit Cloud

1. Crie uma conta gratuita no [Streamlit Cloud](https://streamlit.io/cloud).  
2. Conecte com o GitHub.  
3. Clique em **New app** → selecione este repositório.  
4. Em **Main file path**, informe:
   ```
   app.py
   ```
5. Clique em **Deploy**.  

O sistema ficará disponível em um link do tipo:
```
https://seu-usuario-coleta-imei-qr.streamlit.app
```

---

## 📦 Funcionalidades
- Criar caixas via código master
- Adicionar IMEIs em cada caixa
- Gerar QR Code com os IMEIs da caixa
- Exportar todos os IMEIs em Excel
