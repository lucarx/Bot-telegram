// Usar a configuração do config.js

class ApiClient {
  constructor() {
    this.baseUrl = API_CONFIG.BASE_URL
    this.timeout = API_CONFIG.TIMEOUT
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseUrl}${endpoint}`
    const config = {
      timeout: this.timeout,
      headers: getAuthHeaders(),
      ...options,
    }

    try {
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), this.timeout)

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      })

      clearTimeout(timeoutId)

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.error || `HTTP ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      if (error.name === "AbortError") {
        throw new Error("Timeout: A requisição demorou muito para responder")
      }
      throw error
    }
  }

  // Autenticação
  async login(email, password) {
    return this.request("/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    })
  }

  // Perfil
  async getMe() {
    return this.request("/me")
  }

  async updateMe({ name, password }) {
    return this.request("/me", {
      method: "PUT",
      body: JSON.stringify({ name, password }),
    })
  }

  // Admin
  async listUsers() {
    return this.request("/users")
  }

  async registerUser({ name, email, password }) {
    return this.request("/register", {
      method: "POST",
      body: JSON.stringify({ name, email, password }),
    })
  }

  async deleteUser(userId) {
    return this.request(`/users/${userId}`, { method: "DELETE" })
  }

  // Estatísticas
  async getStats() {
    return this.request("/stats")
  }

  // Grupos
  async getGroups() {
    return this.request("/groups")
  }

  async addGroup(chatId, name) {
    return this.request("/groups", {
      method: "POST",
      body: JSON.stringify({ chat_id: chatId, name }),
    })
  }

  // Templates
  async getTemplates() {
    return this.request("/templates")
  }

  async createTemplate(name, content) {
    return this.request("/templates", {
      method: "POST",
      body: JSON.stringify({ name, content }),
    })
  }

  async deleteTemplate(templateId) {
    return this.request(`/templates/${templateId}`, {
      method: "DELETE",
    })
  }

  // Mensagens
  async sendMessage(message, groups) {
    return this.request("/send_message", {
      method: "POST",
      body: JSON.stringify({ message, groups }),
    })
  }

  // Histórico
  async getHistory() {
    return this.request("/history")
  }
}

// Instância global da API
const api = new ApiClient()