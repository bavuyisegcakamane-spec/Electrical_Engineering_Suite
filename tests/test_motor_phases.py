"""Reference checks for explicitly selected single-phase motor estimates."""
from math import sqrt

import pytest
from calculations.motors import analyze_motor


def test_single_phase_220v_reference():
    result = analyze_motor(2.2, 220, 0.9, 0.85, 1450, phases=1)
    assert result["line_current_amps"] == pytest.approx(2200 / (220 * 0.9 * 0.85))
    assert result["input_kw"] == pytest.approx(2.2 / 0.9)


def test_three_phase_default_backward_compatible():
    default = analyze_motor(2.2, 400, 0.9, 0.85, 1450)
    explicit = analyze_motor(2.2, 400, 0.9, 0.85, 1450, phases=3)
    assert default == explicit
    assert explicit["line_current_amps"] == pytest.approx(2200 / (sqrt(3) * 400 * 0.9 * 0.85))


@pytest.mark.parametrize("phases", [0, 2, 4, True, 1.0, "1", None])
def test_invalid_phase_count_rejected(phases):
    with pytest.raises(ValueError, match="phases"):
        analyze_motor(2.2, 220, 0.9, 0.85, 1450, phases=phases)
