"""Generic low-voltage panel material types for systems up to 450 V.
Not rated products, mandatory BOM items, or engineering approvals.
"""
PANEL_MATERIALS = {
    "Incoming and distribution": (
        "Switch disconnector", "Load break switch", "Fuse switch disconnector",
        "NH fuse base", "HRC fuse link", "MCCB shunt trip", "MCCB undervoltage release",
        "MCCB auxiliary contact", "Rotary door-coupled handle", "Busbar support insulator",
        "Busbar insulating cover", "Busbar end cap", "Busbar joint kit",
        "Distribution block", "Neutral bar", "Phase barrier", "Power terminal block",
        "Feed-through terminal block", "Earth terminal block", "Neutral terminal block"),
    "Motor and pump control": (
        "Reversing contactor", "Mechanical contactor interlock", "Contactor coil",
        "Contactor surge suppressor", "Electronic motor overload relay",
        "Motor thermistor protection relay", "Motor PTC sensor interface",
        "Phase failure relay", "Phase sequence relay", "Phase imbalance relay",
        "Pump alternation relay", "Pump controller", "Float switch interface relay",
        "Pressure switch", "Pressure transmitter interface", "Level controller",
        "Dry-run protection relay", "Flow switch", "VFD braking resistor review",
        "VFD EMC filter", "VFD line reactor", "VFD output reactor",
        "VFD sine filter", "Soft starter bypass contactor"),
    "Controls and automation": (
        "24 V DC power supply", "Control transformer", "Control transformer fuse",
        "DC circuit breaker", "PLC digital input module", "PLC digital output module",
        "PLC analogue input module", "PLC analogue output module", "PLC expansion module",
        "Industrial communication gateway", "Modbus communication module",
        "Interface relay socket", "Relay base", "Plug-in control relay",
        "Control circuit terminal jumper", "Control circuit diode",
        "Control circuit surge suppressor", "Panel thermostat", "Panel hygrostat"),
    "Operator interface and indication": (
        "Illuminated pushbutton", "Momentary pushbutton", "Maintained pushbutton",
        "Key selector switch", "Three-position selector switch", "Pilot indicator lamp",
        "Buzzer", "Alarm sounder", "Alarm beacon", "Emergency stop contact block",
        "Emergency stop protective shroud", "Digital panel voltmeter",
        "Digital panel ammeter", "Multifunction energy meter", "Hour meter",
        "Panel-mounted HMI", "Label legend plate"),
    "Enclosure and assembly": (
        "Wall-mount enclosure", "Floor-standing enclosure", "Mounting backplate",
        "Enclosure plinth", "Enclosure door gasket", "Door earthing braid",
        "Door stay", "Enclosure lock", "Panel ventilation louvre",
        "Filter fan", "Fan filter mat", "Enclosure heater", "Anti-condensation heater",
        "Panel light", "Cable gland plate", "Cable gland locknut",
        "Blanking plug", "Cable grommet", "Slotted wiring duct", "Wiring duct cover",
        "DIN rail end stop", "DIN rail spacer", "Wire marker", "Terminal marker",
        "Ferrule marker", "Cable tie", "Cable tie mount", "Wire end ferrule",
        "Ring cable lug", "Fork cable lug", "Heat-shrink sleeve",
        "Cable shield clamp", "EMC cable gland", "Earthing stud"),
    "Protection and monitoring": (
        "Type 1 surge protection device", "Type 2 surge protection device",
        "SPD backup protection", "SPD remote signalling contact",
        "Residual current monitor", "Earth leakage current transformer",
        "Core balance current transformer", "CT shorting terminal block",
        "Voltage monitoring relay", "Frequency monitoring relay",
        "Temperature monitoring relay", "Thermal sensor", "Power quality meter",
        "Panel temperature sensor"),
}

def panel_material_count():
    return sum(len(items) for items in PANEL_MATERIALS.values())
