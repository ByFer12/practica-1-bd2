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

## 3. Implementación de la Base de Datos

Una vez definido el modelo relacional, se procedió a implementar la base de datos en MySQL 8.0 utilizando scripts SQL versionados dentro del repositorio.

Los archivos principales utilizados fueron:

```text
sql/
├── 00_create_database.sql
├── 01_schema.sql
└── 02_drop_database.sql
```

### 3.1 Creación de la base de datos

El archivo `00_create_database.sql` crea la base de datos `hotel_db` utilizando el conjunto de caracteres `utf8mb4`.

```sql
CREATE DATABASE IF NOT EXISTS hotel_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE hotel_db;
```

El script fue ejecutado mediante:

```bash
mysql -u root -p < sql/00_create_database.sql
```

### 3.2 Creación del esquema

El archivo `01_schema.sql` contiene la definición de las seis tablas:

```text
CLIENTE
HABITACION
EMPLEADO
RESERVA
PAGO
LOG_HABITACION
```

Además, define:

* claves primarias;
* claves foráneas;
* restricciones `UNIQUE`;
* restricciones `CHECK`;
* valores por defecto;
* reglas de integridad referencial.

El esquema fue ejecutado mediante:

```bash
mysql -u root -p < sql/01_schema.sql
```

### 3.3 Reconstrucción de la base de datos

Durante el desarrollo fue necesario sustituir una versión inicial del esquema por el diseño definitivo.

Para ello se eliminó la base de datos existente y posteriormente se volvió a crear desde los scripts.

El archivo `02_drop_database.sql` contiene:

```sql
DROP DATABASE IF EXISTS hotel_db;
```

La reconstrucción se realizó mediante:

```bash
mysql -u root -p < sql/02_drop_database.sql
mysql -u root -p < sql/00_create_database.sql
mysql -u root -p < sql/01_schema.sql
```

Este procedimiento permite reconstruir completamente la estructura de la base de datos a partir de los archivos versionados en el repositorio.

---

## 4. Preparación de los Respaldos Incrementales

Para los respaldos incrementales se decidió utilizar los **Binary Logs de MySQL**.

Los Binary Logs registran los cambios realizados sobre la base de datos y permiten reproducir posteriormente esas operaciones.

### 4.1 Verificación de Binary Logs

Se verificó que el registro binario estuviera habilitado mediante:

```bash
mysql -u root -p -e "
SHOW VARIABLES LIKE 'log_bin';
SHOW MASTER STATUS;
SHOW BINARY LOGS;
"
```

El servidor devolvió:

```text
log_bin = ON
```

El Binary Log utilizado durante la carga del Día 1 fue:

```text
binlog.000006
```

También se verificó el formato utilizado:

```bash
mysql -u root -p -e "
SHOW VARIABLES LIKE 'binlog_format';
"
```

Resultado:

```text
binlog_format = ROW
```

El formato `ROW` registra los cambios realizados sobre las filas de las tablas.

---

## 5. Backup Base

Antes de poder reconstruir una cadena de respaldos incrementales es necesario disponer de un respaldo que contenga únicamente la estructura inicial de la base de datos.

El backup base fue creado mediante:

```bash
mysqldump -u root -p \
  --no-data \
  --routines \
  --triggers \
  hotel_db > backups/backup_base.sql
```

La opción:

```text
--no-data
```

indica a `mysqldump` que debe exportar únicamente la estructura y no los registros almacenados.

### 5.1 Verificación del backup base

Para comprobar que el archivo no contenía datos se utilizó:

```bash
grep -m 3 "^INSERT INTO" backups/backup_base.sql
```

El comando no produjo resultados, confirmando que el respaldo contiene únicamente la estructura.

Información obtenida:

```text
Archivo: backups/backup_base.sql
Tamaño: 8,934 bytes
Fecha: 2026-08-18 23:45:25
```

### 5.2 Procedimiento ideal

En esta ejecución el backup base fue generado después de haber realizado la carga del Día 1.

Esto no afecta su contenido debido a que se utilizó `--no-data`, por lo que el archivo generado contiene únicamente la estructura.

Sin embargo, el procedimiento técnicamente recomendado para esta práctica habría sido:

```text
Crear base de datos
        ↓
Crear tablas
        ↓
Crear backup base
        ↓
Registrar posición inicial del Binary Log
        ↓
Realizar carga Día 1
```

Con este procedimiento, el punto inicial del primer respaldo incremental habría quedado registrado antes de modificar los datos.

El comando para obtener dicha posición habría sido:

```bash
mysql -u root -p -e "SHOW MASTER STATUS;"
```

La posición obtenida en ese momento se habría registrado como:

```text
inicio_incremental_dia1
```

Esto evita tener que localizar posteriormente el comienzo de la transacción dentro del Binary Log.

