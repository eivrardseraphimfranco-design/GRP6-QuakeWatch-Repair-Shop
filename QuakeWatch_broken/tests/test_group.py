import logging
import pandas as pd
import pytest
import responses
import quakewatch as qw


def test_features_stage_uses_depth_km(loaded):
    """Incident 1: features_stage must read the depth_km column."""
    qw.integrate()
    feat = qw.features_stage()
    assert "depth_class" in feat.columns
    assert feat["depth_class"].notna().all()


def test_incident_2_manila_time_conversion(tmp_path, monkeypatch):
    """Incident 2: features_stage must convert UTC timestamps to Asia/Manila (+08:00)."""
    clean_dir = tmp_path / "clean"
    feat_dir = tmp_path / "features"
    clean_dir.mkdir()
    monkeypatch.setattr(qw, "CLEAN", clean_dir)
    monkeypatch.setattr(qw, "FEAT", feat_dir)

    sample = pd.DataFrame([{
        "id": "test-tz-1",
        "time": pd.Timestamp("2023-12-02 14:37:00", tz="UTC"),
        "latitude": 8.5,
        "longitude": 126.4,
        "depth_km": 32.0,
        "mag": 7.6,
        "magType": "mww",
        "place": "Mindanao, Philippines",
        "city_id": "C10",
        "near_km": 120.0,
        "lgu_name": "Butuan",
    }])
    sample.to_parquet(clean_dir / "events.parquet", index=False)

    out = qw.features_stage()

    assert out["hour_local"].iloc[0] == 22
    assert out["local"].iloc[0].strftime("%Y-%m-%d %H:%M") == "2023-12-02 22:37"


@pytest.mark.parametrize("mag, expected", [
    (5.0, "Moderate"),
    (5.9, "Moderate"),
    (6.0, "Strong"),
    (6.9, "Strong"),
    (7.0, "Major"),
    (7.9, "Major"),
    (8.0, "Great"),
])
def test_incident_3_mag_class_boundaries(mag, expected):
    """Incident 3: magnitude 6.0 must be classified as Strong, not Moderate."""
    result = qw.mag_class(pd.Series([mag])).iloc[0]
    assert result == expected


@responses.activate
def test_incident_4_nearest_city_mindanao_via_fake_api(tmp_path, monkeypatch):
    """Incident 4: nearest_city must pass (lat, lon) in order so Mindanao events map to Butuan (C10)."""
    raw_dir = tmp_path / "raw"
    clean_dir = tmp_path / "clean"
    monkeypatch.setattr(qw, "RAW", raw_dir)
    monkeypatch.setattr(qw, "CLEAN", clean_dir)
    monkeypatch.setattr(qw, "BASE", "https://fake-usgs.test")

    responses.add(
        responses.GET,
        "https://fake-usgs.test/fdsnws/event/1/query",
        json={
            "features": [
                {
                    "id": "mindanao-test-1",
                    "properties": {
                        "time": 1701527820000,
                        "mag": 7.6,
                        "magType": "mww",
                        "place": "East of Mindanao, Philippines",
                    },
                    "geometry": {
                        "coordinates": [126.4, 8.5, 32.0],
                    },
                }
            ]
        },
        status=200,
    )

    qw.load_new()
    clean = qw.integrate()

    assert len(clean) == 1
    assert clean["city_id"].iloc[0] == "C10"
    assert clean["lgu_name"].iloc[0] == "Butuan City"


def test_incident_5_idempotent_load_and_logging(project, caplog):
    """Incident 5: second load_new() fetches zero duplicate rows and logs stage counts."""
    with caplog.at_level(logging.INFO, logger="quakewatch"):
        first = qw.load_new()
        second = qw.load_new()

    assert first == 462
    assert second == 0
    assert qw.read_raw()["id"].is_unique
    assert "acquire: 0 new rows" in caplog.text

def test_incident_6_contract_quarantines_invalid_rows(loaded):
    """Incident 6: split_by_contract must set aside invalid rows into rejects.csv."""
    bad = qw.read_raw().head(1).copy()
    bad["id"] = "incident6-invalid-row"
    bad["depth_km"] = -10.0
    qw.save_raw(bad)

    clean = qw.integrate()
    rejects = pd.read_csv(qw.CLEAN / "rejects.csv")

    assert "incident6-invalid-row" not in set(clean["id"])
    assert "incident6-invalid-row" in set(rejects["id"])