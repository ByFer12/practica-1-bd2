# Administrador de Backups — Aplicación de consola

Aplicación demostrativa para ejecutar y explicar el flujo principal de la Práctica 1 de Bases de Datos 2.

## Requisitos

- Python 3.10 o superior.
- MySQL 8.
- `mysql`, `mysqldump` y `mysqlbinlog` disponibles en `PATH`.
- `sudo` disponible para leer `/var/lib/mysql/binlog.*`.
- Repositorio con la estructura original de la práctica.

No requiere librerías externas de Python.

## Configuración de MySQL

La aplicación utiliza el login-path `bd2`, por lo que primero debe configurarse una vez:

```bash
mysql_config_editor set \
  --login-path=bd2 \
  --host=localhost \
  --user=root \
  --password
```

Comprobar:

```bash
mysql --login-path=bd2 -e "SELECT VERSION();"
```

## Ejecución

Desde la raíz del proyecto:

```bash
python3 scripts/backup_manager.py
```

Opcionalmente:

```bash
chmod +x scripts/backup_manager.py
./scripts/backup_manager.py
```

## Menú

```text
1. Ver estado general
2. Preparar práctica desde cero
3. Ejecutar siguiente día completo
4. Verificar conteos de la base
5. Restaurar un backup completo
6. Restaurar cadena incremental
7. Listar backups disponibles
8. Reiniciar estado interno de la aplicación
0. Salir
```

## Flujo demostrativo recomendado

### 1. Preparar desde cero

La opción 2:

- elimina `hotel_db`;
- crea la base;
- crea el esquema;
- genera `backups/backup_base.sql`;
- verifica que todas las tablas estén vacías;
- registra la posición inicial del Binary Log.

### 2. Ejecutar las etapas

Cada vez que se utiliza la opción 3, la aplicación ejecuta únicamente el siguiente día permitido.

Ejemplo:

```text
Día 1
→ valida que la base esté vacía
→ registra posición inicial
→ ejecuta 01_carga_dia1.sql
→ valida los conteos
→ registra posición final
→ genera full_dia1.sql
→ genera incremental_dia1.sql
→ guarda el estado
```

La siguiente ejecución avanza al Día 2, luego al Día 3 y así sucesivamente.

La aplicación impide avanzar si los conteos actuales no coinciden con el estado esperado de la etapa anterior.

## Protección de backups existentes

Si un backup ya existe, la aplicación pregunta antes de sobrescribirlo.

```text
[AVISO] El archivo ya existe...
¿Deseas sobrescribirlo? [s/N]:
```

La respuesta predeterminada es `No`.

## Restauraciones

### Full

La opción 5 comprueba primero que exista el archivo solicitado.

Luego:

```text
DROP hotel_db
→ crear hotel_db
→ restaurar full_diaN.sql
→ verificar conteos esperados
```

### Incremental

La opción 6 comprueba que existan:

- `backup_base.sql`;
- todos los incrementales requeridos hasta el día seleccionado.

Luego:

```text
DROP hotel_db
→ crear hotel_db
→ restaurar backup_base.sql
→ incremental_dia1.sql
→ incremental_dia2.sql
→ ...
→ verificar después de cada paso
```

Si falta un archivo intermedio, la restauración no inicia.


## Archivo de estado

La aplicación crea:

```text
scripts/.backup_manager_state.json
```

Solo contiene información técnica del flujo, por ejemplo:

- último día ejecutado;
- Binary Log;
- posición inicial para la siguiente etapa.

No contiene contraseñas.

Puede agregarse al `.gitignore`:

```gitignore
scripts/.backup_manager_state.json
```

La opción 8 elimina únicamente este estado interno; no elimina la base de datos ni los backups.

## Nota sobre Binary Logs

La generación automática de incrementales asume que el inicio y fin de una etapa permanecen dentro del mismo archivo de Binary Log.

Si MySQL rota el Binary Log durante una carga, la aplicación detiene la creación automática del incremental e informa el problema para evitar producir un respaldo incompleto.

## Eliminar backups generados

La opción 9 permite eliminar únicamente los archivos de respaldo generados durante la práctica:

```text
backups/backup_base.sql
backups/full/full_dia1.sql ... full_dia5.sql
backups/incremental/incremental_dia1.sql ... incremental_dia5.sql
