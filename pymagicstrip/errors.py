"""Custom exceptions for pymagicstrip."""


class OutOfRange(Exception):
    """Color or brightness is out of range."""


class BleConnectionError(Exception):
    """Error connecting to device."""


class BleTimeoutError(Exception):
    """Timeout while communicating with device."""
