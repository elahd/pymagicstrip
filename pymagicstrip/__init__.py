"""Hub for communicating with pymagicstrip devices."""

# https://github.com/elupus/fjaraskupan/blob/master/src/fjaraskupan/__init__.py

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
import logging
import re

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

from . import const
from .const import CHARACTERISTIC_UUID, EFFECTS, TOGGLE_POWER
from .errors import BleConnectionError, BleTimeoutError, OutOfRange

__version__ = "0.1.0"

_LOGGER = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
_LOGGER.addHandler(handler)
_LOGGER.setLevel(logging.DEBUG)


def _judge_rssi(rssi: int) -> str | None:
    """Return qualatative assessment of RSSI."""

    if rssi >= 0:
        return "Unknown"
    if rssi >= -55:
        return "Excellent"
    if rssi >= -75:
        return "Good"
    if rssi >= -85:
        return "Bad"
    if rssi < -85:
        return "Terrible"

    return None


class MagicStripHub:
    """Controller class."""

    def __init__(self) -> None:
        """Initialize hub."""
        self._known_devices: list = []

    async def add_known_devices(self, addresses: list[str]) -> list[MagicStripDevice]:
        """Add known devices from a list of addresses."""

        for address in addresses:
            device = await BleakScanner.find_device_by_address(address)

            if device:
                self._known_devices.append(
                    await MagicStripDevice.create(
                        device.name, device.address, device.rssi
                    )
                )

        return self._known_devices

    async def discover(self) -> list[MagicStripDevice]:
        """Search for undiscovered devices."""

        devices = await BleakScanner.discover()

        if len(devices) == 0:
            return []

        for device in devices:
            if (
                device.name
                and device.name.lower() in [d.lower() for d in const.HARDCODED_NAMES]
                and const.SERVICE_UUID in device.metadata.get("uuids", [])
            ):
                self._known_devices.append(
                    await MagicStripDevice.create(
                        device.name, device.address, device.rssi
                    )
                )

        return self._known_devices


