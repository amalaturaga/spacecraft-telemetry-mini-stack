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

# ---------------------------------------------------------------------------
# Thermal-curve constants for the simulated TVAC cycle.
# Ranges chosen to mimic a typical commercial-space qualification test:
# -40 C cold soak, +85 C hot soak.
# ---------------------------------------------------------------------------
T_AMBIENT = 20.0   # C, soak phase
T_HOT     = 85.0   # C, dwell_hot phase
T_COLD    = -40.0  # C, dwell_cold phase

# Realistic vacuum chamber operating pressure (~1e-4 Torr range).
# We don't model pumpdown in this demo; pressure sits at vacuum throughout.
P_BASE = 1.0e-4  # Torr

# Vibration baseline from chamber pumps / compressors.
ACCEL_BASE = 0.2  # g


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


# ---------------------------------------------------------------------------
# Curve generators per channel.
# Each takes (phase_name, progress_fraction) where progress_fraction is 0..1
# and returns a single sample value.
# ---------------------------------------------------------------------------

def temperature_value(phase, progress):
    """
    Temperature curve in C. The dominant channel for visual storytelling.
    Phase-driven trend + small Gaussian sensor noise.
    """
    if phase == "soak":
        trend = T_AMBIENT
    elif phase == "ramp_hot":
        # Linear ramp from ambient to hot
        trend = T_AMBIENT + (T_HOT - T_AMBIENT) * progress
    elif phase == "dwell_hot":
        trend = T_HOT
    elif phase == "ramp_cold":
        # Linear ramp from hot to cold
        trend = T_HOT + (T_COLD - T_HOT) * progress
    elif phase == "dwell_cold":
        trend = T_COLD
    else:
        trend = T_AMBIENT

    noise = random.gauss(0, 1.2)  # +/- ~1.2 C sensor noise
    return trend + noise


def pressure_value(phase, progress):
    """
    Pressure in Torr. Sits at vacuum baseline throughout the test,
    with small outgassing-related rises during hot phases.
    """
    if phase == "soak":
        base = P_BASE
    elif phase == "ramp_hot":
        # Outgassing increases as temperature rises — linear bump up
        base = P_BASE * (1.0 + 0.8 * progress)
    elif phase == "dwell_hot":
        # Slightly elevated, slowly settling as outgassing stabilizes
        base = P_BASE * (1.8 - 0.3 * progress)
    elif phase == "ramp_cold":
        # Drops back toward baseline as temperature falls
        base = P_BASE * (1.5 - 0.5 * progress)
    elif phase == "dwell_cold":
        # Back to baseline, very stable
        base = P_BASE
    else:
        base = P_BASE

    # Small multiplicative noise so it still looks like a real sensor
    noise_factor = 1.0 + random.gauss(0, 0.03)  # +/- ~3%
    return base * max(0.5, noise_factor)


def acceleration_value(phase, progress):
    """
    Vibration in g. Pump baseline modulates by phase — higher during
    active ramps (pump working harder), lower during dwells (stable
    chamber). Phase-transition spikes preserved.
    """
    # Phase-dependent baseline
    if phase in ("ramp_hot", "ramp_cold"):
        # Active phase — pumps and compressors working harder
        baseline = ACCEL_BASE * 1.4
    elif phase in ("dwell_hot", "dwell_cold"):
        # Stable phase — chamber settled
        baseline = ACCEL_BASE * 0.8
    else:  # soak
        baseline = ACCEL_BASE

    base = baseline + random.gauss(0, 0.04)

    # Spike at phase boundaries (valve actuations, pump speed changes)
    near_boundary = progress < 0.05 or progress > 0.95
    if near_boundary and random.random() < 0.3:
        base += random.uniform(0.3, 0.8)

    return max(0, base)


def write_telemetry_batch(run, phase, progress):
    """
    Compute one sample per channel for the current phase progress and insert.
    """
    rows = [
        (run["id"], run["chamber_id"], "thermal",   "tc_01",
         temperature_value(phase, progress),  "C",    0, phase),
        (run["id"], run["chamber_id"], "pressure",  "pressure_main",
         pressure_value(phase, progress),     "Torr", 0, phase),
        (run["id"], run["chamber_id"], "vibration", "accel_x",
         acceleration_value(phase, progress), "g",    0, phase),
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

    # 5 minutes total. Each phase 60s gives clean linear ramps and visible
    # dwells in a procedure chart.
    phases = [
        ("soak",       60),
        ("ramp_hot",   60),
        ("dwell_hot",  60),
        ("ramp_cold",  60),
        ("dwell_cold", 60),
    ]

    try:
        for phase_name, duration_s in phases:
            log_event(run["id"], "phase_change", "info",
                      f"Entering phase: {phase_name}")
            print(f"  Phase: {phase_name} ({duration_s}s)")
            for tick in range(duration_s):
                progress = tick / max(1, duration_s - 1)  # 0.0 -> 1.0
                write_telemetry_batch(run, phase_name, progress)
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