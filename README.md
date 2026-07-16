# 💬 Assistente de Vendas Inteligente - Chatbot SQL

Este é um projeto de Chatbot inteligente capaz de traduzir perguntas em linguagem natural para consultas SQL em um banco de dados de produtos, retornando respostas dinâmicas e amigáveis para o usuário.

---

## 🛠️ Tecnologias Utilizadas

* **Frontend:** React (JavaScript, CSS reativo, integração com API via Fetch/CORS)
* **Backend:** Python (FastAPI, Uvicorn, SQLite para banco de dados local)
* **Inteligência Artificial:** Integração flexível com LLM (Cohere / Gemini) e motor híbrido de fallback local de segurança.

---

## 📂 Estrutura do Banco de Dados Relacional (SQLite)

O banco de dados `loja.db` conta com as tabelas:
* **`categorias`**: `id` (PK), `nome` (TEXT)
* **`produtos`**: `id` (PK), `nome` (TEXT), `preco` (REAL), `estoque` (INTEGER), `categoria_id` (FK)

---

### Link:(https://desafio-tecnico-chat-bot.vercel.app)

---

## 🚀 Como Executar o Projeto

### 1. Backend (Python)
1. Navegue até a pasta do backend:
   ```Bash
   cd backend

   Ative o seu ambiente virtual:

 ```Bash
.\venv\Scripts\activate
Instale as dependências:

 ```Bash
pip install fastapi uvicorn cohere google-genai
Inicie o servidor:

Bash
python -m uvicorn main:app --reload
2. Frontend (React)
Navegue até a pasta do frontend:

Bash
cd frontend
Instale as dependências e inicie:

Bash
npm install
npm start
