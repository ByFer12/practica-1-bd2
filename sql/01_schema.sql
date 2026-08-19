
USE hotel_db;


CREATE TABLE IF NOT EXISTS CLIENTE (
    id_cliente INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20) NOT NULL,
    documento_identidad VARCHAR(30) NOT NULL UNIQUE,
    pais_origen VARCHAR(80) NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS HABITACION (
    id_habitacion INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    codigo_sede VARCHAR(10) NOT NULL,
    region VARCHAR(80) NOT NULL,
    numero_habitacion VARCHAR(10) NOT NULL,
    piso TINYINT UNSIGNED NOT NULL,
    tipo_habitacion ENUM(
        'INDIVIDUAL',
        'DOBLE',
        'TRIPLE',
        'SUITE'
    ) NOT NULL,
    capacidad TINYINT UNSIGNED NOT NULL,
    precio_noche DECIMAL(10,2) NOT NULL,
    estado_actual ENUM(
        'DISPONIBLE',
        'RESERVADA',
        'OCUPADA',
        'LIMPIEZA',
        'MANTENIMIENTO'
    ) NOT NULL DEFAULT 'DISPONIBLE',
    activa BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT uq_habitacion_sede_numero
        UNIQUE (codigo_sede, numero_habitacion),

    CONSTRAINT chk_habitacion_piso
        CHECK (piso > 0),

    CONSTRAINT chk_habitacion_capacidad
        CHECK (capacidad > 0),

    CONSTRAINT chk_habitacion_precio
        CHECK (precio_noche > 0)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS EMPLEADO (
    id_empleado INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL,
    apellido VARCHAR(80) NOT NULL,
    correo VARCHAR(150) NOT NULL UNIQUE,
    telefono VARCHAR(20) NOT NULL,
    puesto VARCHAR(60) NOT NULL,
    fecha_contratacion DATE NOT NULL,
    activo BOOLEAN NOT NULL DEFAULT TRUE
) ENGINE = InnoDB;

CREATE TABLE IF NOT EXISTS RESERVA (
    id_reserva INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    id_cliente INT UNSIGNED NOT NULL,
    id_habitacion INT UNSIGNED NOT NULL,
    id_empleado INT UNSIGNED NOT NULL,

    fecha_reserva DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_entrada DATE NOT NULL,
    fecha_salida DATE NOT NULL,

    numero_huespedes TINYINT UNSIGNED NOT NULL,

    canal_reserva ENUM(
        'WEB',
        'TELEFONO',
        'PRESENCIAL',
        'AGENCIA'
    ) NOT NULL,

    estado ENUM(
        'PENDIENTE',
        'CONFIRMADA',
        'CHECK_IN',
        'CHECK_OUT',
        'CANCELADA'
    ) NOT NULL DEFAULT 'PENDIENTE',

    monto_total DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_reserva_cliente
        FOREIGN KEY (id_cliente)
        REFERENCES CLIENTE (id_cliente)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_reserva_habitacion
        FOREIGN KEY (id_habitacion)
        REFERENCES HABITACION (id_habitacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_reserva_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO (id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_reserva_fechas
        CHECK (fecha_salida > fecha_entrada),

    CONSTRAINT chk_reserva_huespedes
        CHECK (numero_huespedes > 0),

    CONSTRAINT chk_reserva_monto
        CHECK (monto_total >= 0)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS PAGO (
    id_pago INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    id_reserva INT UNSIGNED NOT NULL,
    id_empleado INT UNSIGNED NOT NULL,

    fecha_pago DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    monto DECIMAL(10,2) NOT NULL,

    metodo_pago ENUM(
        'EFECTIVO',
        'TARJETA',
        'TRANSFERENCIA'
    ) NOT NULL,

    estado ENUM(
        'PENDIENTE',
        'APROBADO',
        'RECHAZADO',
        'ANULADO'
    ) NOT NULL DEFAULT 'PENDIENTE',

    referencia VARCHAR(50) UNIQUE NULL,

    CONSTRAINT fk_pago_reserva
        FOREIGN KEY (id_reserva)
        REFERENCES RESERVA (id_reserva)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_pago_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO (id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_pago_monto
        CHECK (monto > 0)
) ENGINE = InnoDB;


CREATE TABLE IF NOT EXISTS LOG_HABITACION (
    id_log INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    id_habitacion INT UNSIGNED NOT NULL,
    id_empleado INT UNSIGNED NOT NULL,

    estado_anterior ENUM(
        'DISPONIBLE',
        'RESERVADA',
        'OCUPADA',
        'LIMPIEZA',
        'MANTENIMIENTO'
    ) NOT NULL,

    estado_nuevo ENUM(
        'DISPONIBLE',
        'RESERVADA',
        'OCUPADA',
        'LIMPIEZA',
        'MANTENIMIENTO'
    ) NOT NULL,

    fecha_cambio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    motivo VARCHAR(255) NOT NULL,

    CONSTRAINT fk_log_habitacion
        FOREIGN KEY (id_habitacion)
        REFERENCES HABITACION (id_habitacion)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT fk_log_empleado
        FOREIGN KEY (id_empleado)
        REFERENCES EMPLEADO (id_empleado)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_log_estado
        CHECK (estado_anterior <> estado_nuevo)
) ENGINE = InnoDB;