---

## 6. Día 1 — Carga Inicial

El primer archivo de carga utilizado fue:

```text
sql/carga/01_carga_dia1.sql
```

Este archivo contiene:

```text
300 CLIENTE
300 HABITACION
300 EMPLEADO
```

Total:

```text
900 registros
```

La carga fue ejecutada mediante:

```bash
mysql -u root -p < sql/carga/01_carga_dia1.sql
```

El resultado obtenido fue:

```text
total_clientes
300

total_habitaciones
300

total_empleados
300
```

### 6.1 Uso de transacción

El archivo utiliza:

```sql
START TRANSACTION;
```

antes de las inserciones y:

```sql
COMMIT;
```

al finalizar.

Esto agrupa la carga del Día 1 dentro de una sola transacción.

Conceptualmente:

```text
BEGIN
   ├── 300 CLIENTE
   ├── 300 HABITACION
   └── 300 EMPLEADO
COMMIT
```

Esto también facilitó la identificación posterior de la operación completa dentro del Binary Log.

### 6.2 Verificación

Después de la carga se verificó la cantidad de registros mediante:

```sql
SELECT COUNT(*) AS total_clientes
FROM CLIENTE;

SELECT COUNT(*) AS total_habitaciones
FROM HABITACION;

SELECT COUNT(*) AS total_empleados
FROM EMPLEADO;
```

Resultados:

| Tabla      | Registros |
| ---------- | --------: |
| CLIENTE    |       300 |
| HABITACION |       300 |
| EMPLEADO   |       300 |
| **Total**  |   **900** |

También se ejecutaron consultas `SELECT *` para comprobar visualmente los datos insertados.

Las evidencias correspondientes se almacenan en:

```text
evidencia/dia1/
```

---

## 7. Backup Completo del Día 1

Después de finalizar la carga se generó un respaldo completo de la base de datos.

El comando utilizado fue:

```bash
mysqldump -u root -p \
  --single-transaction \
  --routines \
  --triggers \
  hotel_db > backups/full/full_dia1.sql
```

El archivo generado contiene tanto la estructura como los datos disponibles al finalizar el Día 1.

### 7.1 Verificación

Se verificó que el archivo contuviera instrucciones de inserción mediante:

```bash
grep -m 3 "^INSERT INTO" backups/full/full_dia1.sql
```

En este caso sí se encontraron instrucciones `INSERT INTO`, confirmando que el respaldo contiene datos.

Información registrada:

```text
Archivo: backups/full/full_dia1.sql
Tamaño: 91,964 bytes
Fecha: 2026-08-19 00:06:31
```

El respaldo completo puede restaurar por sí mismo el estado de la base de datos correspondiente al Día 1.

---

## 8. Backup Incremental del Día 1

Debido a que no se había registrado la posición del Binary Log inmediatamente antes de la carga, fue necesario identificar posteriormente el intervalo correspondiente a la transacción del Día 1.

### 8.1 Inspección del Binary Log

Debido a que el servidor utiliza:

```text
binlog_format = ROW
```

se utilizó `mysqlbinlog` con decodificación de eventos de fila.

Para localizar los `INSERT` se utilizó:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv \
  /var/lib/mysql/binlog.000006 \
  | grep -n -m 10 "^### INSERT INTO"
```

Esto permitió identificar los eventos correspondientes a la tabla `CLIENTE`.

Posteriormente se inspeccionó el bloque anterior al primer evento mediante:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv \
  /var/lib/mysql/binlog.000006 \
  | sed -n '520,535p'
```

Se identificó el comienzo de la transacción:

```text
# at 11127
BEGIN
```

Por lo tanto:

```text
posición inicial = 11127
```

### 8.2 Localización del final de la transacción

Para localizar el `COMMIT` se inspeccionaron los eventos `Xid`:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv \
  /var/lib/mysql/binlog.000006 \
  | grep -n -A 5 -B 5 "Xid ="
```

El evento correspondiente al Día 1 fue:

```text
# at 71262
end_log_pos 71293
Xid = 94
COMMIT
```

Por lo tanto:

```text
posición final = 71293
```

El intervalo correspondiente a la carga fue:

```text
binlog.000006

11127 ───────────────────────────── 71293
 BEGIN                               COMMIT
   │
   ├── 300 CLIENTE
   ├── 300 HABITACION
   └── 300 EMPLEADO
```

### 8.3 Generación del incremental

Con las posiciones identificadas se generó el archivo:

```bash
sudo mysqlbinlog \
  --start-position=11127 \
  --stop-position=71293 \
  /var/lib/mysql/binlog.000006 \
  > backups/incremental/incremental_dia1.sql
