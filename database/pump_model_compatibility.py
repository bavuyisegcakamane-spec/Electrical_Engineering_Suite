"""Conservative pre-selection screening, not electrical design approval."""
import json

CATEGORY_COMPONENTS = {
    'Variable frequency drive (VFD)': ('vfd', 'variable frequency drive', 'drive'),
    'Soft starter': ('soft starter',),
    'Motor protection circuit breaker (MPCB)': ('motor protection', 'motor circuit breaker', 'mpcb'),
}

def screen_model(component, category, specifications, motor_kw=None, voltage_v=None,
                 nameplate_current_a=None, starter=None):
    """Return (blocked_reasons, review_notes). Missing data never implies approval."""
    blocked, review = [], []
    name = component.lower()
    allowed = CATEGORY_COMPONENTS.get(category)
    if not allowed:
        return ['No verified component-category mapping for this catalogue entry'], []
    if not any(word in name for word in allowed):
        blocked.append(f'{category} does not match BOM component {component}')
    if category == 'Variable frequency drive (VFD)' and starter != 'VFD':
        blocked.append('VFD model requires a VFD motor branch')
    if category == 'Soft starter' and starter != 'Soft starter':
        blocked.append('Soft starter model requires a soft-starter motor branch')
    if motor_kw is not None:
        rating = specifications.get('rated_motor_power_kw')
        if rating is None:
            rating = specifications.get('rated_motor_power_kw_at_400v') if voltage_v == 400 else None
        if rating is not None and motor_kw > rating:
            blocked.append(f'Motor {motor_kw:g} kW exceeds listed model rating {rating:g} kW')
        elif rating is None:
            review.append('Motor power suitability requires OEM datasheet review')
    if voltage_v is not None:
        lo, hi = specifications.get('supply_min_v'), specifications.get('supply_max_v')
        if lo is not None and hi is not None and not lo <= voltage_v <= hi:
            blocked.append(f'Supply {voltage_v:g} V outside listed {lo:g}-{hi:g} V range')
        elif lo is None or hi is None:
            review.append('Supply voltage compatibility requires OEM datasheet review')
    current = specifications.get('continuous_output_a') or specifications.get('starter_rating_a')
    if nameplate_current_a is not None and current is not None and nameplate_current_a > current:
        blocked.append(f'Motor current {nameplate_current_a:g} A exceeds listed {current:g} A')
    elif category != 'Motor protection circuit breaker (MPCB)':
        review.append('Motor nameplate current and thermal duty require verification')
    if category == 'Motor protection circuit breaker (MPCB)':
        low, high = specifications.get('adjustment_min_a'), specifications.get('adjustment_max_a')
        if nameplate_current_a is not None and low is not None and high is not None:
            if not low <= nameplate_current_a <= high:
                blocked.append(f'Nameplate current {nameplate_current_a:g} A outside MPCB setting range {low:g}-{high:g} A')
        else:
            review.append('MPCB adjustment range versus motor nameplate current requires verification')
    review.append('Verify OEM coordination, short-circuit rating, installation and current product status')
    return blocked, review
