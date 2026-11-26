import quakewatch as qw


def test_features_stage_uses_depth_km(loaded):
    """Incident 1: features_stage must read the depth_km column."""
    qw.integrate()
    feat = qw.features_stage()
    assert "depth_class" in feat.columns
    assert feat["depth_class"].notna().all()