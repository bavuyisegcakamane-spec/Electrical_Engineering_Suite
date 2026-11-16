"""Independent reference cases and safeguards for preliminary cable/protection models."""
from math import sqrt
import pytest
from calculations.cables import estimate_voltage_drop
from calculations.protection import estimate_fault_current


def test_single_phase_copper_reference():
    r = estimate_voltage_drop(25, 40, 6, 230, conductor_temp_c=20)
    assert r["voltage_drop_v"] == pytest.approx(2 * 25 * 40 * .01724 / 6)
    assert r["voltage_drop_percent"] == pytest.approx(100 * r["voltage_drop_v"] / 230)


def test_three_phase_hot_aluminium_reference():
    rho = .02826 * (1 + .00403 * 50)
    r = estimate_voltage_drop(32, 55, 16, 400, "Aluminium", 3, 70, .9)
    assert r["voltage_drop_v"] == pytest.approx(sqrt(3) * 32 * 55 * rho / 16 * .9)


def test_single_phase_fault_reference():
    r = estimate_fault_current(230, .115, 32, 6, phases=1)
    assert r["fault_current_amps"] == pytest.approx(2000)
    assert not r["exceeds_stated_breaking_capacity"]


def test_three_phase_fault_reference():
    r = estimate_fault_current(400, .08, 63, 6, phases=3)
    assert r["fault_current_amps"] == pytest.approx(400 / (sqrt(3) * .08))


def test_fault_breaking_capacity_exceeded():
    r = estimate_fault_current(230, .02, 32, 6)
    assert r["fault_current_ka"] == pytest.approx(11.5)
    assert r["exceeds_stated_breaking_capacity"]


@pytest.mark.parametrize("phases", [0, 2, True, None, "3", 1.0])
def test_reject_invalid_phase_values(phases):
    with pytest.raises(ValueError):
        estimate_voltage_drop(10, 20, 4, 230, phases=phases)
    with pytest.raises(ValueError):
        estimate_fault_current(230, .1, 32, 6, phases=phases)
