# Repair log

Study group: Group 6   Members: Eivrard Seraphim Franco, Ralph Aron Bonifacio, Josef Jayden Nepomuceno, Andrei Karl Dela Cruz, Matthew Zachary Medallon

## Defects

| # | Symptom (what was wrong for the user) | Cause (file, function, line; why it was wrong) | Fix (what you changed) | Test that now guards it | Fixed by |
| --- | --- | --- | --- | --- | --- |
| 1 | `features_stage()` crashed with a `KeyError` when classifying earthquake depth. | `quakewatch.py`, `features_stage()`, line 161: referenced non-existent column `t["depth"]` instead of `t["depth_km"]`. | Replaced `t["depth"]` with `t["depth_km"]` in `depth_class(t["depth_km"])`. | `test_features_stage_uses_depth_km` | Eivrard Seraphim Franco |
| 2 | The M 7.6 Mindanao earthquake showed `14:37` instead of `22:37` Manila local time. | `quakewatch.py`, `features_stage()`, line 158: used `.dt.tz_localize(None).dt.tz_localize("Asia/Manila")`, which relabeled UTC timestamps without shifting `+08:00`. | Replaced the double `tz_localize` call with `t["time"].dt.tz_convert("Asia/Manila")`. | `test_incident_2_manila_time_conversion` | Ralph Aron Bonifacio |
| 3 | Magnitude `6.0` events were labeled `"Moderate"` instead of `"Strong"`, lowering the `Strong` or above count from 42 to 31. | `quakewatch.py`, module top level (`MAG_BINS`), line 34: upper bound for `"Moderate"` was `6.05` with right-inclusive `pd.cut`, putting `6.0` in `"Moderate"`. | Changed `MAG_BINS` from `[4.95, 6.05, 6.95, 7.95, 10]` to `[4.95, 5.95, 6.95, 7.95, 10]`. | `test_incident_3_mag_class_boundaries` | Josef Jayden Nepomuceno |
| 4 | Mindanao and southwestern Luzon earthquakes were assigned to Tuguegarao (`C04`) instead of Butuan City (`C10`) and Manila (`C01`). | `quakewatch.py`, `nearest_city()`, line 142: passed `events["longitude"]` as `lat1` and `events["latitude"]` as `lon1` into `haversine_km()`. | Swapped the event arguments so `events["latitude"]` is passed first and `events["longitude"]` second. | `test_incident_4_nearest_city_mindanao_via_fake_api` | Andrei Karl Dela Cruz |
| 5 | Running `load_new()` or `run_pipeline()` twice re-fetched all 462 events and created duplicate event IDs in `data/raw`. | `quakewatch.py`, `load_new()`, line 105: always queried from `FIRST_DAY` instead of checking `watermark()` and skipping existing IDs. | Queried from `watermark().isoformat()` when raw files exist and filtered out existing IDs via `~fetched["id"].isin(existing_ids)`. | `test_incident_5_idempotent_load_and_logging` | Matthew Zachary Medallon |
| 6 | Invalid rows (such as negative `depth_km`) passed into `data/clean/events.parquet` instead of being quarantined to `rejects.csv`. | `quakewatch.py`, `split_by_contract()`, lines 131–135: caught and ignored validation errors with `pass` and always returned all `raw` rows with an empty `rejects` DataFrame. | Validated with `CONTRACT.validate(raw, lazy=True)`, caught `pa.errors.SchemaErrors`, and split failing indices from `err.failure_cases["index"]` into `rejects` and `good`. | `test_incident_6_contract_quarantines_invalid_rows` | Ralph Aron Bonifacio |

## Our own tests (in `tests/test_group.py`)

| Test name | Tool used (`parametrize`, fake API, `caplog`) | What it proves | Fails on the broken code? | Written by |
| --- | --- | --- | --- | --- |
| `test_features_stage_uses_depth_km` | `pytest` fixture (`loaded`) | `features_stage()` reads `depth_km` and populates non-null `depth_class` labels without raising `KeyError`. | Yes | Eivrard Seraphim Franco |
| `test_incident_2_manila_time_conversion` | `tmp_path`, `monkeypatch` | `features_stage()` converts `2023-12-02 14:37 UTC` to `2023-12-02 22:37 Asia/Manila` (`hour_local == 22`). | Yes | Ralph Aron Bonifacio |
| `test_incident_3_mag_class_boundaries` | `@pytest.mark.parametrize` | `mag_class()` maps boundary magnitudes `5.0`, `5.9`, `6.0`, `6.9`, `7.0`, `7.9`, and `8.0` to the exact expected labels (`6.0` -> `Strong`). | Yes | Josef Jayden Nepomuceno |
| `test_incident_4_nearest_city_mindanao_via_fake_api` | fake API (`@responses.activate`) | End-to-end `load_new()` + `integrate()` maps Mindanao coordinates `[126.4, 8.5, 32.0]` to Butuan City (`C10`). | Yes | Andrei Karl Dela Cruz |
| `test_incident_5_idempotent_load_and_logging` | `caplog` | Calling `load_new()` a second time adds `0` duplicate rows, preserves unique IDs, and emits `acquire: 0 new rows`. | Yes | Matthew Zachary Medallon |
| `test_incident_6_contract_quarantines_invalid_rows` | `pytest` fixture (`loaded`) | `split_by_contract()` excludes invalid rows (`depth_km = -10.0`) from `clean` and writes them to `data/clean/rejects.csv`. | Yes | Ralph Aron Bonifacio |
| `test_rejected_rows_log_a_warning` | `caplog` | Proves a `WARNING` (`"rows failed contract validation"`) is logged when invalid rows are quarantined. | Yes | Ralph Aron Bonifacio |

## Logging we added

| Where (function) | Level | Message | Why this level |
| --- | --- | --- | --- |
| `run.py` (module setup via `logging.basicConfig`) | `INFO` | Configured `logging.FileHandler("logs/run.log")` alongside `StreamHandler` with format `"%(asctime)s %(levelname)s %(name)s %(message)s"`. | Captures standard stage-by-stage pipeline progress (`acquire`, `integrate`, `features`, `report`) in both console and `logs/run.log`. |
| `quakewatch.py`, `split_by_contract()` | `ERROR` (`log.exception`) | `"integrate: schema validation failed"` | Records the full `SchemaErrors` traceback whenever incoming raw data violates the Pandera data contract. |
| `quakewatch.py`, `split_by_contract()` | `WARNING` | `"integrate: %d rows failed contract validation"` | Alerts operators that invalid rows were quarantined to `rejects.csv` while allowing clean rows to continue through the pipeline. |

## One thing we learned about debugging

Writing a failing guarding test before touching the pipeline code forced us to pinpoint each root cause instead of guessing at symptoms. Working on isolated feature branches per defect also prevented teammates' edits from colliding and made final integration into `main` straightforward.

- **Contract Validation Edge Case:** In `split_by_contract()`, row-level schema failures populate `bad_idx` via Pandera's `failure_cases["index"]`; if a structural schema-level error (such as a missing column) occurs with no row index, `bad_idx` would be empty unless handled separately.
