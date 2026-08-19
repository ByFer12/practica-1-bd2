#!/usr/bin/env python3
"""
Administrador de Backups - Práctica 1 BD2

Aplicación de consola para demostrar:
- preparación de la base;
- cargas secuenciales Día 1 -> Día 5;
- creación de backups full e incrementales;
- verificación de registros;
- restauración full;
- restauración de la cadena incremental.

No guarda contraseñas. Utiliza el login-path de MySQL configurado como "bd2".
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Tuple

ROOT = Path(__file__).resolve().parent.parent
STATE_FILE = ROOT / "scripts" / ".backup_manager_state.json"

DB = "hotel_db"
LOGIN_PATH = "bd2"

CREATE_DB = ROOT / "sql" / "00_create_database.sql"
SCHEMA = ROOT / "sql" / "01_schema.sql"
VERIFY_SQL = ROOT / "sql" / "consultas" / "verificacion_completa.sql"

BACKUP_BASE = ROOT / "backups" / "backup_base.sql"
FULL_DIR = ROOT / "backups" / "full"
INC_DIR = ROOT / "backups" / "incremental"

LOAD_FILES = {
    1: ROOT / "sql" / "carga" / "01_carga_dia1.sql",
    2: ROOT / "sql" / "carga" / "02_carga_dia2.sql",
    3: ROOT / "sql" / "carga" / "03_carga_dia3.sql",
    4: ROOT / "sql" / "carga" / "04_carga_dia4.sql",
    5: ROOT / "sql" / "carga" / "05_carga_dia5.sql",
}

EXPECTED = {
    0: {
        "CLIENTE": 0, "HABITACION": 0, "EMPLEADO": 0,
        "RESERVA": 0, "PAGO": 0, "LOG_HABITACION": 0,
    },
    1: {
        "CLIENTE": 300, "HABITACION": 300, "EMPLEADO": 300,
        "RESERVA": 0, "PAGO": 0, "LOG_HABITACION": 0,
    },
    2: {
        "CLIENTE": 300, "HABITACION": 300, "EMPLEADO": 300,
        "RESERVA": 300, "PAGO": 0, "LOG_HABITACION": 0,
    },
    3: {
        "CLIENTE": 300, "HABITACION": 300, "EMPLEADO": 300,
        "RESERVA": 300, "PAGO": 0, "LOG_HABITACION": 300,
    },
    4: {
        "CLIENTE": 300, "HABITACION": 300, "EMPLEADO": 300,
        "RESERVA": 300, "PAGO": 300, "LOG_HABITACION": 300,
    },
    5: {
        "CLIENTE": 300, "HABITACION": 300, "EMPLEADO": 300,
        "RESERVA": 300, "PAGO": 300, "LOG_HABITACION": 600,
    },
}

# ANSI simple. No external dependency required.
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
CYAN = "\033[36m"
DIM = "\033[2m"


def c(text: str, color: str) -> str:
    return f"{color}{text}{RESET}" if sys.stdout.isatty() else text


def title(text: str) -> None:
    print("\n" + c("=" * 68, CYAN))
    print(c(f"  {text}", BOLD))
    print(c("=" * 68, CYAN))


def ok(text: str) -> None:
    print(c(f"[OK] {text}", GREEN))


def warn(text: str) -> None:
    print(c(f"[AVISO] {text}", YELLOW))


def error(text: str) -> None:
    print(c(f"[ERROR] {text}", RED))


def info(text: str) -> None:
    print(c(f"[INFO] {text}", CYAN))


def pause() -> None:
    input("\nPresiona Enter para continuar...")


def confirm(question: str) -> bool:
    return input(f"{question} [s/N]: ").strip().lower() in {"s", "si", "sí", "y", "yes"}


def run(
    args,
    *,
    stdin_path: Path | None = None,
    stdout_path: Path | None = None,
    capture: bool = False,
    check: bool = True,
) -> subprocess.CompletedProcess:
    stdin_f = open(stdin_path, "rb") if stdin_path else None
    stdout_f = open(stdout_path, "wb") if stdout_path else None
    try:
        return subprocess.run(
            args,
            cwd=ROOT,
            stdin=stdin_f,
            stdout=subprocess.PIPE if capture else stdout_f,
            stderr=subprocess.PIPE if capture else None,
            text=capture,
            check=check,
        )
    finally:
        if stdin_f:
            stdin_f.close()
        if stdout_f:
            stdout_f.close()


def timed_run(args, *, stdin_path: Path | None = None, stdout_path: Path | None = None) -> float:
    start = time.perf_counter()
    run(args, stdin_path=stdin_path, stdout_path=stdout_path)
    return time.perf_counter() - start


def mysql_args(*extra: str):
    return ["mysql", f"--login-path={LOGIN_PATH}", *extra]


def ensure_tools() -> bool:
    required = ["mysql", "mysqldump", "mysqlbinlog", "sudo"]
    missing = [cmd for cmd in required if shutil.which(cmd) is None]
    if missing:
        error("Faltan comandos requeridos: " + ", ".join(missing))
        return False

    try:
        run(mysql_args("-e", "SELECT 1;"), capture=True)
    except subprocess.CalledProcessError as exc:
        error(f"No se pudo utilizar el login-path '{LOGIN_PATH}'.")
        print("Configúralo con:")
        print(f"mysql_config_editor set --login-path={LOGIN_PATH} --host=localhost --user=root --password")
        if exc.stderr:
            print(exc.stderr.strip())
        return False

    return True


def required_files_ok() -> bool:
    files = [CREATE_DB, SCHEMA, VERIFY_SQL, *LOAD_FILES.values()]
    missing = [p.relative_to(ROOT) for p in files if not p.exists()]
    if missing:
        error("Faltan archivos del proyecto:")
        for p in missing:
            print(f"  - {p}")
        return False
    return True


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {
            "initialized": False,
            "last_completed_day": 0,
            "binlog_file": None,
            "next_start_position": None,
        }
    try:
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        warn("El archivo de estado está dañado. Se usará un estado vacío.")
        return {
            "initialized": False,
            "last_completed_day": 0,
            "binlog_file": None,
            "next_start_position": None,
        }


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2), encoding="utf-8")


def master_status() -> Tuple[str, int]:
    cp = run(
        mysql_args("--batch", "--skip-column-names", "-e", "SHOW MASTER STATUS;"),
        capture=True,
    )
    line = cp.stdout.strip().splitlines()
    if not line:
        raise RuntimeError("SHOW MASTER STATUS no devolvió información. ¿Está habilitado log_bin?")
    parts = line[0].split("\t")
    return parts[0], int(parts[1])


def counts() -> Dict[str, int]:
    query = """
