# ComparteLab 🔬💻

**ComparteLab** es un sistema web integral para la gestión y control del préstamo de equipo de laboratorio escolar o universitario. Permite a los estudiantes registrar solicitudes de préstamo de equipos y a los laboratoristas o docentes administrar y actualizar los estados de dichas solicitudes en tiempo real, garantizando la disponibilidad y evitando conflictos de asignación.

---

## 📌 Tabla de Contenidos

- [Características Principales](#-características-principales)
- [Arquitectura y Tecnologías](#-arquitectura-y-tecnologías)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Reglas de Negocio](#-reglas-de-negocio)
- [Requisitos Previos](#-requisitos-previos)
- [Instalación y Puesta en Marcha](#-instalación-y-puesta-en-marcha)
  - [1. Backend (FastAPI + SQLite)](#1-backend-fastapi--sqlite)
  - [2. Frontend (HTML5 + Bootstrap + JS)](#2-frontend-html5--bootstrap--js)
- [Documentación de la API](#-documentación-de-la-api)
  - [Endpoints](#endpoints)
  - [Modelos de Datos](#modelos-de-datos)
- [Flujo de Estados de Préstamo](#-flujo-de-estados-de-préstamo)

---

## 🚀 Características Principales

- **Registro de solicitudes**: Formulario validado para captura de matrícula, nombre de alumno, número de equipo y justificación.
- **Validación y Reglas de Negocio**:
  - Validación de campos del lado del cliente y del servidor (Pydantic).
  - Bloqueo por conflicto (HTTP 409) si un equipo ya se encuentra en estado `PENDIENTE` o `APROBADA`.
- **Panel de Gestión de Solicitudes**:
  - Visualización tabular con actualización dinámica.
  - Indicadores visuales mediante badges de estado (`PENDIENTE`, `APROBADA`, `RECHAZADA`, `DEVUELTO`).
  - Botones de acción directa para cambiar estado (Aprobar, Rechazar, Marcar como Devuelto).
- **Persistencia Ligera y Confiable**: Base de datos SQLite integrada, autoconfigurable al iniciar el servicio.
- **Documentación Interactiva Automática**: Swagger UI y ReDoc integrados mediante FastAPI.

---

## 🛠️ Arquitectura y Tecnologías

### Backend
- **Lenguaje**: Python 3.12+ / 3.13+
- **Framework API**: [FastAPI](https://fastapi.tiangolo.com/)
- **Servidor ASGI**: [Uvicorn](https://www.uvicorn.org/)
- **Validación de Datos**: [Pydantic v2](https://docs.pydantic.dev/)
- **Base de Datos**: [SQLite3](https://docs.python.org/3/library/sqlite3.html) (con soporte nativo en Python)
- **Middleware**: Soporte CORS abierto para integración frontend desacoplada.

### Frontend
- **Estructura y Marcado**: HTML5 semántico
- **Estilos y Componentes**: [Bootstrap 5.3](https://getbootstrap.com/) & [Bootstrap Icons](https://icons.getbootstrap.com/) (vía CDN)
- **Lógica e Interacción**: JavaScript Vanilla (ES6+, Fetch API, manipulación asíncrona del DOM sin dependencias pesadas).

---

## 📂 Estructura del Proyecto

```text
ComparteLab/
│
├── backend/
│   ├── app/                    # Directorio modular para escalabilidad
│   │   └── routers/            # Rutas modulares (futura expansión)
│   ├── main.py                 # API FastAPI, conexión SQLite, esquemas y endpoints
│   ├── requirements.txt        # Dependencias de Python (fastapi, uvicorn)
│   └── comparte_lab.db         # Archivo de base de datos SQLite (generado automáticamente)
│
├── index.html                  # Interfaz principal (Formulario y tabla de solicitudes)
├── app.js                      # Controlador JS del cliente (consumo de API REST)
├── .gitignore                  # Exclusiones de control de versiones (.venv, bases de datos locales, etc.)
└── README.md                   # Documentación del proyecto
```

---

## ⚖️ Reglas de Negocio

1. **Unicidad de préstamo activo**: Un equipo no puede ser solicitado de nuevo si ya tiene una solicitud activa en estado `PENDIENTE` o `APROBADA`. Si se intenta, la API responde con un código de error `409 Conflict`.
2. **Liberación de equipo**: Cuando una solicitud cambia a estado `RECHAZADA` o `DEVUELTO`, el equipo vuelve a estar disponible para nuevas solicitudes.
3. **Validación estricta**:
   - **Matrícula**: Longitud de 3 a 20 caracteres alfanuméricos.
   - **Nombre**: Longitud de 3 a 100 caracteres.
   - **ID de Equipo**: Entero positivo mayor a 0.
   - **Motivo**: Longitud de 5 a 300 caracteres.

---

## 📋 Requisitos Previos

- **Python**: Versión 3.10 o superior (recomendado 3.12+).
- **Navegador Web**: Cualquier navegador moderno (Chrome, Firefox, Edge, Safari).
- (Opcional) Extensión **Live Server** en VS Code o un servidor estático como `http-server` o el módulo `http.server` de Python.

---

## ⚙️ Instalación y Puesta en Marcha

### 1. Backend (FastAPI + SQLite)

1. Abre una terminal y navega hasta el directorio del backend:
   ```bash
   cd backend
   ```

2. (Opcional pero recomendado) Crea y activa un entorno virtual:
   - **Windows (PowerShell)**:
     ```powershell
     python -m venv .venv
     .venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicia el servidor de desarrollo con Uvicorn:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

5. El backend estará disponible en `http://127.0.0.1:8000`.

---

### 2. Frontend (HTML5 + Bootstrap + JS)

El frontend está compuesto por archivos estáticos en la raíz del proyecto.

#### Opción A: Servidor HTTP simple de Python
En una terminal en la raíz del proyecto:
```bash
python -m http.server 5500
```
Luego abre tu navegador en:
```
http://localhost:5500
```

#### Opción B: Live Server (Visual Studio Code)
1. Instala la extensión **Live Server**.
2. Haz clic derecho sobre [`index.html`](index.html) y selecciona **Open with Live Server**.

#### Opción C: Apertura directa
Puedes abrir directamente el archivo [`index.html`](index.html) en tu navegador, asegurándote de que el backend esté ejecutándose en `http://127.0.0.1:8000`.

---

## 📖 Documentación de la API

FastAPI genera automáticamente documentación interactiva accesible una vez que el backend está corriendo:
- **Swagger UI**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- **ReDoc**: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

### Endpoints

| Método | Ruta | Descripción | Códigos de Respuesta |
| :--- | :--- | :--- | :--- |
| `POST` | `/api/v1/solicitudes` | Registra una nueva solicitud de préstamo | `201 Created`, `409 Conflict`, `422 Unprocessable Entity` |
| `GET` | `/api/v1/solicitudes` | Obtiene el listado de todas las solicitudes ordenadas descendentemente por ID | `200 OK` |
| `PATCH` | `/api/v1/solicitudes/{id}/estado` | Actualiza el estado de una solicitud (`APROBADA`, `RECHAZADA`, `DEVUELTO`, `PENDIENTE`) | `200 OK`, `400 Bad Request`, `404 Not Found` |

### Modelos de Datos

#### Solicitud de Creación (`POST /api/v1/solicitudes`)
```json
{
  "matricula": "2024001",
  "nombre_alumno": "Carlos Mendoza",
  "equipo_id": 1,
  "motivo": "Práctica de laboratorio de redes"
}
```

#### Cambio de Estado (`PATCH /api/v1/solicitudes/{id}/estado`)
```json
{
  "estado": "APROBADA"
}
```

---

## 🔄 Flujo de Estados de Préstamo

```text
       [ Nueva Solicitud ]
                │
                ▼
        ┌───────────────┐
        │   PENDIENTE   │
        └───────┬───────┘
                │
        ┌───────┴───────┐
        ▼               ▼
┌───────────────┐ ┌───────────────┐
│   APROBADA    │ │   RECHAZADA   │
└───────┬───────┘ └───────────────┘
        │          (Equipo liberado)
        ▼
┌───────────────┐
│   DEVUELTO    │
└───────────────┘
 (Equipo liberado)
```

---

## 👨‍💻 Autor y Contribuciones

Desarrollado para el control y préstamo eficiente de material de laboratorio en **ComparteLab**. ¡Contribuciones, sugerencias y mejoras son bienvenidas!
- Uriel Barrales Martinez
- Jose Abimael Cisneros Escamilla
