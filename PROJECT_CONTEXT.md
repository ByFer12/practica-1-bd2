# Contexto del proyecto — Práctica 1 BD2

## 1. Información general

**Curso:** Bases de Datos 2  
**Práctica:** Práctica 1  
**Semestre:** Segundo semestre 2026  
**SGBD obligatorio:** MySQL  
**Modalidad:** Individual  

Este archivo funciona como **memoria técnica y de avance del proyecto**. Se actualizará durante toda la práctica para conservar el contexto, las decisiones tomadas, los archivos creados, las actividades realizadas y las tareas pendientes.

---

## 2. Fuente oficial de requisitos

**Documento:** `Practica-1-BD2-1.pdf`

Requisitos principales establecidos por el documento:

- El SGBD obligatorio es MySQL.
- La práctica trata sobre una cadena hotelera.
- Deben existir las tablas:
  - CLIENTE
  - HABITACION
  - EMPLEADO
  - RESERVA
  - PAGO
  - LOG_HABITACION
- Deben elaborarse cinco archivos de carga:
  1. CLIENTE, HABITACION y EMPLEADO
  2. RESERVA
  3. Primera carga de LOG_HABITACION
  4. PAGO
  5. Segunda carga de LOG_HABITACION
- El orden de carga es obligatorio y la información es acumulativa.
- Cada archivo debe contener como mínimo 50 registros, salvo justificación.
- Después de cada etapa se deben verificar los datos, ejecutar SELECT * y SELECT COUNT(*), tomar capturas y generar backup completo e incremental.
- Antes de la primera carga debe existir un **backup base** que contenga únicamente la estructura.
- Los backups completos deben restaurarse independientemente.
- Los incrementales deben contener únicamente los cambios desde el respaldo anterior y restaurarse en orden.
- Se pueden utilizar Binary Logs de MySQL, Percona XtraBackup, MySQL Enterprise Backup u otro mecanismo técnicamente válido.
- Deben medirse tiempos, registrar tamaños y analizar los resultados.
- Debe existir una bitácora técnica.
- La entrega incluye código/scripts SQL, script de creación, archivos de carga, backups completos, backups incrementales, comandos/scripts de respaldo y restauración, capturas, bitácora, tabla comparativa, análisis, conclusiones y manual técnico.

### Nota sobre la fecha del documento

El PDF indica **19 de agosto de 2026** como fecha de entrega, pero simultáneamente lo describe como “lunes”; el 19 de agosto de 2026 es miércoles. Esta inconsistencia queda registrada y debe verificarse con la indicación oficial del curso.

La práctica también establece que “Día 1” a “Día 5” son **etapas consecutivas y no necesariamente días calendario**. Por lo tanto, no se falsificarán fechas ni horas.

---

## 3. Entorno confirmado

### Sistema operativo
- Ubuntu Linux
- x86_64

### MySQL

Comprobación realizada:

```bash
mysql --version
```

Resultado confirmado:

```text
mysql  Ver 8.0.46-0ubuntu0.24.04.3 for Linux on x86_64
```

También se comprobó correctamente el funcionamiento de las herramientas necesarias durante la Etapa 0:

- MySQL Server
- cliente `mysql`
- `mysqldump`
- `mysqlbinlog`
- Git
- DBeaver
- herramientas de Git/GitHub

### Herramientas elegidas

**DBeaver:** cliente gráfico para SQL, exploración de tablas, consultas y capturas.

**Terminal:** para administración y procesos reproducibles:
- `mysql`
- `mysqldump`
- `mysqlbinlog`
- scripts
- mediciones
- restauraciones
- Git

**Git + GitHub:** repositorio principal del proyecto.

No se utilizará MySQL Workbench salvo que el curso lo exija explícitamente.

---

## 4. Decisiones del proyecto

### Git y GitHub

El repositorio contendrá los archivos que iremos construyendo para la práctica y servirá como repositorio central del trabajo.

No se utilizará Node.js en este proyecto.

No se incluirán `node_modules/` ni `.env` porque no corresponden a este proyecto.

### Commits

Se harán múltiples commits por **hitos reales** del proyecto, no un único commit gigante.

Ejemplos de hitos:

- estructura inicial
- diseño de BD
- creación del esquema
- carga de cada etapa
- configuración de Binary Logs
- backups completos
- backups incrementales
- restauraciones
- resultados
- documentación final

No se falsificarán fechas de commits.

### Fechas y horas

No se cambiará el reloj del sistema ni se usarán variables como `GIT_AUTHOR_DATE` o `GIT_COMMITTER_DATE` para aparentar trabajo realizado en otra fecha.

Las capturas, bitácora y commits reflejarán el momento real de ejecución.

---

## 5. Estructura planificada del repositorio

