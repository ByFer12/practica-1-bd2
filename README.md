## Flujo de la práctica

La práctica implementa una base de datos hotelera en MySQL y demuestra el proceso completo de respaldo y recuperación mediante:

- 5 etapas de carga de datos.
- Backups completos por cada etapa.
- Backups incrementales utilizando Binary Logs.
- Restauración independiente de backups completos.
- Restauración acumulativa desde backup base + incrementales.
- Verificación mediante consultas y conteos.
- Registro de tiempos, tamaños y evidencias.

También se incluye una aplicación de consola en Python para ejecutar y demostrar el flujo principal de la práctica:

```bash
python3 scripts/backup_manager.py

## Estructura principal

```text
backups/
├── backup_base.sql
├── full/
└── incremental/

docs/
├── bitacora.md
└── manual_tecnico.md

evidencia/
├── dia1 ... dia5
└── restauraciones/
    ├── full/
    └── incrementales/

resultados/
├── tamanos.csv
└── resultados_restauracion.csv

scripts/
└── backup_manager.py

sql/
├── 00_create_database.sql
├── 01_schema.sql
├── 02_drop_database.sql
├── backups/
├── carga/
└── consultas/