SELECT 'CLIENTE', COUNT(*) FROM CLIENTE
UNION ALL SELECT 'HABITACION', COUNT(*) FROM HABITACION
UNION ALL SELECT 'EMPLEADO', COUNT(*) FROM EMPLEADO
UNION ALL SELECT 'RESERVA', COUNT(*) FROM RESERVA
UNION ALL SELECT 'PAGO', COUNT(*) FROM PAGO
UNION ALL SELECT 'LOG_HABITACION', COUNT(*) FROM LOG_HABITACION;
"""
    cp = run(
        mysql_args("--batch", "--skip-column-names", DB, "-e", query),
        capture=True,
    )
    result = {}
    for line in cp.stdout.strip().splitlines():
        name, value = line.split("\t")
        result[name] = int(value)
    return result


def print_counts(actual: Dict[str, int], expected_day: int | None = None) -> bool:
    expected = EXPECTED.get(expected_day) if expected_day is not None else None
    print(f"\n{'TABLA':<18} {'REGISTROS':>10} {'ESTADO':>12}")
    print("-" * 42)
    valid = True
    for table in ["CLIENTE", "HABITACION", "EMPLEADO", "RESERVA", "PAGO", "LOG_HABITACION"]:
        value = actual.get(table, -1)
        if expected is None:
            status = "-"
        else:
            is_ok = value == expected[table]
            valid &= is_ok
            status = c("OK", GREEN) if is_ok else c(f"Esperado {expected[table]}", RED)
        print(f"{table:<18} {value:>10} {status:>20}")
    return valid


def database_exists() -> bool:
    cp = run(
        mysql_args("--batch", "--skip-column-names", "-e",
                   f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{DB}';"),
        capture=True,
    )
    return cp.stdout.strip() == DB


def overwrite_allowed(path: Path) -> bool:
    if not path.exists():
        return True
    warn(f"El archivo ya existe: {path.relative_to(ROOT)}")
    return confirm("¿Deseas sobrescribirlo?")


def prepare_from_zero() -> None:
    title("Preparar práctica desde cero")
    warn("Este proceso ELIMINA hotel_db, crea nuevamente el esquema y genera backup_base.sql.")
    if not confirm("¿Continuar?"):
        return

    run(mysql_args("-e", f"DROP DATABASE IF EXISTS {DB};"))
    run(mysql_args(), stdin_path=CREATE_DB)
    run(mysql_args(), stdin_path=SCHEMA)
    ok("Base de datos y esquema creados.")

    if BACKUP_BASE.exists() and not overwrite_allowed(BACKUP_BASE):
        warn("No se reemplazó backup_base.sql.")
    else:
        elapsed = timed_run(
            ["mysqldump", f"--login-path={LOGIN_PATH}", "--no-data",
             "--routines", "--triggers", DB],
            stdout_path=BACKUP_BASE,
        )
        ok(f"Backup base creado en {elapsed:.3f} s: {BACKUP_BASE.relative_to(ROOT)}")

    actual = counts()
    if not print_counts(actual, 0):
        error("La base no está vacía. Se detiene la preparación.")
        return

    binlog_file, pos = master_status()
    state = {
        "initialized": True,
        "last_completed_day": 0,
        "binlog_file": binlog_file,
        "next_start_position": pos,
    }
    save_state(state)
    ok(f"Punto inicial registrado: {binlog_file} posición {pos}")
    info("Ahora puedes ejecutar la opción 'Ejecutar siguiente día completo'.")


def execute_next_day() -> None:
    title("Ejecutar siguiente etapa completa")
    state = load_state()
    if not state.get("initialized"):
        error("La práctica no está inicializada desde la aplicación.")
        print("Usa primero la opción 2: Preparar práctica desde cero.")
        return

    day = int(state.get("last_completed_day", 0)) + 1
    if day > 5:
        ok("Los cinco días ya fueron completados.")
        return

    if not database_exists():
        error(f"La base {DB} no existe.")
        return

    actual_before = counts()
    if not print_counts(actual_before, day - 1):
        error(
            f"El estado actual de la BD no corresponde al final del Día {day-1}. "
            "No se ejecutará la siguiente carga para evitar inconsistencias."
        )
        return

    load_file = LOAD_FILES[day]
    full_path = FULL_DIR / f"full_dia{day}.sql"
    inc_path = INC_DIR / f"incremental_dia{day}.sql"

    print(f"\nDía {day}")
    print(f"  Carga:       {load_file.relative_to(ROOT)}")
    print(f"  Full:        {full_path.relative_to(ROOT)}")
    print(f"  Incremental: {inc_path.relative_to(ROOT)}")
    if not confirm("¿Ejecutar esta etapa?"):
        return

    binlog_before, start_pos = master_status()
    info(f"Inicio Binary Log: {binlog_before} posición {start_pos}")

    load_elapsed = timed_run(mysql_args(), stdin_path=load_file)
    ok(f"Carga del Día {day} finalizada en {load_elapsed:.3f} s.")

    actual_after = counts()
    if not print_counts(actual_after, day):
        error("Los conteos no coinciden con el estado esperado. NO se crearán backups.")
        return

    binlog_after, end_pos = master_status()
    info(f"Fin Binary Log: {binlog_after} posición {end_pos}")

    if binlog_before != binlog_after:
        error(
            "El Binary Log cambió de archivo durante la etapa. "
            "Esta versión demostrativa no concatena múltiples binlogs automáticamente."
        )
        print("Genera el incremental manualmente o ajusta la rotación antes de repetir.")
        return

    FULL_DIR.mkdir(parents=True, exist_ok=True)
    INC_DIR.mkdir(parents=True, exist_ok=True)

    if overwrite_allowed(full_path):
        full_elapsed = timed_run(
            ["mysqldump", f"--login-path={LOGIN_PATH}", "--single-transaction",
             "--routines", "--triggers", DB],
            stdout_path=full_path,
        )
        ok(f"Full Día {day} creado en {full_elapsed:.3f} s.")
    else:
        warn("Se conservó el full existente.")

    if overwrite_allowed(inc_path):
        info("Validando sudo antes de medir mysqlbinlog...")
        run(["sudo", "-v"])
        inc_elapsed = timed_run(
            ["sudo", "mysqlbinlog",
             f"--start-position={start_pos}",
             f"--stop-position={end_pos}",
             f"/var/lib/mysql/{binlog_after}"],
            stdout_path=inc_path,
        )
        ok(f"Incremental Día {day} creado en {inc_elapsed:.3f} s.")
    else:
        warn("Se conservó el incremental existente.")

    state.update({
        "initialized": True,
        "last_completed_day": day,
        "binlog_file": binlog_after,
        "next_start_position": end_pos,
    })
    save_state(state)

    print("\nResumen:")
    print(f"  Día completado: {day}")
    print(f"  Rango binlog:   {binlog_after} {start_pos} -> {end_pos}")
    if full_path.exists():
        print(f"  Full:           {full_path.stat().st_size:,} bytes")
    if inc_path.exists():
        print(f"  Incremental:    {inc_path.stat().st_size:,} bytes")
    ok(f"Etapa Día {day} completada.")


def verify_database() -> None:
    title("Verificación de la base")
    if not database_exists():
        error(f"La base {DB} no existe.")
        return
    actual = counts()
    print_counts(actual)
    state = load_state()
    expected_day = state.get("last_completed_day")
    if state.get("initialized") and expected_day in EXPECTED:
        print(f"\nComparación con estado registrado de Día {expected_day}:")
        if print_counts(actual, expected_day):
            ok("Los conteos coinciden con el estado registrado.")
        else:
            warn("La BD fue modificada/restaurada y ya no coincide con el estado persistido.")


def restore_full() -> None:
    title("Restaurar backup completo")
    raw = input("Día a restaurar [1-5]: ").strip()
    if raw not in {"1", "2", "3", "4", "5"}:
        error("Día inválido.")
        return
    day = int(raw)
    path = FULL_DIR / f"full_dia{day}.sql"

    if not path.exists():
        error(f"No existe {path.relative_to(ROOT)}. No se puede restaurar.")
        return

    warn(f"Se eliminará {DB} y se restaurará full_dia{day}.sql.")
    if not confirm("¿Continuar?"):
        return

    run(mysql_args("-e", f"DROP DATABASE IF EXISTS {DB};"))
    run(mysql_args(), stdin_path=CREATE_DB)
    elapsed = timed_run(mysql_args(DB), stdin_path=path)
    ok(f"Restauración Full Día {day}: {elapsed:.3f} s")

    actual = counts()
    if print_counts(actual, day):
        ok(f"Full Día {day} validado correctamente.")
    else:
        error("La restauración terminó, pero los conteos no coinciden.")


def restore_incremental_chain() -> None:
    title("Restaurar cadena incremental")
    raw = input("Reconstruir hasta el Día [1-5]: ").strip()
    if raw not in {"1", "2", "3", "4", "5"}:
        error("Día inválido.")
        return
    target = int(raw)

    needed = [BACKUP_BASE] + [INC_DIR / f"incremental_dia{i}.sql" for i in range(1, target + 1)]
    missing = [p.relative_to(ROOT) for p in needed if not p.exists()]
    if missing:
        error("No se puede restaurar. Faltan archivos:")
        for p in missing:
            print(f"  - {p}")
        return

    warn(f"Se eliminará {DB} y se reconstruirá hasta el Día {target}.")
    if not confirm("¿Continuar?"):
        return

    run(mysql_args("-e", f"DROP DATABASE IF EXISTS {DB};"))
    run(mysql_args(), stdin_path=CREATE_DB)

    base_elapsed = timed_run(mysql_args(DB), stdin_path=BACKUP_BASE)
    ok(f"Backup base restaurado en {base_elapsed:.3f} s.")

    base_counts = counts()
    if not print_counts(base_counts, 0):
        error("El backup base no dejó la estructura vacía esperada.")
        return

    total = base_elapsed
    for day in range(1, target + 1):
        path = INC_DIR / f"incremental_dia{day}.sql"
        elapsed = timed_run(mysql_args(DB), stdin_path=path)
        total += elapsed
        ok(f"Incremental Día {day} aplicado en {elapsed:.3f} s.")
        actual = counts()
        if not print_counts(actual, day):
            error(f"Fallo de validación después del incremental Día {day}.")
            return

    ok(f"Cadena incremental restaurada hasta Día {target}. Tiempo acumulado: {total:.3f} s.")


def show_backups() -> None:
    title("Backups disponibles")
    rows = []
    if BACKUP_BASE.exists():
        rows.append(("backup_base", "Base", BACKUP_BASE))
    for day in range(1, 6):
        fp = FULL_DIR / f"full_dia{day}.sql"
        ip = INC_DIR / f"incremental_dia{day}.sql"
        if fp.exists():
            rows.append((f"full_dia{day}", "Completo", fp))
        if ip.exists():
            rows.append((f"incremental_dia{day}", "Incremental", ip))

    if not rows:
        warn("No hay backups disponibles.")
        return

    print(f"{'NOMBRE':<24} {'TIPO':<14} {'TAMAÑO':>12}")
    print("-" * 54)
    for name, kind, path in rows:
        print(f"{name:<24} {kind:<14} {path.stat().st_size:>12,} B")


def show_status() -> None:
    title("Estado de la práctica")
    state = load_state()
    print(f"Raíz del proyecto: {ROOT}")
    print(f"Login path:         {LOGIN_PATH}")
    print(f"Inicializada app:   {'Sí' if state.get('initialized') else 'No'}")
    print(f"Último día app:     {state.get('last_completed_day', 0)}")
    print(f"BD existente:       {'Sí' if database_exists() else 'No'}")

    try:
        file, pos = master_status()
        print(f"Binary Log actual:  {file} @ {pos}")
    except Exception as exc:
        warn(f"No se pudo consultar Binary Log: {exc}")

    if database_exists():
        try:
            actual = counts()
            print_counts(actual)
        except subprocess.CalledProcessError:
            warn("La base existe, pero el esquema requerido no está completo.")

    print("\nBackups:")
    for p in [BACKUP_BASE] + [
        x for d in range(1, 6)
        for x in (FULL_DIR / f"full_dia{d}.sql", INC_DIR / f"incremental_dia{d}.sql")
    ]:
        marker = c("OK", GREEN) if p.exists() else c("FALTA", RED)
        print(f"  [{marker}] {p.relative_to(ROOT)}")


def reset_app_state() -> None:
    title("Reiniciar estado interno")
    warn("Esto NO elimina la base ni los backups. Solo elimina el estado interno de la aplicación.")
    if confirm("¿Reiniciar el estado?"):
        if STATE_FILE.exists():
            STATE_FILE.unlink()
        ok("Estado interno reiniciado.")

def delete_backups() -> None:
    title("Eliminar backups generados")

    warn("Esta opción eliminará:")
    print("  - backups/backup_base.sql")
    print("  - backups/full/full_dia1.sql ... full_dia5.sql")
    print("  - backups/incremental/incremental_dia1.sql ... incremental_dia5.sql")

    print()
    warn("NO elimina:")
    print("  - scripts SQL")
    print("  - cargas")
    print("  - documentación")
    print("  - evidencias")
    print("  - resultados")

    confirmation = input(
        '\nEscribe exactamente "ELIMINAR BACKUPS" para continuar: '
    ).strip()

    if confirmation != "ELIMINAR BACKUPS":
        warn("Operación cancelada.")
        return

    deleted = 0

    paths = [BACKUP_BASE]

    for day in range(1, 6):
        paths.append(FULL_DIR / f"full_dia{day}.sql")
        paths.append(INC_DIR / f"incremental_dia{day}.sql")

    for path in paths:
        if path.exists():
            path.unlink()
            print(f"Eliminado: {path.relative_to(ROOT)}")
            deleted += 1

    # Reiniciar también el estado interno de la app,
    # porque ya no existe la cadena de backups anterior.
    if STATE_FILE.exists():
        STATE_FILE.unlink()

    if deleted == 0:
        warn("No había backups para eliminar.")
    else:
        ok(f"Se eliminaron {deleted} archivos de backup.")
        info("El estado interno de la aplicación fue reiniciado.")
        info("Puedes comenzar nuevamente con la opción 2.")

def menu() -> None:
    while True:
        title("ADMINISTRADOR DE BACKUPS — PRÁCTICA 1 BD2")
        print("1. Ver estado general")
        print("2. Preparar práctica desde cero")
        print("3. Ejecutar siguiente día completo")
        print("4. Verificar conteos de la base")
        print("5. Restaurar un backup completo")
        print("6. Restaurar cadena incremental")
        print("7. Listar backups disponibles")
        print("8. Reiniciar estado interno de la aplicación")
        print("9. Eliminar backups generados")
        print("0. Salir")

        option = input("\nSelecciona una opción: ").strip()

        actions = {
            "1": show_status,
            "2": prepare_from_zero,
            "3": execute_next_day,
            "4": verify_database,
            "5": restore_full,
            "6": restore_incremental_chain,
            "7": show_backups,
            "8": reset_app_state,
            "9": delete_backups,
        }

        if option == "0":
            print("Hasta luego.")
            return

        action = actions.get(option)
        if not action:
            error("Opción inválida.")
            pause()
            continue

        try:
            action()
        except subprocess.CalledProcessError as exc:
            error(f"Un comando terminó con código {exc.returncode}.")
            if exc.stderr:
                print(exc.stderr.strip())
        except KeyboardInterrupt:
            print()
            warn("Operación cancelada por el usuario.")
        except Exception as exc:
            error(str(exc))

        pause()


def main() -> int:
    os.chdir(ROOT)

    if not ensure_tools():
        return 1
    if not required_files_ok():
        return 1

    FULL_DIR.mkdir(parents=True, exist_ok=True)
    INC_DIR.mkdir(parents=True, exist_ok=True)

    menu()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
