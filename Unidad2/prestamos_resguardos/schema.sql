CREATE DATABASE IF NOT EXISTS prestamos_resguardos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE prestamos_resguardos;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    matricula VARCHAR(30) NOT NULL UNIQUE,
    correo VARCHAR(150) NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE=InnoDB;

CREATE TABLE equipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(30) NOT NULL UNIQUE,
    nombre VARCHAR(100) NOT NULL,
    descripcion VARCHAR(500) NOT NULL DEFAULT '',
    estado ENUM(
        'disponible',
        'prestado',
        'mantenimiento',
        'baja'
    ) NOT NULL DEFAULT 'disponible'
) ENGINE=InnoDB;

CREATE TABLE prestamos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    equipo_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_prestamo DATE NOT NULL,
    fecha_limite DATE NOT NULL,
    observaciones VARCHAR(500) NOT NULL DEFAULT '',
    estado ENUM('activo', 'devuelto') NOT NULL DEFAULT 'activo',

    CONSTRAINT fk_prestamo_equipo
        FOREIGN KEY (equipo_id) REFERENCES equipos(id),

    CONSTRAINT fk_prestamo_usuario
        FOREIGN KEY (usuario_id) REFERENCES usuarios(id),

    INDEX idx_prestamos_estado (estado)
) ENGINE=InnoDB;

CREATE TABLE devoluciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    prestamo_id INT NOT NULL UNIQUE,
    fecha_devolucion DATE NOT NULL,
    condicion ENUM('bueno', 'danado') NOT NULL,
    observaciones VARCHAR(500) NOT NULL DEFAULT '',

    CONSTRAINT fk_devolucion_prestamo
        FOREIGN KEY (prestamo_id) REFERENCES prestamos(id)
) ENGINE=InnoDB;

CREATE USER 'prestamos_app'@'localhost'
IDENTIFIED BY 'Test1234';

GRANT SELECT, INSERT, UPDATE, DELETE
ON prestamos_resguardos.*
TO 'prestamos_app'@'localhost';