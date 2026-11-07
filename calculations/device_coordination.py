"""Manufacturer time-current envelope review; no inferred protective-device curves.

CSV columns: current_a,min_trip_s,max_trip_s. Both envelope bounds must be
provided by the manufacturer. No interpolation outside the measured data range.
"""
import csv
import io
import math


def parse_curve_csv(content):
    if not isinstance(content, str) or len(content) > 1_000_000:
        raise ValueError('Curve CSV must be text under 1 MB')
    reader = csv.DictReader(io.StringIO(content))
    if reader.fieldnames != ['current_a', 'min_trip_s', 'max_trip_s']:
        raise ValueError('Expected CSV columns: current_a,min_trip_s,max_trip_s')
    points = []
    for row in reader:
        if len(points) >= 1000:
            raise ValueError('Maximum 1000 curve points')
        try:
            values = tuple(float(row[name]) for name in reader.fieldnames)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError('Invalid numeric curve row') from exc
        if any(not math.isfinite(v) or v <= 0 for v in values):
            raise ValueError('Curve values must be positive and finite')
        current, minimum, maximum = values
        if minimum > maximum:
            raise ValueError('Minimum trip time exceeds maximum')
        if points and current <= points[-1][0]:
            raise ValueError('Curve currents must be strictly increasing')
        points.append(values)
    if len(points) < 2:
        raise ValueError('At least two valid manufacturer points required')
    return tuple(points)


def _envelope(points, current):
    if not math.isfinite(current) or current < points[0][0] or current > points[-1][0]:
        raise ValueError('Current outside documented curve range; no extrapolation')
    for left, right in zip(points, points[1:]):
        if left[0] <= current <= right[0]:
            ratio = math.log(current / left[0]) / math.log(right[0] / left[0])
            return tuple(math.exp(math.log(left[i]) + ratio * math.log(right[i] / left[i]))
                         for i in (1, 2))
    raise ValueError('Current outside curve range')


def review_device_coordination(upstream_csv, downstream_csv, fault_current_a,
                               required_disconnection_s, source_description):
    """Conservative envelope separation at one specified fault current only.

    PASS means sampled bounds do not overlap; it does not prove selectivity,
    interrupting capacity, or compliance across the entire fault-current range.
    """
    if any(not isinstance(v, (int, float)) or isinstance(v, bool) or
           not math.isfinite(v) or v <= 0 for v in (fault_current_a, required_disconnection_s)):
        raise ValueError('Current and disconnection time must be positive and finite')
    if not isinstance(source_description, str) or not source_description.strip():
        raise ValueError('Manufacturer, device model and curve source are required')
    upstream = _envelope(parse_curve_csv(upstream_csv), fault_current_a)
    downstream = _envelope(parse_curve_csv(downstream_csv), fault_current_a)
    return {'fault_current_a': fault_current_a,
            'upstream_trip_envelope_s': upstream, 'downstream_trip_envelope_s': downstream,
            'downstream_upper_time_within_user_limit': downstream[1] <= required_disconnection_s,
            'envelopes_separated_at_sampled_current': downstream[1] < upstream[0],
            'source': source_description,
            'compliance_status': 'NOT DETERMINED',
            'limitations': 'Log-log interpolated manufacturer envelopes only. Verify device settings, DC/AC ratings, full fault-current range, short-circuit capacity, tolerances and installation requirements.'}
