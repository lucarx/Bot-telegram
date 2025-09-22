let currentSection = "dashboard"
let groups = []
let templates = []

// Declare variables before using them

// Inicialização da aplicação
document.addEventListener("DOMContentLoaded", () => {
  if (isAuthenticated()) {
    showMainContent()
    loadDashboard()
  } else {
    showLoginModal()
  }

  // Event listeners
  setupEventListeners()
})

function setupEventListeners() {
  // Login form
  document.getElementById("loginForm").addEventListener("submit", handleLogin)
  document.getElementById("updateProfileForm").addEventListener("submit", handleUpdateProfile)

  // Send message form
  document.getElementById("sendMessageForm").addEventListener("submit", handleSendMessage)

  // Create template form
  document.getElementById("createTemplateForm").addEventListener("submit", handleCreateTemplate)

  // Add group form
  document.getElementById("addGroupForm").addEventListener("submit", handleAddGroup)
}

// Autenticação
function showLoginModal() {
  const loginModal = new bootstrap.Modal(document.getElementById("loginModal"))
  loginModal.show()
}

async function handleLogin(event) {
  event.preventDefault()

  const email = document.getElementById("email").value
  const password = document.getElementById("password").value
  const errorDiv = document.getElementById("loginError")

  try {
    showLoading(true)
    const response = await api.login(email, password)

    localStorage.setItem("authToken", response.token)
    localStorage.setItem("currentUser", response.user.name || response.user.email)
    localStorage.setItem("isAdmin", response.user.is_admin ? "1" : "0")

    bootstrap.Modal.getInstance(document.getElementById("loginModal")).hide()
    showMainContent()
    loadDashboard()
  } catch (error) {
    errorDiv.textContent = error.message
    errorDiv.classList.remove("d-none")
  } finally {
    showLoading(false)
  }
}

function logout() {
  localStorage.removeItem("authToken")
  localStorage.removeItem("currentUser")
  location.reload()
}

function showMainContent() {
  document.getElementById("mainContent").classList.remove("d-none")
  document.getElementById("currentUser").textContent = getCurrentUser()
  const isAdmin = localStorage.getItem("isAdmin") === "1"
  document.getElementById("adminMenu").classList.toggle("d-none", !isAdmin)
}

// Navegação
function showSection(sectionName) {
  // Esconder todas as seções
  document.querySelectorAll(".content-section").forEach((section) => {
    section.classList.add("d-none")
  })

  // Remover classe active de todos os links
  document.querySelectorAll(".nav-link").forEach((link) => {
    link.classList.remove("active")
  })

  // Mostrar seção selecionada
  document.getElementById(sectionName).classList.remove("d-none")

  // Adicionar classe active ao link correspondente
  // event.target.classList.add('active'); // Removed as event.target is not defined in this context

  currentSection = sectionName

  // Carregar dados da seção
  switch (sectionName) {
    case "dashboard":
      loadDashboard()
      break
    case "profile":
      loadProfile()
      break
    case "send":
      loadSendMessage()
      break
    case "templates":
      loadTemplates()
      break
    case "groups":
      loadGroups()
      break
    case "history":
      loadHistory()
      break
  }
}

// Perfil
async function loadProfile() {
  try {
    const me = await api.getMe()
    document.getElementById("meName").textContent = me.name || "-"
    document.getElementById("meEmail").textContent = me.email
    document.getElementById("meRole").textContent = me.is_admin ? "Admin" : "Cliente"
    document.getElementById("meCreated").textContent = new Date(me.created_at).toLocaleString()
    document.getElementById("profileName").value = me.name || ""
    document.getElementById("profilePassword").value = ""
  } catch (error) {
    showToast("Erro ao carregar perfil: " + error.message, "error")
  }
}

async function handleUpdateProfile(event) {
  event.preventDefault()
  try {
    const name = document.getElementById("profileName").value
    const password = document.getElementById("profilePassword").value
    await api.updateMe({ name: name || undefined, password: password || undefined })
    showToast("Perfil atualizado com sucesso!", "success")
    loadProfile()
  } catch (error) {
    showToast("Erro ao atualizar perfil: " + error.message, "error")
  }
}

