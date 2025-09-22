const API_CONFIG = {
  // URL base da API - altere para a URL do seu backend em produção
  BASE_URL: "http://localhost:5000/api",

  // Headers padrão
  HEADERS: {
    "Content-Type": "application/json",
  },

  // Timeout para requisições (em ms)
  TIMEOUT: 30000,
}

// Configuração para produção
if (window.location.hostname !== "localhost" && window.location.hostname !== "127.0.0.1") {
  // Altere esta URL para a URL do seu backend em produção
  // Exemplos para diferentes plataformas:
  // Render: https://seu-app.onrender.com/api
  // Railway: https://seu-app.railway.app/api
  // Deta: https://seu-app.deta.dev/api
  API_CONFIG.BASE_URL = "https://telegram-bot-backend-pcpz.onrender.com"
}

// Função para obter headers com token de autenticação
function getAuthHeaders() {
  const token = localStorage.getItem("authToken")
  return {
    ...API_CONFIG.HEADERS,
    Authorization: token ? `Bearer ${token}` : "",
  }
}

// Função para verificar se está autenticado
function isAuthenticated() {
  return localStorage.getItem("authToken") !== null
}

// Função para obter dados do usuário
function getCurrentUser() {
  return localStorage.getItem("currentUser") || "Usuário"
}
