# GRP6 — QuakeWatch Repair Shop

Group 6 repository for debugging, testing, and restoring the **QuakeWatch** earthquake data pipeline (`magnitude 5+` earthquakes around the Philippines).

## Group 6 Members
* **Eivrard Seraphim Franco** (Member 1 — Integrator & Incident 1)
* **Ralph Aron Bonifacio** (Member 2 — Incident 2, Incident 6 & Repair Log)
* **Josef Jayden Nepomuceno** (Member 3 — Incident 3)
* **Andrei Karl Dela Cruz** (Member 4 — Incident 4)
* **Matthew Zachary Medallon** (Member 5 — Incident 5 & Logging)

## Project Structure
* `QuakeWatch_broken/quakewatch.py` — Core 4-stage pipeline (`acquire`, `integrate`, `features`, `report`)
* `QuakeWatch_broken/run.py` — Entry point with console and file logging (`quakewatch.log`)
* `QuakeWatch_broken/tests/test_group.py` — Group 6 guarding tests covering Incidents 1–6
* `QuakeWatch_broken/REPAIR_LOG.md` — Full documentation of defects, root causes, fixes, and tests

## How to Run & Verify
From inside `QuakeWatch_broken`:

```bash
# Run the full test suite (32 tests)
python -m pytest -v

# Run the end-to-end pipeline and generate figures/dashboard.png
python run.py