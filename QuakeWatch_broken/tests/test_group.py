import quakewatch as qw
import responses

def test_features_stage_uses_depth_km(loaded):
    """Incident 1: features_stage must read the depth_km column."""
    qw.integrate()
    feat = qw.features_stage()
    assert "depth_class" in feat.columns
    assert feat["depth_class"].notna().all()


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
