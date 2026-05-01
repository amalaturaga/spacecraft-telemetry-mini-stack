# telemetry_simulator.py
import os
import time
import random
from dotenv import load_dotenv
import psycopg
from psycopg.types.json import Jsonb

load_dotenv()

pg_dsn = os.getenv("POSTGRES_DSN")
if not pg_dsn:
    raise RuntimeError("POSTGRES_DSN not set in .env")

conn = psycopg.connect(pg_dsn, autocommit=True)


def start_test_run(chamber_name, article_name, procedure_name, operator, test_level):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO test_runs
                (chamber_id, article_id, procedure_name, operator,
                 test_level, started_at, result)
            SELECT c.id, a.id, %s, %s, %s, NOW(), 'running'
            FROM chambers c, test_articles a
            WHERE c.name = %s AND a.name = %s
            RETURNING id, run_uuid, chamber_id;
        """, (procedure_name, operator, test_level, chamber_name, article_name))
        run_id, run_uuid, chamber_id = cur.fetchone()

    log_event(run_id, "phase_change", "info", f"Test started: {procedure_name}")
    print(f"Started run {run_uuid} (id={run_id})")
    return {
        "id": run_id,
        "uuid": str(run_uuid),
        "chamber_id": chamber_id,
        "chamber_name": chamber_name,
        "article_name": article_name,
    }

def log_event(run_id, event_type, severity, description, metadata=None):
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO test_events
                (time, run_id, event_type, severity, description, metadata)
            VALUES (NOW(), %s, %s, %s, %s, %s);
        """, (run_id, event_type, severity, description,
              Jsonb(metadata) if metadata else None))


def finish_test_run(run_id, result, abort_reason=None):
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE test_runs
            SET ended_at = NOW(), result = %s, abort_reason = %s
            WHERE id = %s;
        """, (result, abort_reason, run_id))
    log_event(run_id, "phase_change", "info", f"Test ended: {result}")


def write_telemetry_batch(run, phase):
    rows = [
        (run["id"], run["chamber_id"], "thermal",   "tc_01",
         random.uniform(20, 120), "C",    0, phase),
        (run["id"], run["chamber_id"], "pressure",  "pressure_main",
         random.uniform(0.8, 1.2), "Torr", 0, phase),
        (run["id"], run["chamber_id"], "vibration", "accel_x",
         random.uniform(0, 5),     "g",    0, phase),
    ]
    with conn.cursor() as cur:
        cur.executemany("""
            INSERT INTO telemetry
                (time, run_id, chamber_id, channel_type, channel_id,
                 value, unit, quality, phase)
            VALUES (NOW(), %s, %s, %s, %s, %s, %s, %s, %s);
        """, rows)


def main():
    run = start_test_run(
        chamber_name="tvac_sim",
        article_name="imager_em1",
        procedure_name="Imager TVAC Qual (sim)",
        operator="amalaturaga",
        test_level="qual",
    )

    # Short phases for fast iteration; lengthen later
    phases = [
        ("soak",       20),
        ("ramp_hot",   30),
        ("dwell_hot",  60),
        ("ramp_cold",  30),
        ("dwell_cold", 60),
    ]

    try:
        for phase_name, duration_s in phases:
            log_event(run["id"], "phase_change", "info",
                      f"Entering phase: {phase_name}")
            print(f"  Phase: {phase_name} ({duration_s}s)")
            for _ in range(duration_s):
                write_telemetry_batch(run, phase_name)
                time.sleep(1)
        finish_test_run(run["id"], "passed")
        print("Test completed: passed")
    except KeyboardInterrupt:
        finish_test_run(run["id"], "aborted", "operator interrupt (Ctrl+C)")
        print("\nAborted by user.")
    except Exception as e:
        finish_test_run(run["id"], "failed", str(e))
        raise


if __name__ == "__main__":
    main()