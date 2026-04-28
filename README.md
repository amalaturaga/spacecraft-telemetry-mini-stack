# TVAC Mini Stack

A local end-to-end telemetry pipeline that simulates the data flow of a 
spacecraft thermal-vacuum (TVAC) test campaign. Built to mirror the 
architecture of real ground-test data systems used in aerospace: 
time-series telemetry, structured test-run metadata, and live dashboards 
in a unified database.

> **What's TVAC?** Thermal Vacuum testing is how spacecraft hardware is 
> qualified for spaceflight. The article under test is placed in a sealed 
> chamber, vacuum is drawn down to simulate space, and temperature is 
> cycled through hot and cold extremes while the article is operated and 
> monitored. The data captured during these tests determines whether 
> hardware is fit to fly.

## What this demonstrates

- **Time-series database design** with TimescaleDB hypertables for 
  high-frequency sensor data.
- **Relational modeling** of test campaigns, articles, and event timelines 
  in normalized Postgres schemas.
- **Live observability stack** with Grafana querying Postgres for both 
  time-series visualizations and tabular analytics.
- **Test lifecycle modeling**: every test run has a defined start, ordered 
  phases, events, and a recorded outcome — the same pattern used in 
  production aerospace ground systems.
- **Containerized infrastructure** via Docker for reproducible local 
  development.

## Architecture
┌──────────────────────────────┐
│  Python Telemetry Simulator  │
│  - Phase-driven test runner  │
│  - Sensor stream generator   │
│  - Event logger              │
└──────────────┬───────────────┘
│
▼
┌──────────────────────────────┐
│   TimescaleDB (Postgres 16)  │
│   - chambers (metadata)      │
│   - test_articles            │
│   - test_runs                │
│   - telemetry (hypertable)   │
│   - test_events (hypertable) │
└──────────────┬───────────────┘
│
▼
┌──────────────────────────────┐
│           Grafana            │
│   - Live sensor dashboards   │
│   - Test run history table   │
│   - Phase-change annotations │
└──────────────────────────────┘

## Quickstart

Requirements: Docker Desktop, Python 3.10+, Grafana (local install or 
container).

**1. Start TimescaleDB**

```bash
docker run -d \
  --name tvac-timescale \
  -p 5433:5432 \
  -e POSTGRES_PASSWORD=tvac_dev \
  -v tvac_pgdata:/var/lib/postgresql/data \
  timescale/timescaledb:latest-pg16
```

**2. Initialize the schema**

```bash
docker exec -i tvac-timescale psql -U postgres -d postgres < schema/init.sql
```

**3. Set up Python environment**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env if your connection details differ
```

**4. Run a simulated test campaign**

```bash
python telemetry_simulator.py
```

Each run creates a new entry in `test_runs`, streams ~600 telemetry 
points across three sensors, and logs phase transitions as events.

**5. View dashboards**

Add the database as a PostgreSQL data source in Grafana:
- Host: `localhost:5433`
- Database: `tvac_sandbox`
- User: `postgres`
- TimescaleDB toggle: ON

Import `grafana/dashboards/tvac_overview.json` for a pre-built dashboard.

## Schema

The data model separates **what** is being tested (`test_articles`), 
**where** it's tested (`chambers`), **when** a test happened (`test_runs`), 
**what was measured** (`telemetry`), and **what occurred** (`test_events`).

Telemetry and events are TimescaleDB hypertables, partitioned by time 
for efficient range queries. Reference tables are normal Postgres tables.

See `schema/init.sql` for the full schema.

## What I learned building this

- The trade-offs between log aggregation systems (Loki) and time-series 
  databases (InfluxDB, TimescaleDB) for industrial telemetry workloads.
- Why hybrid relational + time-series stores (TimescaleDB) are 
  increasingly preferred for analytics-heavy use cases over pure TSDBs.
- The importance of a well-designed schema for queryability — the 
  difference between "data exists" and "data can be analyzed."
- How real test infrastructure organizes data around test-run lifecycles, 
  not just raw sensor streams.

## Next steps

- Realistic thermal profiles (sinusoidal ramps, soak gradients) replacing 
  uniform random readings.
- Failure injection: sensor dropouts, drift, simulated thermal runaway.
- Automated abort logic: webhook receiver that responds to Grafana alerts 
  by writing safety events back into the database.
- Multi-chamber simulation with concurrent test runs.

## License

MIT