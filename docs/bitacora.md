## Actividad 1 — Creacion de la base de datos y backup base

**Resultado:** Correcto

Se creo el respaldo base de la base de datos `hotel_db`, incluyendo unicamente la estructura y sin registros de datos.

- Archivo: `backups/backup_base.sql`
- Tamanio: 8,934 bytes
- Fecha y hora: 2026-08-18 23:45:25
- Verificacion: no contiene sentencias `INSERT INTO`.

## Actividad 2 — Carga y respaldos del Dia 1

Se cargaron correctamente:

- CLIENTE: 300 registros
- HABITACION: 300 registros
- EMPLEADO: 300 registros
- Total acumulado: 900 registros

### Backup completo

- Archivo: `backups/full/full_dia1.sql`
- Tamanio: 91,964 bytes
- Fecha y hora: 2026-08-19 00:06:31
- Resultado: Correcto

### Backup incremental

- Archivo: `backups/incremental/incremental_dia1.sql`
- Binary Log origen: `binlog.000006`
- Posicion inicial: `11127`
- Posicion final: `71293`
- Tamanio: 84,326 bytes
- Fecha y hora: 2026-08-19 00:36:19
- Resultado: Correcto