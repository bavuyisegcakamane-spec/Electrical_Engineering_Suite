"""Hand-calculated reference checks for user-supplied ampacity and adiabatic factors."""
import pytest
from calculations.cable_sizing import derated_ampacity, adiabatic_short_circuit_check


def test_derating_and_nominal_chain():
    r = derated_ampacity(100, .87, .8, .95, design_current_a=55, breaker_rating_a=63)
    assert r["derated_ampacity_a"] == pytest.approx(66.12)
    assert r["nominal_current_chain_passes"] is True


def test_derating_flags_overrated_breaker():
    r = derated_ampacity(100, .8, .8, design_current_a=60, breaker_rating_a=80)
    assert r["derated_ampacity_a"] == pytest.approx(64)
    assert r["nominal_current_chain_passes"] is False


def test_adiabatic_pass_and_fail():
    passing = adiabatic_short_circuit_check(10, 1000, .1, 115)
    assert passing["fault_energy_a2s"] == pytest.approx(100000)
    assert passing["conductor_limit_a2s"] == pytest.approx(1322500)
    assert passing["thermal_screen_passes"]
    failing = adiabatic_short_circuit_check(1, 10000, 1, 115)
    assert not failing["thermal_screen_passes"]


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_invalid_reference_ampacity(bad):
    with pytest.raises(ValueError):
        derated_ampacity(bad)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True, 1.1])
def test_invalid_correction_factors(bad):
    with pytest.raises(ValueError):
        derated_ampacity(100, temperature_factor=bad)


@pytest.mark.parametrize("bad", [0, -1, float("nan"), float("inf"), True])
def test_invalid_short_circuit_inputs(bad):
    with pytest.raises(ValueError):
        adiabatic_short_circuit_check(10, 1000, .1, bad)