```text
practica-1-bd2/
│
├── README.md
├── PROJECT_CONTEXT.md
├── .gitignore
│
├── docs/
│   ├── manual_tecnico.md
│   ├── bitacora.md
│   ├── analisis_resultados.md
│   └── conclusiones.md
│
├── sql/
│   ├── 00_create_database.sql
│   ├── 01_schema.sql
│   ├── 02_drop_database.sql
│   │
│   ├── carga/
│   │   ├── 01_carga_dia1.sql
│   │   ├── 02_carga_dia2.sql
│   │   ├── 03_carga_dia3.sql
│   │   ├── 04_carga_dia4.sql
│   │   └── 05_carga_dia5.sql
│   │
│   ├── consultas/
│   │   ├── dia1.sql
│   │   ├── dia2.sql
│   │   ├── dia3.sql
│   │   ├── dia4.sql
│   │   └── dia5.sql
│   │
│   └── backups/
│       ├── backup_base.sh
│       ├── backup_full.sh
│       ├── backup_incremental.sh
│       ├── restore_full.sh
│       └── restore_incremental.sh
│
├── backups/
│   ├── full/
│   └── incremental/
│
├── evidencia/
│   ├── dia1/
│   ├── dia2/
│   ├── dia3/
│   ├── dia4/
│   ├── dia5/
│   └── restauraciones/
│       ├── full/
│       └── incrementales/
│
├── resultados/
│   ├── tiempos.csv
│   ├── tamanos.csv
│   └── comparacion.csv
│
└── scripts/
```

Esta estructura es una propuesta de trabajo y podrá ajustarse si la implementación demuestra una organización mejor.

---

## 6. Flujo general de la práctica

```text
Preparación del entorno
        ↓
Repositorio Git/GitHub
        ↓
Diseño relacional
        ↓
Creación de BD y tablas
        ↓
Backup base (solo estructura)
        ↓
Día 1 → cargar → verificar → full → incremental
        ↓
Día 2 → cargar → verificar → full → incremental
        ↓
Día 3 → cargar → verificar → full → incremental
        ↓
Día 4 → cargar → verificar → full → incremental
        ↓
Día 5 → cargar → verificar → full → incremental
        ↓
Restaurar cada FULL independientemente
        ↓
Restaurar cadena incremental
        ↓
Medir tiempos y tamaños
        ↓
Analizar resultados
        ↓
Bitácora + Manual técnico + Conclusiones
        ↓
Revisión final + Entrega
```

---

## 7. Etapas del proyecto

### Etapa 0 — Preparación del entorno
**Estado: COMPLETADA**

Se verificaron MySQL, servidor, cliente, `mysqldump`, `mysqlbinlog`, Git, DBeaver y herramientas de Git/GitHub.

También se estableció que las fechas serán reales.

### Etapa 1 — Repositorio y organización
**Estado: SIGUIENTE / EN PROCESO**

Objetivos:
- crear/finalizar repositorio local
- crear repositorio remoto en GitHub
- conectar local y remoto
- dejar estructura inicial
- crear README
- añadir este archivo
- preparar `.gitignore`
- realizar commit inicial
- hacer primer `push`

### Etapa 2 — Diseño de la base de datos
**Estado: PENDIENTE**

Definir:
- modelo relacional
- columnas
- tipos de datos
- PK
- FK
- restricciones
- relaciones
- índices
- reglas de integridad

### Etapa 3 — Creación del esquema
**Estado: PENDIENTE**

Crear:
- base de datos
- tablas
- restricciones
- índices necesarios
- scripts reproducibles

### Etapa 4 — Datos
**Estado: PENDIENTE**

Preparar los cinco archivos de carga y validar completamente los datos.

Volumen de trabajo propuesto inicialmente:

```text
CLIENTE             300
HABITACION          300
EMPLEADO            300
RESERVA             300
LOG_HABITACION      600
PAGO                300
-------------------------
TOTAL              2100
```

Estos números son una propuesta de trabajo, no resultados finales. Todo debe validarse antes de entregarlo.

### Etapa 5 — Binary Logs
**Estado: PENDIENTE**

Estudiar y configurar Binary Logs como mecanismo propuesto para respaldos incrementales.

Documentar:
- propósito
- configuración
- archivos
- posiciones
- rotación
- lectura con `mysqlbinlog`
- identificación de cambios
- restauración de cambios

### Etapa 6 — Cargas Día 1 a Día 5
**Estado: PENDIENTE**

Orden obligatorio:

```text
Día 1: CLIENTE + HABITACION + EMPLEADO
Día 2: RESERVA
Día 3: LOG_HABITACION
Día 4: PAGO
Día 5: segunda carga de LOG_HABITACION
```

La información será acumulativa.

Después de cada etapa:

1. cargar
2. verificar
3. SELECT *
4. SELECT COUNT(*)
5. capturas
6. backup completo
7. backup incremental
8. bitácora

### Etapa 7 — Backups completos
**Estado: PENDIENTE**

Generar:

```text
backup_base
full_dia1
full_dia2
full_dia3
full_dia4
full_dia5
```

### Etapa 8 — Backups incrementales
**Estado: PENDIENTE**

Generar:

```text
incremental_dia1
incremental_dia2
incremental_dia3
incremental_dia4
incremental_dia5
```

Deben representar cambios y permitir una restauración correcta en cadena.

### Etapa 9 — Restauraciones completas
**Estado: PENDIENTE**

Probar cada `full_diaN` de forma independiente, midiendo tiempo y verificando datos.

### Etapa 10 — Restauración incremental
**Estado: PENDIENTE**

Restaurar:

```text
backup_base
↓
incremental_dia1
↓
incremental_dia2
↓
incremental_dia3
↓
incremental_dia4
↓
incremental_dia5
```

Verificar después de cada aplicación.

### Etapa 11 — Resultados
**Estado: PENDIENTE**

Comparar:
- tamaño
- tiempo de creación
- tiempo de restauración
- complejidad
- dependencia
- ventajas
- desventajas
- recomendación

### Etapa 12 — Entrega
**Estado: PENDIENTE**

Finalizar:
- bitácora
- manual técnico
- resultados
- análisis
- conclusiones
- README
- revisión del repositorio
- paquete de entrega si corresponde

---

## 8. Estado actual

**Fecha de actualización:** 18 de agosto de 2026

### Completado

- [x] Leer y analizar la práctica
- [x] Confirmar MySQL 8.0.46
- [x] Confirmar herramientas necesarias
- [x] Elegir DBeaver + terminal
- [x] Decidir usar Git + GitHub
- [x] Definir commits por hitos reales
- [x] Definir estrategia para fechas reales
- [x] Definir estructura general
- [x] Crear este archivo de contexto

### En curso

- [x] Crear/finalizar repositorio GitHub
- [x] Añadir este archivo al repositorio
- [x] Primer commit
- [x] Primer push
- [x] Confirmar estado local/remoto

### Pendiente

- [ ] Diseñar modelo relacional
- [ ] Crear esquema SQL
- [ ] Validar estructura
- [ ] Preparar cinco archivos de carga
- [ ] Generar y validar datos
- [ ] Configurar Binary Logs
- [ ] Ejecutar Día 1
- [ ] Ejecutar Día 2
- [ ] Ejecutar Día 3
- [ ] Ejecutar Día 4
- [ ] Ejecutar Día 5
- [ ] Generar full backups
- [ ] Generar incrementales
- [ ] Medir tiempos
- [ ] Medir tamaños
- [ ] Restaurar full backups
- [ ] Restaurar incrementales
- [ ] Capturar evidencias
- [ ] Completar bitácora
- [ ] Completar manual técnico
- [ ] Completar análisis
- [ ] Completar conclusiones
- [ ] Revisar entrega final

---

## 9. Registro de decisiones importantes

### DBeaver
Se utilizará como cliente gráfico principal.

### Terminal
Se utilizará para administración, backups, restauraciones, Binary Logs, medición y automatización.

### GitHub
Será el repositorio central del proyecto.

### Fechas
No se cambiarán manualmente las fechas del sistema ni de Git.

### Commits
Se crearán commits por hitos reales.

### Incrementales
El mecanismo propuesto inicialmente son los Binary Logs de MySQL; se validará técnicamente antes de usarlo como solución final.

### Datos
Se usarán más datos que el mínimo requerido, pero siempre con revisión de coherencia, PK, FK y carga real.

---

## 10. Regla de actualización de este archivo

Cada vez que terminemos una etapa importante, actualizar este archivo con:

1. fecha y hora real
2. etapa terminada
3. comandos principales
4. archivos creados/modificados
5. resultados obtenidos
6. problemas y solución
7. evidencia generada
8. commit realizado
9. siguiente etapa
10. tareas pendientes

Este archivo debe permitir responder:

> ¿Qué hemos hecho?

> ¿Cómo lo hicimos?

> ¿Por qué lo hicimos así?

> ¿Qué archivos existen?

> ¿Qué falta?

> ¿Cuál es el estado actual?

> ¿Cuál es el siguiente paso?

---

## 11. Nota final

Este archivo es una **memoria viva del proyecto**. No sustituye al manual técnico final.

El manual técnico será redactado posteriormente con una presentación académica y técnica formal, basándose en los resultados reales obtenidos durante la ejecución.

No se deben inventar:
- tiempos
- tamaños
- resultados
- capturas
- registros
- estados de restauración

Todo resultado final deberá provenir de una ejecución real y verificable.
