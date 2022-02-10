"""Bluetooth command constants."""

SERVICE_UUID = "0000fff0-0000-1000-8000-00805f9b34fb"
CHARACTERISTIC_UUID = "0000fff1-0000-1000-8000-00805f9b34fb"
HARDCODED_NAMES = ["HTZM"]

CMD_ACK = "f00201"
STATUS_REGEX = r"0f(00|01)([A-Za-z-0-9]{2})[A-Za-z-0-9]{2}([A-Za-z-0-9]{2})"

TOGGLE_POWER = "04"

EFFECTS = {
    "Flashing Blue": "0701",
    "Flashing Green": "0702",
    "Flashing Red": "0703",
    "Flashing Cyan": "0704",
    "Flashing Purple": "0705",
    "Flashing Yellow": "0706",
    "Flashing White": "0707",
    "Breathing Blue": "0708",
    "Breathing Green": "0709",
    "Breathing Red": "070A",
    "Breathing Cyan": "070B",
    "Breathing Purple": "070C",
    "Breathing Yellow": "070D",
    "Breathing White": "070E",
    "Strobe Blue": "070F",
    "Strobe Green": "0710",
    "Strobe Red": "0711",
    "Strobe Cyan": "0712",
    "Strobe Purple": "0713",
    "Strobe Yellow": "0714",
    "Strobe White": "0715",
    "Gradient RBR": "0716",
    "Gradient WVW": "0717",
    "Gradient GVG": "0718",
    "Gradient BYB": "0719",
    "Gradient RCR": "071A",
    "Gradient YCY": "071B",
    "Gradient VCV": "071C",
    "Gradient VYV": "071D",
    "Three-Color Transitions": "071E",
    "Colorful Jump": "071F",
    "Three-Color Alternating Breathing": "0720",
    "Colorful Alternate Breathing": "0721",
    "Colorful": "0722",
    "Six Color Gradient": "0723",
    "RGB Gradient": "0724",
    "Three-Color Flashing": "0725",
    "Colorful Flashing": "0726",
    "Three-Color Strobe": "0727",
    "Colorful Strobe": "0728",
    "Automatic": "07F0",
}