// Dashboard
async function loadDashboard() {
  try {
    const stats = await api.getStats()

    document.getElementById("statsGroups").textContent = stats.active_groups
    document.getElementById("statsTemplates").textContent = stats.total_templates
    document.getElementById("statsToday").textContent = stats.messages_today
    document.getElementById("statsTotal").textContent = stats.total_messages
  } catch (error) {
    showToast("Erro ao carregar estatísticas: " + error.message, "error")
  }
}

// Envio de mensagens
async function loadSendMessage() {
  try {
    // Carregar grupos
    groups = await api.getGroups()
    renderGroupsList()

    // Carregar templates
    templates = await api.getTemplates()
    renderTemplateSelect()
  } catch (error) {
    showToast("Erro ao carregar dados: " + error.message, "error")
  }
}

function renderGroupsList() {
  const container = document.getElementById("groupsList")

  if (groups.length === 0) {
    container.innerHTML = '<p class="text-muted">Nenhum grupo cadastrado</p>'
    return
  }

  container.innerHTML = groups
    .map(
      (group) => `
        <div class="group-checkbox">
            <input type="checkbox" id="group_${group.id}" value="${group.id}">
            <label for="group_${group.id}">${group.name}</label>
            <small class="text-muted d-block">ID: ${group.chat_id}</small>
        </div>
    `,
    )
    .join("")
}

function renderTemplateSelect() {
  const select = document.getElementById("templateSelect")
  select.innerHTML = '<option value="">Selecione um template...</option>'

  templates.forEach((template) => {
    const option = document.createElement("option")
    option.value = template.id
    option.textContent = template.name
    select.appendChild(option)
  })
}

function loadTemplate() {
  const templateId = document.getElementById("templateSelect").value
  if (!templateId) return

  const template = templates.find((t) => t.id == templateId)
  if (template) {
    document.getElementById("messageText").value = template.content
  }
}

// Admin
function showCreateClientModal() {
  const modal = new bootstrap.Modal(document.getElementById("createClientModal"))
  modal.show()
}

async function createClient() {
  const name = document.getElementById("clientName").value
  const email = document.getElementById("clientEmail").value
  const password = document.getElementById("clientPassword").value
  if (!email || !password) {
    showToast("Preencha email e senha", "error")
    return
  }
  try {
    await api.registerUser({ name, email, password })
    bootstrap.Modal.getInstance(document.getElementById("createClientModal")).hide()
    document.getElementById("createClientForm").reset()
    loadAdmin()
    showToast("Cliente criado!", "success")
  } catch (error) {
    showToast("Erro ao criar cliente: " + error.message, "error")
  }
}

async function loadAdmin() {
  const isAdmin = localStorage.getItem("isAdmin") === "1"
  if (!isAdmin) return
  try {
    const users = await api.listUsers()
    renderUsersTable(users)
  } catch (error) {
    showToast("Erro ao carregar clientes: " + error.message, "error")
  }
}

function renderUsersTable(users) {
  const container = document.getElementById("usersTable")
  if (!users || users.length === 0) {
    container.innerHTML = '<p class="text-muted">Nenhum cliente</p>'
    return
  }
  container.innerHTML = `
    <div class="table-responsive">
      <table class="table">
        <thead>
          <tr>
            <th>Nome</th>
            <th>Email</th>
            <th>Tipo</th>
            <th>Criado em</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${users
            .map(
              (u) => `
              <tr>
                <td>${u.name || '-'}</td>
                <td>${u.email}</td>
                <td>${u.is_admin ? 'Admin' : 'Cliente'}</td>
                <td>${new Date(u.created_at).toLocaleString()}</td>
                <td>${u.is_admin ? '' : `<button class="btn btn-sm btn-outline-danger" onclick="deleteClient(${u.id})"><i class="bi bi-trash"></i></button>`}</td>
              </tr>
            `,
            )
            .join("")}
        </tbody>
      </table>
    </div>
  `
}

