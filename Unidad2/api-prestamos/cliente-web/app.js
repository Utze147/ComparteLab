const API_URL = "http://localhost:8000/api/v1";

// Función centralizada de comunicación HTTP
async function solicitar(endpoint, opciones = {}) {
    const respuesta = await fetch(`${API_URL}${endpoint}`, opciones);
    let datos = null;

    if (respuesta.status !== 204) {
        datos = await respuesta.json();
    }

    if (!respuesta.ok) {
        const error = new Error(
            datos?.error?.mensaje ?? `Error al comunicarse con la API (HTTP ${respuesta.status})`
        );
        error.status = respuesta.status;
        error.codigo = datos?.error?.codigo;
        error.detalles = datos?.error?.detalles;
        throw error;
    }

    return datos;
}

// 1. Obtener y listar equipos (GET /equipos)
async function obtenerEquipos() {
    mostrarCarga(true);
    limpiarMensajes();
    try {
        const equipos = await solicitar("/equipos");
        mostrarEquipos(equipos);
    } catch (error) {
        mostrarError(error);
    } finally {
        mostrarCarga(false);
    }
}

// 2. Registrar un equipo (POST /equipos)
async function crearEquipo() {
    const equipo = {
        tipo: document.getElementById("tipo").value,
        marca: document.getElementById("marca").value.trim(),
        modelo: document.getElementById("modelo").value.trim(),
        numero_inventario: document.getElementById("inventario").value.trim()
    };

    try {
        await solicitar("/equipos", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(equipo)
        });
        mostrarMensaje("Equipo registrado correctamente.");
        document.getElementById("formEquipo").reset();
        await obtenerEquipos();
    } catch (error) {
        mostrarError(error);
    }
}

// Renderizar tabla de equipos en la UI
function mostrarEquipos(equipos) {
    const tabla = document.getElementById("tablaEquipos");
    const sinDatos = document.getElementById("sinDatos");
    tabla.innerHTML = "";

    if (equipos.length === 0) {
        sinDatos.classList.remove("d-none");
        return;
    }

    sinDatos.classList.add("d-none");
    equipos.forEach(equipo => {
        const fila = document.createElement("tr");
        fila.innerHTML = `
            <td>${equipo.id}</td>
            <td><span class="badge bg-secondary">${equipo.tipo}</span></td>
            <td>${equipo.marca}</td>
            <td>${equipo.modelo}</td>
            <td><code>${equipo.numero_inventario}</code></td>
            <td><span class="badge ${equipo.estado === 'disponible' ? 'bg-success' : 'bg-warning text-dark'}">${equipo.estado}</span></td>
        `;
        tabla.appendChild(fila);
    });
}

// Gestión de Estados Visuales de la Interfaz
function mostrarCarga(activo) {
    document.getElementById("cargando").classList.toggle("d-none", !activo);
}

function mostrarMensaje(texto) {
    const mensaje = document.getElementById("mensaje");
    mensaje.className = "alert alert-success";
    mensaje.textContent = texto;
}

function mostrarError(error) {
    const mensaje = document.getElementById("mensaje");
    mensaje.className = "alert alert-danger";
    mensaje.textContent = `[${error.codigo || 'ERROR'}] ${error.message}`;
}

function limpiarMensajes() {
    const mensaje = document.getElementById("mensaje");
    mensaje.className = "alert d-none";
    mensaje.textContent = "";
}

// Event Listeners
document.getElementById("btnActualizar").addEventListener("click", obtenerEquipos);
document.getElementById("formEquipo").addEventListener("submit", async evento => {
    evento.preventDefault();
    await crearEquipo();
});

// Ejecución inicial al cargar la página
obtenerEquipos();