import quakewatch as qw
import pandas as pd


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