async function deleteClient(userId) {
  if (!confirm("Deletar este cliente?")) return
  try {
    await api.deleteUser(userId)
    loadAdmin()
    showToast("Cliente deletado", "success")
  } catch (error) {
    showToast("Erro ao deletar cliente: " + error.message, "error")
  }
}

async function handleSendMessage(event) {
  event.preventDefault()

  const messageText = document.getElementById("messageText").value
  const selectedGroups = Array.from(document.querySelectorAll("#groupsList input:checked")).map((checkbox) =>
    Number.parseInt(checkbox.value),
  )

  if (selectedGroups.length === 0) {
    showToast("Selecione pelo menos um grupo", "error")
    return
  }

  try {
    showLoading(true)
    const result = await api.sendMessage(messageText, selectedGroups)

    // Mostrar resultado
    const resultDiv = document.getElementById("sendResult")
    resultDiv.innerHTML = `
            <div class="alert alert-success">
                <h5>Mensagem enviada!</h5>
                <p><strong>Enviada para:</strong> ${result.sent_groups.join(", ")}</p>
                <p><strong>Total enviadas:</strong> ${result.total_sent}</p>
                ${
                  result.failed_groups.length > 0
                    ? `
                    <p><strong>Falhas:</strong> ${result.failed_groups.join(", ")}</p>
                `
                    : ""
                }
            </div>
        `
    resultDiv.classList.remove("d-none")

    // Limpar formulário
    document.getElementById("sendMessageForm").reset()
    document.querySelectorAll("#groupsList input:checked").forEach((cb) => (cb.checked = false))

    showToast("Mensagem enviada com sucesso!", "success")
  } catch (error) {
    showToast("Erro ao enviar mensagem: " + error.message, "error")
  } finally {
    showLoading(false)
  }
}

// Templates
async function loadTemplates() {
  try {
    templates = await api.getTemplates()
    renderTemplatesList()
  } catch (error) {
    showToast("Erro ao carregar templates: " + error.message, "error")
  }
}

function renderTemplatesList() {
  const container = document.getElementById("templatesList")

  if (templates.length === 0) {
    container.innerHTML = '<p class="text-muted">Nenhum template cadastrado</p>'
    return
  }

  container.innerHTML = templates
    .map(
      (template) => `
        <div class="card mb-3">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <div>
                        <h5 class="card-title">${template.name}</h5>
                        <p class="card-text text-truncate-3">${template.content}</p>
                        <small class="text-muted">Criado em: ${new Date(template.created_at).toLocaleString()}</small>
                    </div>
                    <button class="btn btn-outline-danger btn-sm" onclick="deleteTemplate(${template.id})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        </div>
    `,
    )
    .join("")
}

function showCreateTemplate() {
  const modal = new bootstrap.Modal(document.getElementById("createTemplateModal"))
  modal.show()
}

async function handleCreateTemplate(event) {
  event.preventDefault()

  const name = document.getElementById("templateName").value
  const content = document.getElementById("templateContent").value

  if (!name || !content) {
    showToast("Preencha todos os campos", "error")
    return
  }

  try {
    await api.createTemplate(name, content)

    bootstrap.Modal.getInstance(document.getElementById("createTemplateModal")).hide()
    document.getElementById("createTemplateForm").reset()

    loadTemplates()
    showToast("Template criado com sucesso!", "success")
  } catch (error) {
    showToast("Erro ao criar template: " + error.message, "error")
  }
}

async function deleteTemplate(templateId) {
  if (!confirm("Tem certeza que deseja deletar este template?")) return

  try {
    await api.deleteTemplate(templateId)
    loadTemplates()
    showToast("Template deletado com sucesso!", "success")
  } catch (error) {
    showToast("Erro ao deletar template: " + error.message, "error")
  }
}

// Grupos
async function loadGroups() {
  try {
    groups = await api.getGroups()
    renderGroupsTable()
  } catch (error) {
    showToast("Erro ao carregar grupos: " + error.message, "error")
  }
}

