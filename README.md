# Práctica 1 — Bases de Datos 2
## Respaldos y Recuperación en MySQL

Práctica desarrollada para implementar una base de datos relacional de una cadena hotelera y demostrar procesos de carga, respaldo completo, respaldo incremental y recuperación de información mediante MySQL.

---

## Índice del proyecto

- [Backups](#backups)
- [Documentación](#documentación)
- [Evidencias](#evidencias)
- [Resultados](#resultados)
- [Aplicación de consola](#aplicación-de-consola)
- [Scripts SQL](#scripts-sql)
- [Flujo general](#flujo-general)
- [Verificación](#verificación)

---

## Backups

📁 [`backups/`](backups/)

Contiene todos los respaldos generados durante la práctica.

- [`backup_base.sql`](backups/backup_base.sql)  
  Respaldo únicamente de la estructura de la base de datos.

- [`backups/full/`](backups/full/)  
  Contiene los cinco backups completos:
  - `full_dia1.sql`
  - `full_dia2.sql`
  - `full_dia3.sql`
  - `full_dia4.sql`
  - `full_dia5.sql`

- [`backups/incremental/`](backups/incremental/)  
  Contiene los cinco respaldos incrementales generados mediante Binary Logs.

---

## Documentación

📁 [`docs/`](docs/)

Contiene la documentación técnica de la práctica.

- [`bitacora.pdf`](docs/bitacora.pdf)  
  Registro de las actividades realizadas, comandos utilizados, tiempos y resultados.

- [`manual_tecnico.pdf`](docs/Manual_Tecnico.pdf)  
  Describe el diseño de la base de datos, implementación, backups, restauraciones, análisis y conclusiones.

Las carpetas internas de capturas utilizadas en la documentación se encuentran también dentro de `docs/`.

---

## Evidencias

📁 [`evidencia/`](evidencia/)

Contiene las capturas utilizadas para demostrar las cargas y restauraciones realizadas.

### Evidencias de carga

- [`evidencia/dia1/`](evidencia/dia1/dia1_resumen.png)
- [`evidencia/dia2/`](evidencia/dia2/dia2_resumen.png)
- [`evidencia/dia3/`](evidencia/dia3/dia3_resumen.png)
- [`evidencia/dia4/`](evidencia/dia4/dia4_resumen.png)
- [`evidencia/dia5/`](evidencia/dia5/dia5_resumen.png)

### Evidencias de backup

- [`evidencia/dia1/`](evidencia/dia1/)
- [`evidencia/dia2/`](evidencia/dia2/)
- [`evidencia/dia3/`](evidencia/dia3/)
- [`evidencia/dia4/`](evidencia/dia4/)
- [`evidencia/dia5/`](evidencia/dia5/)

### Evidencias de restauración

- [`evidencia/restauraciones/full/`](evidencia/restauraciones/full/)  
  Restauraciones independientes de los backups completos.

- [`evidencia/restauraciones/incrementales/`](evidencia/restauraciones/incrementales/)  
  Restauración acumulativa desde el backup base y los incrementales.

---

## Resultados

📁 [`resultados/`](resultados/)

Contiene los resultados medidos durante la práctica.

- [`resultados_restauracion.csv`](resultados/resultados_restauracion.csv)  
  Tamaños, tiempos de creación, tiempos de restauración y resultado de cada backup.

- [`tamanos.csv`](resultados/tamanos.csv)  
  Registro de tamaños y fechas de generación de los respaldos.

---

## Aplicación de consola

📁 [`scripts/`](scripts/)

La aplicación:

[`scripts/backup_manager.py`](scripts/backup_manager.py)

permite ejecutar de forma guiada las operaciones principales de la práctica.

Funciones principales:

- preparar la base de datos desde cero;
- generar el backup base;
- ejecutar las cargas del Día 1 al Día 5;
- validar que las cargas se realicen en el orden correcto;
- generar backups completos;
- generar backups incrementales;
- consultar el estado actual;
- restaurar un backup completo;
- restaurar la cadena incremental;
- listar backups disponibles;
- eliminar backups para repetir la práctica.

Ejecución:

```bash
python3 scripts/backup_manager.py
