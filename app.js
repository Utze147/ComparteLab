
// 1. Configuración base
const API_BASE_URL = "http://localhost:8000/api/v1/solicitudes";

// 2. Referencias del DOM
const elements = {
  form: document.getElementById("solicitud-form"),
  btnSubmit: document.getElementById("btn-submit"),
  btnSpinner: document.getElementById("btn-spinner"),
  btnText: document.getElementById("btn-text"),
  btnReload: document.getElementById("btn-reload"),
  reloadIcon: document.getElementById("reload-icon"),
  tbody: document.getElementById("solicitudes-tbody"),
  tableLoading: document.getElementById("table-loading"),
  tableEmpty: document.getElementById("table-empty"),
  alertContainer: document.getElementById("alert-container")
};

/**
 * Muestra alertas dinámicas con Bootstrap 5
 * @param {string} message - Mensaje a mostrar
 * @param {'success' | 'danger' | 'warning' | 'info'} type - Estilo de la alerta
 * @param {boolean} autoDismiss - Si debe cerrarse automáticamente después de un tiempo
 */
function showAlert(message, type = "danger", autoDismiss = true) {
  const iconMap = {
    success: "bi-check-circle-fill",
    danger: "bi-exclamation-triangle-fill",
    warning: "bi-exclamation-circle-fill",
    info: "bi-info-circle-fill"
  };

  const iconClass = iconMap[type] || "bi-info-circle-fill";

  const alertWrapper = document.createElement("div");
  alertWrapper.className = `alert alert-${type} alert-dismissible fade show d-flex align-items-center shadow-sm`;
  alertWrapper.setAttribute("role", "alert");

  alertWrapper.innerHTML = `
    <i class="bi ${iconClass} flex-shrink-0 me-2 fs-5"></i>
    <div class="flex-grow-1">${escapeHtml(message)}</div>
    <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Cerrar"></button>
  `;

  // Limpiamos alertas previas o anexamos la nueva
  elements.alertContainer.replaceChildren(alertWrapper);

  if (autoDismiss) {
    setTimeout(() => {
      const bsAlert = window.bootstrap ? (bootstrap.Alert.getInstance(alertWrapper) || new bootstrap.Alert(alertWrapper)) : null;
      if (bsAlert && alertWrapper.parentNode) {
        bsAlert.close();
      } else if (alertWrapper.parentNode) {
        alertWrapper.remove();
      }
    }, 6000);
  }
}

/**
 * Escapa strings para prevenir Cross-Site Scripting (XSS)
 * @param {string} str 
 * @returns {string}
 */
