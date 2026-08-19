# Comandos de Backups y Restauración — Práctica 1 BD2

> Guía operativa. Los comandos están ordenados según el flujo real de la práctica.
> Base de datos: `hotel_db`  
> Login Path recomendado: `bd2`

---

## 1. Preparación inicial

### 1.1 Crear la base y el esquema

```bash
mysql --login-path=bd2 < sql/00_create_database.sql
mysql --login-path=bd2 < sql/01_schema.sql
```

### 1.2 Verificar Binary Log

```bash
mysql --login-path=bd2 -e "
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
SHOW MASTER STATUS;
SHOW BINARY LOGS;
"
```

Condiciones usadas en la práctica:

```text
log_bin = ON
binlog_format = ROW
Binary Log utilizado = binlog.000006
```

### 1.3 Crear el backup base ANTES de cargar datos

```bash
mysqldump --login-path=bd2 \
  --no-data \
  --routines \
  --triggers \
  hotel_db > backups/backup_base.sql
```

Verificar que no contenga datos:

```bash
grep -m 3 "^INSERT INTO" backups/backup_base.sql
```

Si no muestra resultados, el backup contiene únicamente estructura.

### Alternativa si el backup base se genera después de haber cargado datos

Puede generarse igualmente con `--no-data`:

```bash
mysqldump --login-path=bd2 \
  --no-data \
  --routines \
  --triggers \
  hotel_db > backups/backup_base.sql
```

El archivo seguirá conteniendo únicamente la estructura. Sin embargo, para generar correctamente el **incremental del Día 1** será necesario identificar en el Binary Log la posición donde comenzó la primera carga, porque ya no se habrá registrado previamente.

---

## 2. Flujo de trabajo para cada día

Para cada etapa se utiliza el mismo orden:

```text
1. Registrar posición inicial del Binary Log
2. Ejecutar carga del día
3. Verificar datos
4. Registrar posición final del Binary Log
5. Crear backup completo
6. Crear backup incremental con el rango inicio → fin
7. Registrar tamaño, fecha y tiempo
```

### 2.1 Registrar posición inicial

```bash
mysql --login-path=bd2 -e "SHOW MASTER STATUS;"
```

Guardar:

```text
Binary Log = archivo actual
Inicio = posición actual
```

### 2.2 Ejecutar la carga

Día 1:

```bash
mysql --login-path=bd2 < sql/carga/01_carga_dia1.sql
```

Día 2:

```bash
mysql --login-path=bd2 < sql/carga/02_carga_dia2.sql
```

Día 3:

```bash
mysql --login-path=bd2 < sql/carga/03_carga_dia3.sql
```

Día 4:

```bash
mysql --login-path=bd2 < sql/carga/04_carga_dia4.sql
```

Día 5:

```bash
mysql --login-path=bd2 < sql/carga/05_carga_dia5.sql
```

### 2.3 Verificar el estado

```bash
mysql --login-path=bd2 hotel_db -e "
SELECT 'CLIENTE' AS tabla, COUNT(*) AS registros FROM CLIENTE
UNION ALL
SELECT 'HABITACION', COUNT(*) FROM HABITACION
UNION ALL
SELECT 'EMPLEADO', COUNT(*) FROM EMPLEADO
UNION ALL
SELECT 'RESERVA', COUNT(*) FROM RESERVA
UNION ALL
SELECT 'PAGO', COUNT(*) FROM PAGO
UNION ALL
SELECT 'LOG_HABITACION', COUNT(*) FROM LOG_HABITACION;
"
```

Estados esperados:

| Día | CLIENTE | HABITACION | EMPLEADO | RESERVA | PAGO | LOG_HABITACION |
|---:|---:|---:|---:|---:|---:|---:|
| 1 | 300 | 300 | 300 | 0 | 0 | 0 |
| 2 | 300 | 300 | 300 | 300 | 0 | 0 |
| 3 | 300 | 300 | 300 | 300 | 0 | 300 |
| 4 | 300 | 300 | 300 | 300 | 300 | 300 |
| 5 | 300 | 300 | 300 | 300 | 300 | 600 |

Para ejecutar también los `SELECT *` requeridos:

```bash
mysql --login-path=bd2 < sql/consultas/verificacion_completa.sql
```

### 2.4 Registrar posición final

```bash
mysql --login-path=bd2 -e "SHOW MASTER STATUS;"
```

Guardar:

```text
Fin = posición actual
```

### 2.5 Crear backup completo del día

Patrón:

```bash
time mysqldump --login-path=bd2 \
  --single-transaction \
  --routines \
  --triggers \
  hotel_db > backups/full/full_diaN.sql
```

Cambiar `N` por `1`, `2`, `3`, `4` o `5`.

### 2.6 Crear backup incremental del día

Primero autenticar `sudo` fuera de la medición:

```bash
sudo -v
```

Patrón:

```bash
time sudo mysqlbinlog \
  --start-position=INICIO \
  --stop-position=FIN \
  /var/lib/mysql/ARCHIVO_BINLOG \
  > backups/incremental/incremental_diaN.sql
```

Rangos utilizados en esta práctica:

| Día | Binary Log | Inicio | Fin |
|---:|---|---:|---:|
| 1 | `binlog.000006` | 11127 | 71293 |
| 2 | `binlog.000006` | 71293 | 82739 |
| 3 | `binlog.000006` | 82739 | 95746 |
| 4 | `binlog.000006` | 95746 | 106886 |
| 5 | `binlog.000006` | 106886 | 120913 |

