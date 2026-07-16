import React, { useState } from 'react';

// 1. Declarando a URL padrão para nunca mais dar erro de variável indefinida
const API_URL = "http://localhost:8000";

export default function App() {
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    // Adiciona a pergunta do usuário na tela
    const userMsg = { sender: 'user', text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // 2. Adicionado 'const res = await' para definir a variável da resposta do servidor
      const res = await fetch(`${API_URL}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ mensagem: input })
      });
      
      if (!res.ok) throw new Error('Falha de conexão');
      
      const data = await res.json();
      
      // Adiciona a resposta da LLM e a query SQL usada para transparência
      setMessages(prev => [
        ...prev, 
        { sender: 'bot', text: data.resposta, sql: data.query_executada }
      ]);
    } catch (error) {
      setMessages(prev => [
        ...prev, 
        { sender: 'bot', text: 'Desculpe, ocorreu um erro de conexão com o servidor do chatbot.' }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Assistente de Vendas Inteligente 💬</h1>
        <p style={styles.subtitle}>Consulte produtos, preços e estoque em tempo real usando IA</p>
      </header>
      
      <div style={styles.chatArea}>
        {messages.length === 0 ? (
          <div style={styles.placeholder}>
            Pergunte algo como: <br />
            <em>"Quais produtos temos no estoque?"</em> ou <br />
            <em>"Qual é o preço do Smartphone X?"</em>
          </div>
        ) : (
          messages.map((msg, i) => (
            <div key={i} style={{ ...styles.messageRow, justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{ 
                ...styles.bubble, 
                backgroundColor: msg.sender === 'user' ? '#1e3a8a' : '#e2e8f0', 
                color: msg.sender === 'user' ? '#fff' : '#1f2937' 
              }}>
                <div>{msg.text}</div>
                {msg.sql && (
                  <div style={styles.sqlCode}>
                    <strong>Query executada no SQLite:</strong>
                    <code>{msg.sql}</code>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {loading && <div style={styles.loading}>Consultando banco de dados...</div>}
      </div>

      <div style={styles.inputArea}>
        <input 
          type="text" 
          value={input} 
          onChange={e => setInput(e.target.value)} 
          onKeyDown={e => e.key === 'Enter' && handleSend()}
          style={styles.input} 
          placeholder="Digite sua pergunta sobre a loja..." 
          disabled={loading}
        />
        <button onClick={handleSend} style={styles.button} disabled={loading}>
          {loading ? '...' : 'Enviar'}
        </button>
      </div>
    </div>
  );
}

const styles = {
  container: {
    maxWidth: '650px',
    margin: '40px auto',
    fontFamily: 'system-ui, sans-serif',
    border: '1px solid #cbd5e1',
    borderRadius: '12px',
    boxShadow: '0 10px 15px -3px rgba(0,0,0,0.1)',
    display: 'flex',
    flexDirection: 'column',
    height: '600px',
    backgroundColor: '#fff'
  },
  header: {
    backgroundColor: '#1e3a8a',
    color: '#fff',
    padding: '20px',
    borderRadius: '11px 11px 0 0'
  },
  title: { margin: 0, fontSize: '18px', fontWeight: 'bold' },
  subtitle: { margin: '5px 0 0 0', fontSize: '12px', opacity: 0.8 },
  chatArea: {
    flexGrow: 1,
    padding: '20px',
    overflowY: 'auto',
    backgroundColor: '#f8fafc',
    display: 'flex',
    flexDirection: 'column',
    gap: '15px'
  },
  placeholder: {
    margin: 'auto',
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '14px',
    lineHeight: 1.6
  },
  messageRow: { display: 'flex', width: '100%' },
  bubble: {
    maxWidth: '80%',
    padding: '12px 16px',
    borderRadius: '12px',
    fontSize: '14px',
    lineHeight: 1.5,
  },
  sqlCode: {
    marginTop: '8px',
    paddingTop: '8px',
    borderTop: '1px dashed #94a3b8',
    fontSize: '11px',
    color: '#475569',
    fontFamily: 'monospace',
    display: 'block'
  },
  loading: {
    textAlign: 'center',
    color: '#94a3b8',
    fontSize: '12px',
    margin: '10px 0'
  },
  inputArea: {
    display: 'flex',
    padding: '15px',
    borderTop: '1px solid #e2e8f0',
    gap: '10px'
  },
  input: {
    flexGrow: 1,
    padding: '12px',
    borderRadius: '8px',
    border: '1px solid #cbd5e1',
    outline: 'none',
    fontSize: '14px'
  },
  button: {
    padding: '0 20px',
    backgroundColor: '#2563eb',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    fontWeight: 'bold',
    cursor: 'pointer',
    fontSize: '14px'
  }
};