function escapeHtml(str) {
  if (str === null || str === undefined) return "";
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#039;'
  };
  return String(str).replace(/[&<>"']/g, (m) => map[m]);
}

/**
 * Alterna el estado visual de carga del botón de envío
 * @param {boolean} isLoading 
 */
function setFormLoading(isLoading) {
  if (isLoading) {
    elements.btnSubmit.disabled = true;
    elements.btnSpinner.classList.remove("d-none");
    elements.btnText.textContent = " Registrando...";
  } else {
    elements.btnSubmit.disabled = false;
    elements.btnSpinner.classList.add("d-none");
    elements.btnText.innerHTML = `<i class="bi bi-send-fill me-1"></i> Registrar Solicitud`;
  }
}

/**
 * Mapea el estado a un badge estilizado de Bootstrap
 * @param {string} estado 
 * @returns {string} HTML del badge
 */
function renderStatusBadge(estado) {
  const normalized = (estado || "pendiente").toLowerCase().trim();
  let badgeClass = "bg-secondary";
  let label = estado || "Pendiente";

  if (normalized === "aprobada" || normalized === "aprobado" || normalized === "activo") {
    badgeClass = "bg-success";
  } else if (normalized === "pendiente" || normalized === "en espera") {
    badgeClass = "bg-warning text-dark";
  } else if (normalized === "rechazada" || normalized === "rechazado" || normalized === "cancelado") {
    badgeClass = "bg-danger";
  } else if (normalized === "devuelto" || normalized === "completado" || normalized === "finalizado") {
    badgeClass = "bg-info text-dark";
  }

  return `<span class="badge ${badgeClass} text-uppercase px-2 py-1">${escapeHtml(label)}</span>`;
}

/**
 * Petición GET: Consulta y renderiza las solicitudes
 */
async function fetchSolicitudes() {
  elements.tbody.innerHTML = "";
  elements.tableEmpty.classList.add("d-none");
  elements.tableLoading.classList.remove("d-none");

  try {
    const response = await fetch(API_BASE_URL, {
      method: "GET",
      headers: {
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      let errorMsg = `Error al consultar solicitudes (HTTP ${response.status})`;
      try {
        const errJson = await response.json();
        errorMsg = errJson.detail || errJson.message || errorMsg;
      } catch (_) {}
      throw new Error(errorMsg);
    }

    const data = await response.json();
    const solicitudes = Array.isArray(data) ? data : (data.items || data.data || []);
    renderTable(solicitudes);
  } catch (error) {
    console.error("Error al obtener solicitudes:", error);
    const mensaje = (error instanceof TypeError)
      ? "No se pudo conectar con el servidor. Verifica que la API esté encendida en http://localhost:8000."
      : error.message;
    showAlert(mensaje, "danger", false);
    elements.tableEmpty.classList.remove("d-none");
  } finally {
    elements.tableLoading.classList.add("d-none");
  }
}

/**
 * Renderiza la lista de solicitudes en la tabla
 * @param {Array} solicitudes 
 */
function renderTable(solicitudes) {
  elements.tbody.innerHTML = "";

  if (!solicitudes || solicitudes.length === 0) {
    elements.tableEmpty.classList.remove("d-none");
    return;
  }

  elements.tableEmpty.classList.add("d-none");
  const fragment = document.createDocumentFragment();

  solicitudes.forEach((solicitud) => {
    const tr = document.createElement("tr");
    const id = solicitud.id ?? "-";
    const matricula = solicitud.matricula ?? "N/A";
    const alumno = solicitud.nombre_alumno ?? solicitud.alumno ?? "Sin nombre";
    const equipoId = solicitud.equipo_id ?? "-";
    const estadoBadge = renderStatusBadge(solicitud.estado);

    tr.innerHTML = `
      <td class="ps-3 text-center fw-semibold text-secondary">#${escapeHtml(id)}</td>
      <td><span class="font-monospace text-primary fw-medium">${escapeHtml(matricula)}</span></td>
      <td>${escapeHtml(alumno)}</td>
      <td class="text-center"><span class="badge bg-light text-dark border">#${escapeHtml(equipoId)}</span></td>
      <td class="text-center pe-3">${estadoBadge}</td>
    `;
    fragment.appendChild(tr);
  });

  elements.tbody.appendChild(fragment);
}

/**
 * Manejador del evento submit del formulario
 * @param {SubmitEvent} event 
 */
async function handleFormSubmit(event) {
  event.preventDefault();
  event.stopPropagation();
  const form = elements.form;

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    showAlert("Por favor, corrige los errores en el formulario antes de continuar.", "warning");
    return;
  }

  form.classList.remove("was-validated");
  const formData = new FormData(form);
  const payload = {
    matricula: formData.get("matricula").trim(),
    nombre_alumno: formData.get("nombre_alumno").trim(),
    equipo_id: parseInt(formData.get("equipo_id"), 10),
    motivo: formData.get("motivo").trim()
  };

  setFormLoading(true);

  try {
    const response = await fetch(API_BASE_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify(payload)
    });

    if (response.status === 201) {
      form.reset();
      showAlert("¡Solicitud de préstamo registrada exitosamente!", "success");
      await fetchSolicitudes();
    } else {
      let errorMessage = `Ocurrió un error al registrar la solicitud (HTTP ${response.status}).`;
      try {
        const errorData = await response.json();
        if (typeof errorData.detail === "string") {
          errorMessage = errorData.detail;
        } else if (Array.isArray(errorData.detail)) {
          errorMessage = errorData.detail.map(err => `${err.loc ? err.loc.slice(-1)[0] : 'campo'}: ${err.msg}`).join(" | ");
        } else if (errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (_) {}
      showAlert(errorMessage, "danger");
    }
  } catch (error) {
    console.error("Error en la petición POST:", error);
    showAlert(
      "Error de conexión: No se pudo contactar con la API. Asegúrate de que el servidor esté activo en http://localhost:8000.",
      "danger",
      false
    );
  } finally {
    setFormLoading(false);
  }
}

// 3. Inicialización al cargar el documento
document.addEventListener("DOMContentLoaded", () => {
  fetchSolicitudes();
  if (elements.form) {
    elements.form.addEventListener("submit", handleFormSubmit);
  }
  if (elements.btnReload) {
    elements.btnReload.addEventListener("click", () => {
      fetchSolicitudes();
    });
  }
});