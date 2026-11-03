// ==============================================================================
// 1. CONFIGURACIÓN BASE
// ==============================================================================
const API_BASE_URL = "http://127.0.0.1:8000/api/v1/solicitudes";

// Referencias a elementos del DOM
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

// ==============================================================================
// 2. UTILIDADES DE INTERFAZ (Alertas y badges)
// ==============================================================================
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

  elements.alertContainer.replaceChildren(alertWrapper);

  if (autoDismiss) {
    setTimeout(() => {
      const bsAlert = window.bootstrap ? (bootstrap.Alert.getInstance(alertWrapper) || new bootstrap.Alert(alertWrapper)) : null;
      if (bsAlert && alertWrapper.parentNode) {
        bsAlert.close();
      } else if (alertWrapper.parentNode) {
        alertWrapper.remove();
      }
    }, 5000);
  }
}

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

function renderStatusBadge(estado) {
  const normalized = (estado || "PENDIENTE").toUpperCase().trim();
  let badgeClass = "bg-secondary";

  if (normalized === "APROBADA") {
    badgeClass = "bg-success";
  } else if (normalized === "PENDIENTE") {
    badgeClass = "bg-warning text-dark";
  } else if (normalized === "RECHAZADA") {
    badgeClass = "bg-danger";
  } else if (normalized === "DEVUELTO") {
    badgeClass = "bg-info text-dark";
  }

  return `<span class="badge ${badgeClass} text-uppercase px-2 py-1">${escapeHtml(normalized)}</span>`;
}

// ==============================================================================
// 3. CONSULTAR SOLICITUDES (GET)
// ==============================================================================
async function fetchSolicitudes() {
  elements.tbody.innerHTML = "";
  elements.tableEmpty.classList.add("d-none");
  elements.tableLoading.classList.remove("d-none");

  try {
    const response = await fetch(API_BASE_URL, {
      method: "GET",
      headers: { "Accept": "application/json" }
    });

    if (!response.ok) {
      throw new Error(`Error al consultar solicitudes (HTTP ${response.status})`);
    }

    const solicitudes = await response.json();
    renderTable(solicitudes);

  } catch (error) {
    console.error("Error al obtener solicitudes:", error);
    const mensaje = (error instanceof TypeError)
      ? "No se pudo conectar con el servidor. Verifica que el backend esté activo en http://127.0.0.1:8000."
      : error.message;
    showAlert(mensaje, "danger", false);
    elements.tableEmpty.classList.remove("d-none");
  } finally {
    elements.tableLoading.classList.add("d-none");
  }
}

// ==============================================================================
// 4. RENDERIZAR TABLA Y ACCIONES DE ESTADO (Aprobar, Rechazar, Devolver)
// ==============================================================================
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
    const estado = (solicitud.estado || "PENDIENTE").toUpperCase();

    // Botones de acción según el estado actual
    let botonesAccion = "";
    if (estado === "PENDIENTE") {
      botonesAccion = `
        <div class="btn-group btn-group-sm" role="group">
          <button class="btn btn-outline-success" onclick="cambiarEstado(${solicitud.id}, 'APROBADA')" title="Aprobar préstamo">
            <i class="bi bi-check-lg"></i>
          </button>
          <button class="btn btn-outline-danger" onclick="cambiarEstado(${solicitud.id}, 'RECHAZADA')" title="Rechazar préstamo">
            <i class="bi bi-x-lg"></i>
          </button>
        </div>
      `;
    } else if (estado === "APROBADA") {
      botonesAccion = `
        <button class="btn btn-sm btn-outline-primary" onclick="cambiarEstado(${solicitud.id}, 'DEVUELTO')" title="Marcar como entregado/devuelto">
          <i class="bi bi-box-arrow-in-down me-1"></i>Devolver
        </button>
      `;
    } else {
      botonesAccion = `<span class="text-muted small"><i class="bi bi-lock-fill"></i> Concluido</span>`;
    }

    tr.innerHTML = `
      <td class="ps-3 text-center fw-semibold text-secondary">#${escapeHtml(solicitud.id)}</td>
      <td><span class="font-monospace text-primary fw-medium">${escapeHtml(solicitud.matricula)}</span></td>
      <td>${escapeHtml(solicitud.nombre_alumno)}</td>
      <td class="text-center"><span class="badge bg-light text-dark border">#${escapeHtml(solicitud.equipo_id)}</span></td>
      <td><small class="text-muted text-truncate d-inline-block" style="max-width: 180px;" title="${escapeHtml(solicitud.motivo)}">${escapeHtml(solicitud.motivo)}</small></td>
      <td class="text-center">${renderStatusBadge(solicitud.estado)}</td>
      <td class="text-center pe-3">${botonesAccion}</td>
    `;
    fragment.appendChild(tr);
  });

  elements.tbody.appendChild(fragment);
}

// ==============================================================================
// 5. CAMBIAR ESTADO DE UNA SOLICITUD (PATCH)
// ==============================================================================
async function cambiarEstado(id, nuevoEstado) {
  try {
    const response = await fetch(`${API_BASE_URL}/${id}/estado`, {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json"
      },
      body: JSON.stringify({ estado: nuevoEstado })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.detail || "Error al actualizar estado");
    }

    showAlert(`Solicitud #${id} actualizada a ${nuevoEstado}.`, "success");
    await fetchSolicitudes();

  } catch (error) {
    console.error("Error al actualizar:", error);
    showAlert(error.message, "danger");
  }
}

// ==============================================================================
// 6. REGISTRAR NUEVA SOLICITUD (POST)
// ==============================================================================
async function handleFormSubmit(event) {
  event.preventDefault();
  event.stopPropagation();
  const form = elements.form;

  if (!form.checkValidity()) {
    form.classList.add("was-validated");
    showAlert("Por favor, corrige los campos del formulario.", "warning");
    return;
  }

  form.classList.remove("was-validated");

  const payload = {
    matricula: document.getElementById("matricula").value.trim(),
    nombre_alumno: document.getElementById("nombre_alumno").value.trim(),
    equipo_id: parseInt(document.getElementById("equipo_id").value, 10),
    motivo: document.getElementById("motivo").value.trim()
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

    const resultado = await response.json();

    if (response.status === 201) {
      form.reset();
      showAlert(`¡Solicitud #${resultado.id} registrada correctamente para el equipo #${resultado.equipo_id}!`, "success");
      await fetchSolicitudes();
    } else if (response.status === 409) {
      showAlert(resultado.detail || "El equipo ya se encuentra ocupado.", "warning", false);
    } else if (response.status === 422) {
      let detalle = resultado.detail;
      if (Array.isArray(detalle)) {
        detalle = detalle.map(e => `${e.loc?.slice(-1)[0] || 'campo'}: ${e.msg}`).join(", ");
      }
      showAlert(`Error de validación: ${detalle}`, "danger", false);
    } else {
      showAlert(resultado.detail || `Error del servidor (HTTP ${response.status})`, "danger");
    }

  } catch (error) {
    console.error("Error en POST:", error);
    showAlert("No se pudo conectar con el servidor backend.", "danger", false);
  } finally {
    setFormLoading(false);
  }
}

// ==============================================================================
// 7. INICIALIZACIÓN
// ==============================================================================
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