Ejemplo Día 5:

```bash
time sudo mysqlbinlog \
  --start-position=106886 \
  --stop-position=120913 \
  /var/lib/mysql/binlog.000006 \
  > backups/incremental/incremental_dia5.sql
```

### 2.7 Consultar tamaño y fecha

```bash
stat -c "%n | %s bytes | %y" backups/full/full_diaN.sql
stat -c "%n | %s bytes | %y" backups/incremental/incremental_diaN.sql
```

---

## 3. Caso especial: no se registró el inicio del Día 1

Si la carga del Día 1 ya se ejecutó y no se guardó previamente la posición del Binary Log, localizar el primer evento de inserción:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv /var/lib/mysql/binlog.000006 \
  | grep -n -m 10 "^### INSERT INTO"
```

Inspeccionar el bloque anterior:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv /var/lib/mysql/binlog.000006 \
  | sed -n '520,535p'
```

Localizar el cierre de la transacción:

```bash
sudo mysqlbinlog \
  --base64-output=DECODE-ROWS \
  -vv /var/lib/mysql/binlog.000006 \
  | grep -n -A 5 -B 5 "Xid ="
```

En esta práctica se determinó:

```text
Inicio = 11127
Fin = 71293
```

Luego se generó normalmente el incremental:

```bash
sudo mysqlbinlog \
  --start-position=11127 \
  --stop-position=71293 \
  /var/lib/mysql/binlog.000006 \
  > backups/incremental/incremental_dia1.sql
```

---

## 4. Restauración de un backup completo

Cada full se restaura de forma independiente.

### 4.1 Eliminar la base actual

```bash
mysql --login-path=bd2 -e "DROP DATABASE IF EXISTS hotel_db;"
```

### 4.2 Crear la base vacía

```bash
mysql --login-path=bd2 < sql/00_create_database.sql
```

### 4.3 Restaurar el full seleccionado

```bash
time mysql --login-path=bd2 hotel_db < backups/full/full_diaN.sql
```

Ejemplo:

```bash
time mysql --login-path=bd2 hotel_db < backups/full/full_dia3.sql
```

### 4.4 Verificar

```bash
mysql --login-path=bd2 hotel_db -e "
SELECT 'CLIENTE' AS tabla, COUNT(*) AS registros FROM CLIENTE
UNION ALL
SELECT 'HABITACION', COUNT(*) FROM HABITACION
UNION ALL
SELECT 'EMPLEADO', COUNT(*) FROM EMPLEADO
UNION ALL
SELECT 'RESERVA', COUNT(*) FROM RESERVA
UNION ALL
SELECT 'PAGO', COUNT(*) FROM PAGO
UNION ALL
SELECT 'LOG_HABITACION', COUNT(*) FROM LOG_HABITACION;
"
```

---

## 5. Restauración de la cadena incremental

Los incrementales **no son independientes**. Deben aplicarse sobre el backup base y en el orden en que fueron creados.

### 5.1 Preparar la base

```bash
mysql --login-path=bd2 -e "DROP DATABASE IF EXISTS hotel_db;"
mysql --login-path=bd2 < sql/00_create_database.sql
```

### 5.2 Restaurar el backup base

```bash
time mysql --login-path=bd2 hotel_db < backups/backup_base.sql
```

### 5.3 Aplicar incrementales en orden

```bash
time mysql --login-path=bd2 hotel_db < backups/incremental/incremental_dia1.sql
time mysql --login-path=bd2 hotel_db < backups/incremental/incremental_dia2.sql
time mysql --login-path=bd2 hotel_db < backups/incremental/incremental_dia3.sql
time mysql --login-path=bd2 hotel_db < backups/incremental/incremental_dia4.sql
time mysql --login-path=bd2 hotel_db < backups/incremental/incremental_dia5.sql
```

Después de cada incremental ejecutar la verificación de conteos.

---

## 6. Medición limpia de tiempos

Para evitar incluir el tiempo de escritura de la contraseña de MySQL:

```bash
mysql_config_editor set \
  --login-path=bd2 \
  --host=localhost \
  --user=root \
  --password
```

Verificar:

```bash
mysql --login-path=bd2 -e "SELECT VERSION();"
```

Para `sudo`, autenticar antes de iniciar `time`:

```bash
sudo -v
```

Ejemplo:

```bash
time sudo mysqlbinlog \
  --start-position=11127 \
  --stop-position=71293 \
  /var/lib/mysql/binlog.000006 \
  > /tmp/incremental_medicion.sql
```

---

## 7. Resultados finales obtenidos

### Creación

| Backup | Full (s) | Incremental (s) |
|---:|---:|---:|
| Día 1 | 0.083 | 0.025 |
| Día 2 | 0.056 | 0.029 |
| Día 3 | 0.055 | 0.017 |
| Día 4 | 0.053 | 0.016 |
| Día 5 | 0.051 | 0.016 |

### Restauración

| Backup | Full (s) | Incremental individual (s) |
|---:|---:|---:|
| Día 1 | 0.183 | 0.043 |
| Día 2 | 0.187 | 0.034 |
| Día 3 | 0.194 | 0.026 |
| Día 4 | 0.197 | 0.031 |
| Día 5 | 0.204 | 0.024 |

Backup base:

```text
Restauración = 0.127 s
```

Los resultados consolidados se encuentran en:

```text
resultados/resultados_restauracion.csv
```
