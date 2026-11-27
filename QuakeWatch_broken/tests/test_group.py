import quakewatch as qw
import logging

def test_features_stage_uses_depth_km(loaded):
    """Incident 1: features_stage must read the depth_km column."""
    qw.integrate()
    feat = qw.features_stage()
    assert "depth_class" in feat.columns
    assert feat["depth_class"].notna().all()


def test_incident_5_idempotent_load_and_logging(project, caplog):
    """Incident 5: second load_new() fetches zero duplicate rows and logs stage counts."""
    with caplog.at_level(logging.INFO, logger="quakewatch"):
        first = qw.load_new()
        second = qw.load_new()

    assert first == 462
    assert second == 0
    assert qw.read_raw()["id"].is_unique
    assert "acquire: 0 new rows" in caplog.text