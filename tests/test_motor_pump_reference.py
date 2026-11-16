"""Independent hand-worked reference cases for preliminary three-phase motors/panels.

These verify textbook equations, not compliance or suitability of protection.
"""
from math import pi, sqrt

import pytest

from calculations.motors import analyze_motor
from calculations.pump_panel import Pump, study_panel


def test_motor_reference_11kw_400v_three_phase():
    # P_in=11/0.9 kW, S=P_in/0.85 kVA, I=S*1000/(sqrt(3)*400).
    result = analyze_motor(11, 400, 0.90, 0.85, 1470)
    assert result["input_kw"] == pytest.approx(12.2222222222)
    assert result["apparent_kva"] == pytest.approx(14.3790849673)
    assert result["line_current_amps"] == pytest.approx(20.754427, rel=1e-5)
    assert result["shaft_torque_nm"] == pytest.approx(11000 * 60 / (2 * pi * 1470))
    assert result["losses_kw"] == pytest.approx(1.2222222222)


def test_panel_reference_two_motors_full_precision_and_simultaneity():
    panel = study_panel([Pump(7.5), Pump(11), Pump(22)], voltage_v=400,
                        power_factor=0.85, efficiency=0.9, simultaneous=2)
    amps_per_kw = 1000 / (sqrt(3) * 400 * 0.85 * 0.9)
    assert panel["simultaneous_running_a"] == pytest.approx(round((22 + 11) * amps_per_kw, 2))
    assert panel["installed_running_a"] == pytest.approx(round((7.5 + 11 + 22) * amps_per_kw, 2))


def test_panel_breaker_comparison_uses_unrounded_current():
    # Exactly 20 A is slightly below the actual 11 kW running estimate.
    result = study_panel([Pump(11)], main_breaker_a=20)
    exact = 11000 / (sqrt(3) * 400 * 0.85 * 0.9)
    assert result["exceeds_main_rating"] == (exact > 20)


@pytest.mark.parametrize("invalid", [0, -1, float("nan"), float("inf"), True])
def test_motor_rejects_invalid_power(invalid):
    with pytest.raises(ValueError):
        analyze_motor(invalid, 400, 0.9, 0.85, 1470)


def test_single_phase_is_not_silently_supported():
    # Existing API is explicitly three-phase; a 220 V input is interpreted
    # as three-phase line-to-line voltage, NOT a single-phase motor study.
    three_phase = analyze_motor(2.2, 220, 0.9, 0.85, 1450)
    assert three_phase["line_current_amps"] == pytest.approx(
        2200 / (sqrt(3) * 220 * 0.9 * 0.85)
    )