function renderGroupsTable() {
  const container = document.getElementById("groupsTable")

  if (groups.length === 0) {
    container.innerHTML = '<p class="text-muted">Nenhum grupo cadastrado</p>'
    return
  }

  container.innerHTML = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Nome</th>
                        <th>Chat ID</th>
                        <th>Status</th>
                        <th>Criado em</th>
                    </tr>
                </thead>
                <tbody>
                    ${groups
                      .map(
                        (group) => `
                        <tr>
                            <td>${group.name}</td>
                            <td><code>${group.chat_id}</code></td>
                            <td>
                                <span class="badge ${group.active ? "bg-success" : "bg-secondary"}">
                                    ${group.active ? "Ativo" : "Inativo"}
                                </span>
                            </td>
                            <td>${new Date(group.created_at).toLocaleString()}</td>
                        </tr>
                    `,
                      )
                      .join("")}
                </tbody>
            </table>
        </div>
    `
}

function showAddGroup() {
  const modal = new bootstrap.Modal(document.getElementById("addGroupModal"))
  modal.show()
}

async function handleAddGroup(event) {
  event.preventDefault()

  const chatId = document.getElementById("groupChatId").value
  const name = document.getElementById("groupName").value

  if (!chatId || !name) {
    showToast("Preencha todos os campos", "error")
    return
  }

  try {
    await api.addGroup(chatId, name)

    bootstrap.Modal.getInstance(document.getElementById("addGroupModal")).hide()
    document.getElementById("addGroupForm").reset()

    loadGroups()
    showToast("Grupo adicionado com sucesso!", "success")
  } catch (error) {
    showToast("Erro ao adicionar grupo: " + error.message, "error")
  }
}

// Histórico
async function loadHistory() {
  try {
    const history = await api.getHistory()
    renderHistoryTable(history)
  } catch (error) {
    showToast("Erro ao carregar histórico: " + error.message, "error")
  }
}

function renderHistoryTable(history) {
  const container = document.getElementById("historyTable")

  if (history.length === 0) {
    container.innerHTML = '<p class="text-muted">Nenhuma mensagem no histórico</p>'
    return
  }

  container.innerHTML = `
        <div class="table-responsive">
            <table class="table">
                <thead>
                    <tr>
                        <th>Mensagem</th>
                        <th>Grupos</th>
                        <th>Status</th>
                        <th>Enviado em</th>
                    </tr>
                </thead>
                <tbody>
                    ${history
                      .map(
                        (item) => `
                        <tr>
                            <td>
                                <div class="text-truncate-3" style="max-width: 300px;">
                                    ${item.message_text}
                                </div>
                            </td>
                            <td>${item.groups_sent}</td>
                            <td>
                                <span class="badge ${item.status === "sent" ? "bg-success" : "bg-danger"}">
                                    ${item.status === "sent" ? "Enviada" : "Falha"}
                                </span>
                            </td>
                            <td>${new Date(item.sent_at).toLocaleString()}</td>
                        </tr>
                    `,
                      )
                      .join("")}
                </tbody>
            </table>
        </div>
    `
}

// Utilitários
function showLoading(show) {
  const spinner = document.getElementById("loadingSpinner")
  if (show) {
    spinner.classList.remove("d-none")
  } else {
    spinner.classList.add("d-none")
  }
}

function showToast(message, type = "info") {
  const toast = document.getElementById("toast")
  const toastBody = document.getElementById("toastBody")

  toastBody.textContent = message

  // Remover classes de tipo anteriores
  toast.classList.remove("text-bg-success", "text-bg-danger", "text-bg-info")

  // Adicionar classe baseada no tipo
  switch (type) {
    case "success":
      toast.classList.add("text-bg-success")
      break
    case "error":
      toast.classList.add("text-bg-danger")
      break
    default:
      toast.classList.add("text-bg-info")
  }

  const bsToast = new bootstrap.Toast(toast)
  bsToast.show()
}
