"""Transparent symptom-based electrical fault-finding guidance.

Suggestions are not diagnoses; never instruct live or unqualified testing.
"""

FAULT_GUIDES = {
    "Motor will not start": (
        "Supply interruption or missing phase", "Tripped overload or protective device",
        "Control circuit, contactor or interlock fault", "Motor winding or mechanical seizure"),
    "Motor overheating": (
        "Overload or poor ventilation", "Voltage imbalance or single phasing",
        "Bearing friction or excessive starts", "Incorrect motor connection"),
    "Breaker trips repeatedly": (
        "Overload or short circuit", "Earth leakage or insulation damage",
        "Incorrect device characteristic", "Faulty downstream equipment"),
    "Low voltage at equipment": (
        "Excessive cable voltage drop", "Loose or high-resistance connection",
        "Overloaded supply or transformer", "Unbalanced load"),
    "RCD trips": (
        "Earth leakage in connected equipment", "Moisture or damaged insulation",
        "Neutral-to-earth connection downstream", "Cumulative leakage or faulty device"),
    "Transformer overheating": (
        "Overload or harmonics", "Cooling system obstruction",
        "Loose termination or winding issue", "Voltage or tap mismatch"),
}


def diagnose_symptom(symptom):
    if symptom not in FAULT_GUIDES:
        raise ValueError("Choose a supported symptom")
    return {
        "symptom": symptom,
        "possible_causes": list(FAULT_GUIDES[symptom]),
        "safe_next_steps": [
            "Record the symptom, equipment rating, operating conditions and event history.",
            "Have a qualified person isolate, lock out and verify absence of voltage before inspection.",
            "Inspect accessible documentation and de-energized equipment using approved procedures.",
            "Have a qualified person select appropriate instruments and perform standards-compliant tests.",
            "Compare measurements with manufacturer specifications and applicable local standards."
        ],
        "warning": "Possible causes are not ranked or confirmed. Do not bypass protection, open energized equipment, or attempt live measurements without authorized professional procedures."
    }
