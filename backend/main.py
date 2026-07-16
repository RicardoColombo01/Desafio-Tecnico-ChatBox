import os
import sqlite3
import re
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Descobre o caminho exato da pasta onde este arquivo main.py está salvo
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "loja.db")

# Tenta importar a Cohere. Se não estiver instalada, o código não vai quebrar!
try:
    import cohere
    COHERE_INSTALADO = True
except ImportError:
    COHERE_INSTALADO = False

app = FastAPI(title="Chatbot de Loja - Inteligente e Seguro")

# CORS com permissão total aberta para evitar qualquer bloqueio na Vercel
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Permite requisições de qualquer origem externa
    allow_credentials=False,         # Obrigatório ser False quando usamos "*" no allow_origins
    allow_methods=["*"],             # Permite todos os métodos (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],             # Permite todos os cabeçalhos
)

# Se você tiver uma chave da Cohere, cole aqui. Se não tiver ou der erro, o sistema local assume!
COHERE_API_KEY = "CORSMiddleware"

# Inicializa o cliente se a biblioteca estiver disponível e a chave não for a padrão
co = None
if COHERE_INSTALADO and COHERE_API_KEY and COHERE_API_KEY != "SUA_CHAVE_COHERE_AQUI":
    try:
        co = cohere.Client(api_key=COHERE_API_KEY)
    except Exception:
        co = None

class ChatRequest(BaseModel):
    mensagem: str

def executar_consulta_sql(query: str):
    """Executa consultas de forma segura no SQLite usando o caminho dinâmico."""
    try:
        # Usa o caminho absoluto dinâmico para nunca errar a pasta do banco
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query)
        
        colunas = [desc[0] for desc in cursor.description] if cursor.description else []
        resultados = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        conn.close()
        return resultados
    except Exception as e:
        return f"Erro ao executar SQL: {str(e)}"

def resolver_pergunta_localmente(pergunta: str):
    """Fallback inteligente local: gera SQL e respostas sem usar nenhuma API externa."""
    pergunta_clean = pergunta.lower().strip()
    
    # Caso a mensagem seja vazia de alguma forma (garantia extra)
    if not pergunta_clean:
        sql = "NENHUMA"
        resposta = (
            "Olá! Como posso te ajudar hoje? \n\n"
            "Você pode me perguntar sobre:\n"
            "• Os produtos em estoque (ex: 'Quais produtos temos no estoque?')\n"
            "• O preço de um item (ex: 'Qual é o preço do Smartphone X?')"
        )
        return sql, resposta

    # 1. Identificar a intenção e gerar a Query SQL localmente
    if "estoque" in pergunta_clean or "produtos" in pergunta_clean or "temos" in pergunta_clean:
        sql = "SELECT nome, preco, estoque FROM produtos"
    elif "preco" in pergunta_clean or "preço" in pergunta_clean or "quanto custa" in pergunta_clean:
        # Tenta extrair o nome de um produto (ex: Smartphone, Camisa, etc.)
        match = re.search(r'(smartphone x|smartphone|camisa|calça|eletrônicos|vestuário)', pergunta_clean)
        produto = match.group(1) if match else ""
        if produto:
            sql = f"SELECT nome, preco, estoque FROM produtos WHERE nome LIKE '%{produto}%'"
        else:
            sql = "SELECT nome, preco FROM produtos"
    elif "categoria" in pergunta_clean:
        sql = "SELECT * FROM categorias"
    else:
        # RESPOSTA AUTOMÁTICA DE AJUDA (Caso nenhuma palavra-chave acima seja identificada)
        sql = "NENHUMA"
        resposta = (
            "Não entendi muito bem sua pergunta. \n\n"
            "Sou o assistente virtual da loja e posso te ajudar com as seguintes opções:\n"
            "• Estoque: Pergunte 'Quais produtos temos?'\n"
            "• Preços: Pergunte 'Qual o preço do Smartphone X?'\n\n"
            "Como posso te ajudar agora?"
        )
        return sql, resposta

    # 2. Executar no banco (só roda se passou pelos filtros com SQL válido)
    dados = executar_consulta_sql(sql)
    
    # 3. Formatar uma resposta amigável em português
    if isinstance(dados, str) and dados.startswith("Erro"):
        resposta = f"Desculpe, tive um problema ao acessar o banco de dados local."
    elif not dados:
        resposta = "Não encontrei essas informações no momento em nosso estoque de produtos."
    else:
        resposta = "Aqui estão as informações que encontrei no nosso sistema:\n\n"
        for item in dados:
            nome = item.get("nome", "Produto")
            preco = item.get("preco", "")
            estoque = item.get("estoque", "")
            
            detalhes = []
            if preco: detalhes.append(f"R$ {preco:.2f}")
            if estoque is not None: detalhes.append(f"{estoque} unidades em estoque")
            
            resposta += f"• {nome}: {', '.join(detalhes)}\n"
            
        resposta += "\nPrecisa de ajuda com mais alguma coisa?"

    return sql, resposta


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    if not request.mensagem.strip():
        raise HTTPException(status_code=400, detail="A mensagem não pode ser vazia.")

    # Se a API da Cohere estiver configurada corretamente, tenta usar a IA
    if co:
        try:
            # ETAPA 1: Text-to-SQL
            prompt_sql = f"""
            Escreva APENAS a query SQL SQLite correspondente para a pergunta: "{request.mensagem}"
            Esquema:
            - categorias (id, nome)
            - produtos (id, nome, preco, estoque, categoria_id)
            Regras: Retorne apenas o SQL limpo, sem markdown, sem explicações.
            """
            response_sql = co.chat(message=prompt_sql, model="command-r")
            clean_sql = response_sql.text.replace("```sql", "").replace("```", "").strip()

            # ETAPA 2: Banco de Dados
            dados_retornados = executar_consulta_sql(clean_sql)

            if isinstance(dados_retornados, str) and dados_retornados.startswith("Erro"):
                # Se a IA errou no SQL, usamos o resolvedor local de segurança
                sql_local, resp_local = resolver_pergunta_localmente(request.mensagem)
                return {"query_executada": sql_local, "resposta": resp_local}

            # ETAPA 3: SQL-to-Text
            prompt_resposta = f"""
            Você é o assistente virtual da loja. Responda amigavelmente em português do Brasil para a pergunta: "{request.mensagem}"
            Dados do banco: {dados_retornados}
            """
            response_humanizada = co.chat(message=prompt_resposta, model="command-r")
            
            return {
                "query_executada": clean_sql,
                "resposta": response_humanizada.text.strip()
            }
            
        except Exception:
            # Se a requisição falhar por limite, internet ou chave, o sistema local assume sem dar Erro 500!
            sql_local, resp_local = resolver_pergunta_localmente(request.mensagem)
            return {"query_executada": sql_local, "resposta": resp_local}
            
    else:
        # Se nenhuma IA estiver configurada, o motor local responde instantaneamente
        sql_local, resp_local = resolver_pergunta_localmente(request.mensagem)
        return {
            "query_executada": sql_local,
            "resposta": resp_local
        }