```

Información registrada:

```text
Archivo: backups/incremental/incremental_dia1.sql
Binary Log: binlog.000006
Inicio: 11127
Fin: 71293
Tamaño: 84,326 bytes
Fecha: 2026-08-19 00:36:19
```

### 8.4 Verificación estructural

Se verificó que el incremental conservara el inicio y final de la transacción:

```bash
grep -n -E "BEGIN|COMMIT" backups/incremental/incremental_dia1.sql
```

Resultado:

```text
28:BEGIN
1125:COMMIT/*!*/;
```

Esto confirma que el archivo contiene la transacción completa correspondiente a la carga del Día 1.

---

## 9. Resumen del Día 1

Al finalizar esta etapa se obtuvieron los siguientes resultados:

| Elemento           | Resultado     |
| ------------------ | ------------- |
| CLIENTE            | 300 registros |
| HABITACION         | 300 registros |
| EMPLEADO           | 300 registros |
| Total de registros | 900           |
| Backup base        | Correcto      |
| Backup completo    | Correcto      |
| Backup incremental | Correcto      |
| Binary Log         | binlog.000006 |
| Inicio incremental | 11127         |
| Fin incremental    | 71293         |

### 9.1 Tamaño de los respaldos

| Respaldo             | Tipo        |       Tamaño |
| -------------------- | ----------- | -----------: |
| backup_base.sql      | Base        |  8,934 bytes |
| full_dia1.sql        | Completo    | 91,964 bytes |
| incremental_dia1.sql | Incremental | 84,326 bytes |

Los tiempos de creación no fueron registrados durante esta primera ejecución, por lo que no se asignan valores estimados o inventados.

A partir de las siguientes etapas los tiempos serán medidos directamente durante la ejecución de los comandos.

---

## 10. Procedimiento Recomendado para los Siguientes Días

A partir del Día 2 se utilizará un procedimiento más controlado.

Antes de cada carga:

```bash
mysql -u root -p -e "SHOW MASTER STATUS;"
```

Se registrarán:

```text
Binary Log
posición inicial
```

Después se ejecutará la carga correspondiente.

Al finalizar:

```bash
mysql -u root -p -e "SHOW MASTER STATUS;"
```

Se registrará:

```text
posición final
```

El incremento quedará definido directamente por:

```text
posición inicial → posición final
```

Por ejemplo:

```text
ANTES DE DÍA 2
posición = X

        ↓ carga Día 2

DESPUÉS DE DÍA 2
posición = Y
```

Entonces:

```bash
sudo mysqlbinlog \
  --start-position=X \
  --stop-position=Y \
  /var/lib/mysql/binlog.XXXXXX \
  > backups/incremental/incremental_dia2.sql
```

Este procedimiento evita tener que buscar manualmente las transacciones después de que fueron ejecutadas.

### 10.1 Medición de tiempo

Para las siguientes etapas se utilizará `time` sobre el comando correspondiente.

Ejemplo para un backup completo:

```bash
time mysqldump -u root -p \
  --single-transaction \
  --routines \
  --triggers \
  hotel_db > backups/full/full_dia2.sql
```

El tiempo real obtenido se registrará en la bitácora y en los archivos de resultados.

### 10.2 Principio utilizado

La estrategia de las siguientes etapas será:

```text
Registrar inicio
      ↓
Realizar cambios
      ↓
Registrar fin
      ↓
Crear FULL
      ↓
Extraer INCREMENTAL
      ↓
Registrar tamaño y tiempo
      ↓
Actualizar bitácora
```

Esto permitirá mantener una cadena de respaldos reproducible y facilitar posteriormente las pruebas de restauración.
## 11. Ejecución de las Etapas Día 2 a Día 5

Las etapas posteriores utilizaron el mismo procedimiento técnico documentado para el Día 1:

1. Registrar posición inicial del Binary Log.
2. Ejecutar el archivo de carga correspondiente.
3. Verificar los registros insertados.
4. Registrar posición final del Binary Log.
5. Crear backup completo.
6. Extraer el intervalo correspondiente al backup incremental.
7. Registrar tamaño, fecha, hora y tiempo de ejecución.
8. Guardar las evidencias correspondientes.

Los detalles específicos de cada etapa se resumen a continuación.

### Día 2 — RESERVA

- Archivo de carga: `sql/carga/02_carga_dia2.sql`
- Registros insertados: [cantidad real]
- Backup completo: `backups/full/full_dia2.sql`
- Incremental: `backups/incremental/incremental_dia2.sql`
- Binary Log: [archivo real]
- Posición inicial: [posición]
- Posición final: [posición]
- Tamaño full: [bytes]
- Tamaño incremental: [bytes]
- Resultado: Correcto

### Día 3 — Primer LOG_HABITACION

[misma estructura]

### Día 4 — PAGO

[misma estructura]

### Día 5 — Segundo LOG_HABITACION

[misma estructura]