class MagicStripDevice:
    """Device class."""

    @classmethod
    async def create(cls, name: str, address: str, rssi: int) -> MagicStripDevice:
        """Magicstripdevice factory. Required to allow use of async functions immediately upon creation."""
        new_device = MagicStripDevice(name, address, rssi)
        await new_device.refresh_state()
        return new_device

    def __init__(self, address: str, name: str, rssi: int | None = None):
        """MagicStripDevice."""
        self.name = name
        self.address = address
        self.rssi = rssi
        self._on: bool | None = None
        self._brightness: int | None = None
        self._color: tuple[int, int, int] | None = None
        self._effect: str | None = None
        self._effect_speed: int | None = None

        self._power_status_millis: datetime | None = None

        self.lock = asyncio.Lock()
        self._client = BleakClient(self.address)
        self._client_count = 0

        _LOGGER.info(
            "Found %s (%s), Signal Strength: %s (%s)",
            self.name,
            self.address,
            _judge_rssi(self.rssi),
            self.rssi,
        )

    async def __aenter__(self) -> MagicStripDevice:
        """Enter context."""
        async with self.lock:
            if self._client_count == 0:
                try:
                    await self._client.__aenter__()
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on connect", exc_info=True)
                    raise BleConnectionError("Timeout on connect") from exc
                except BleakError as exc:
                    _LOGGER.debug("Error on connect", exc_info=True)
                    raise BleTimeoutError("Error on connect") from exc
            self._client_count += 1
            return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Exit context."""
        async with self.lock:
            self._client_count -= 1
            if self._client_count == 0:
                await self._client.__aexit__(exc_type, exc_val, exc_tb)

    def _onoff_notification_handler(self, sender, data) -> None:  # type: ignore
        """Handle HCI event notifications."""

        """
        Connection workflow:
        1. Write 0xF0 to CHARACTERISTIC_UUID (Triggers 0xF00201 response.)
        2. Write 0x0F to CHARACTERISTIC_UUID (Returns state string.)
        3. Write 0x0100 to attribute handle 4 (Unsure of purpose. Ignoring.)
        4. Receive 0xF00201 from device (Seems to be generic acknowledgement.)
        5. Receive current status message from device in format 0F WW XX YY ZZ, where:
            a. WW = 00 for 'off', 01 for 'on'
            b. XX = brightness (0: Min Brightness - 255: Max brightness)
            c. YY = last used effect speed (0: Fastest - 255: Slowest)
            d. ZZ = last used effect, with ZZ being the second byte of the effect commands starting with 0x07.

        Unfortunately, the device doesn't report current color or whether an effect is currently active, rendering
        ZZ useless.
        """

        if self._power_status_millis and (
            (datetime.now() - self._power_status_millis) > timedelta(seconds=10)
        ):
            _LOGGER.debug(
                "%s: Message received outside of acceptable time range. Ignoring.",
                self.address,
            )
            self._power_status_millis = None
            return

        if bytearray.hex(data) == const.CMD_ACK:
            # Prepare to receive on/off status
            _LOGGER.debug(
                "%s: Received status message preamble. Waiting for status message...",
                self.address,
            )
            self._power_status_millis = datetime.now()
            return

        status_components: re.Match | None
        if (
            status_components := re.search(const.STATUS_REGEX, bytearray.hex(data))
        ) is not None:

            self._on = status_components.group(1) == "01"
            self._brightness = int(status_components.group(2), 16)

            _LOGGER.debug(
                "%s: Device status reported as %s. On: %s, Brightness: %s",
                self.address,
                bytearray.hex(data),
                self._on,
                self._brightness,
            )

    async def refresh_state(self) -> None:
        """Query device for current power and brightness states."""

        _LOGGER.debug("Refreshing state.")

        async with self:
            async with self.lock:
                try:
                    _LOGGER.debug("%s: Connected", self.address)

                    await self._client.start_notify(
                        CHARACTERISTIC_UUID, self._onoff_notification_handler
                    )

                    await self._client.write_gatt_char(
                        CHARACTERISTIC_UUID, bytes.fromhex("F0"), True
                    )
                    await self._client.write_gatt_char(
                        CHARACTERISTIC_UUID, bytes.fromhex("0F")
                    )

                    # await self._client.write_gatt_descriptor(4, bytes.fromhex("0100"))

                    await self._client.stop_notify(CHARACTERISTIC_UUID)
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on update", exc_info=True)
                    raise BleTimeoutError from exc
                except BleakError as exc:
                    _LOGGER.debug("Failed to update", exc_info=True)
                    raise BleConnectionError("Failed to update device") from exc

    @property
    def brightness(self) -> int | None:
        """Return current brightness."""
        return self._brightness

    @property
    def is_on(self) -> bool | None:
        """Return current brightness."""
        return self._on

    @property
    def color(self) -> tuple[int, int, int] | None:
        """Return current color."""
        return self._color

    @property
    def effect(self) -> str | None:
        """Return current effect."""
        return self._effect

    @property
    def effect_speed(self) -> int | None:
        """Return current effect speed."""
        return self._effect_speed

    @property
    def effects_list(self) -> list:
        """Get list of effects."""

        return list(EFFECTS)

    async def _send_command(self, cmd: str | list, attempts: int = 1) -> None:
        """Send given command."""

        if isinstance(cmd, list):
            for cmd_single in cmd:
                await self._send_command(cmd_single)
            return

        async with self:
            async with self.lock:
                try:
                    _LOGGER.debug("Sending command: %s", cmd)
                    await self._client.write_gatt_char(
                        CHARACTERISTIC_UUID, bytes.fromhex(cmd)
                    )
                    await self._client.write_gatt_char(
                        CHARACTERISTIC_UUID, bytes.fromhex("F0")
                    )
                except asyncio.TimeoutError as exc:
                    _LOGGER.debug("Timeout on write", exc_info=True)
                    raise BleTimeoutError from exc
                except BleakError as exc:
                    _LOGGER.debug("Failed to write", exc_info=True)
                    raise BleConnectionError("Failed to write") from exc
                except OSError:
                    _LOGGER.debug("Encountered OSError.")
                    if attempts <= 2:
                        _LOGGER.debug(
                            "Assuming connection has been closed. Trying again..."
                        )
                        self._send_command(cmd, attempts + 1)
                    else:
                        raise

    async def set_color(self, red: int, green: int, blue: int) -> None:
        """Set strip to specified color; no effects."""

        """
        Command submission workflow:
        1. Write command CHARACTERISTIC_UUID.
        2. Write 0xF0 to CHARACTERISTIC_UUID (Triggers 0xF00201 response.)
        3. Receive 0xF00201 from device (Seems to be generic acknowledgement.)

        It's easier to send a forget, so we've just implemented step 1.
        """

        for color in (red, green, blue):
            if not 0 <= color <= 255:
                raise OutOfRange

        self._color = (red, green, blue)
        self._effect_speed = None
        self._effect = None

        await self._send_command(f"03{''.join(f'{i:02x}' for i in self._color)}")

    async def set_brightness(self, brightness: int) -> None:
        """Set strip to specified brightness; no effects."""

        if not 0 <= brightness <= 255:
            raise OutOfRange

        self._brightness = brightness

        await self._send_command(f"08{''.join(f'{brightness:02x}')}")

    async def set_effect(self, effect: str, speed: int = 128) -> None:
        """Set strip to specified effect."""

        if (not 0 <= speed <= 255) or (effect not in list(EFFECTS)):
            raise OutOfRange

        self._effect_speed = speed
        self._effect = effect
        self._color = None

        effect_cmd = EFFECTS[effect]
        speed_cmd = f"09{speed:02x}"

        await self._send_command([effect_cmd, speed_cmd])

    async def toggle_power(self) -> None:
        """Set strip to specified effect."""

        await self._send_command(TOGGLE_POWER)
