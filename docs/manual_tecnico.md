# Manual Técnico — Práctica 1: Respaldos y Recuperación en Bases de Datos Relacionales
**Curso:** Bases de Datos 2  
**Semestre:** Segundo Semestre 2026  
**SGBD:** MySQL 8.0  

---

## 1. Introducción

El presente documento detalla la arquitectura, el diseño, la implementación y los procesos de administración de la base de datos relacional orientada a la gestión de operaciones de una cadena hotelera. Esta práctica tiene como objetivo fundamental aplicar técnicas de respaldo completo e incremental, evaluar estrategias de recuperación ante fallos y medir el rendimiento, los tiempos y los tamaños de almacenamiento bajo un entorno controlado en MySQL.

---

## 2. Diseño de la Base de Datos

La base de datos fue diseñada para representar las operaciones principales de una cadena hotelera, considerando clientes, habitaciones, empleados, reservas, pagos y el historial de cambios de estado de las habitaciones.

El diseño mantiene las seis entidades requeridas por la práctica:

- CLIENTE
- HABITACION
- EMPLEADO
- RESERVA
- PAGO
- LOG_HABITACION

Se decidió no agregar entidades adicionales como HOTEL, REGION, PUESTO o METODO_PAGO, debido a que no son necesarias para cumplir los objetivos de la práctica y aumentarían innecesariamente la complejidad de la carga, respaldo y restauración de la información.

### 2.1 Propósito de las entidades

| Entidad | Propósito |
|---|---|
| CLIENTE | Almacena los datos generales y de contacto de los clientes. |
| HABITACION | Registra las habitaciones, sus características, ubicación dentro de la cadena y estado actual. |
| EMPLEADO | Almacena los empleados responsables de registrar operaciones. |
| RESERVA | Registra las reservaciones realizadas por los clientes para determinadas habitaciones. |
| PAGO | Registra los pagos realizados asociados a una reservación. |
| LOG_HABITACION | Mantiene el historial de cambios de estado de las habitaciones. |

### 2.2 Diagrama entidad-relación

El siguiente diagrama representa las entidades, sus atributos principales y las relaciones establecidas mediante claves primarias y foráneas.

![Modelo entidad-relación](diagramas/modelo_relacional.png)

El archivo editable del diagrama se conserva en formato `.drawio` dentro del repositorio para permitir futuras modificaciones y mantener la trazabilidad del diseño.

### 2.3 Diccionario de datos

#### 2.3.1 CLIENTE

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_cliente | INT UNSIGNED | PK, AUTO_INCREMENT | Identificador único del cliente. |
| nombre | VARCHAR(80) | NOT NULL | Nombre del cliente. |
| apellido | VARCHAR(80) | NOT NULL | Apellido del cliente. |
| correo | VARCHAR(150) | NOT NULL, UNIQUE | Correo electrónico del cliente. |
| telefono | VARCHAR(20) | NOT NULL | Número telefónico del cliente. |
| documento_identidad | VARCHAR(30) | NOT NULL, UNIQUE | Documento que identifica al cliente. |
| pais_origen | VARCHAR(80) | NOT NULL | País de origen del cliente. |
| fecha_registro | DATETIME | NOT NULL | Fecha y hora en que fue registrado. |
| activo | BOOLEAN | NOT NULL, DEFAULT TRUE | Permite conservar clientes históricos sin eliminarlos. |

**Justificación:** además de los datos básicos de contacto, se incorporan atributos que permiten identificar individualmente a los clientes, registrar su procedencia y conservar el historial sin eliminar registros utilizados por otras operaciones.

#### 2.3.2 HABITACION

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| id_habitacion | INT UNSIGNED | PK, AUTO_INCREMENT | Identificador interno de la habitación. |
| codigo_sede | VARCHAR(10) | NOT NULL | Código de la sede donde se encuentra. |
| region | VARCHAR(80) | NOT NULL | Región donde se encuentra la sede. |
| numero_habitacion | VARCHAR(10) | NOT NULL | Número visible de la habitación. |
| piso | TINYINT UNSIGNED | NOT NULL | Piso donde está ubicada. |
| tipo_habitacion | ENUM | NOT NULL | Tipo de habitación. |
| capacidad | TINYINT UNSIGNED | NOT NULL | Capacidad máxima de huéspedes. |
| precio_noche | DECIMAL(10,2) | NOT NULL | Precio de la habitación por noche. |
| estado_actual | ENUM | NOT NULL, DEFAULT DISPONIBLE | Estado actual de la habitación. |
| activa | BOOLEAN | NOT NULL, DEFAULT TRUE | Indica si la habitación continúa disponible para operaciones. |

Existe una restricción única sobre:

```text
(codigo_sede, numero_habitacion)