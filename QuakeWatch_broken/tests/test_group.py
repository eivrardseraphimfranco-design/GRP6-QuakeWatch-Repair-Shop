import quakewatch as qw


def test_features_stage_uses_depth_km(loaded):
    """Incident 1: features_stage must read the depth_km column."""
    qw.integrate()
    feat = qw.features_stage()
    assert "depth_class" in feat.columns
    assert feat["depth_class"].notna().all()

import pandas as pd
import pytest


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