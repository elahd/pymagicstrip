# pymagicstrip

## Purpose

Minimal python library for controlling LED controllers that use the MagicStrip iOS/Android app. These are inexpensive, white labeled controllers that are available on Amazon, AliExpress, etc. under brand names that include TOPMAX and L8star.

The firmware on these devices is terrible so feature support is spotty.

## Device Support

This library only supports RGB LED strips that appear in the MagicStrip app under the name "HTZM". RGBW, RGBWW, etc. devices are not currently supported.

## Feature Support

| Feature            | Read Property | Set Property | Notes                                                                                                                                               |
| ------------------ | ------------- | ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| Power              | ✅            | ⚠️           | Device firmware does not have discrete on and off commands. This library can only toggle state.                                                     |
| Brightness         | ✅            | ✅           |                                                                                                                                                     |
| Color              | 🚫            | ✅           |                                                                                                                                                     |
| Effects            | 🚫            | ✅           | We _technically_ can read this property, but the device does not report whether it is in solid color mode or effect mode, so the report is useless. |
| Effect Speed       | 🚫            | ✅           | (See above.)                                                                                                                                        |
| Sound / Music Mode | 🚫            | 🚫           |                                                                                                                                                     |

## Use

This library is based on the python [bleak](https://github.com/hbldh/bleak) library and does not abstract/wrap all features. You must use bleak directly alongside pymagicstrip.

For usage examples, see https://github.com/elahd/ha-magicstrip. (Apologies for the lack of clear examples here.)

## Guts

**Processor:** Lenze Technology ST17H26 ([Datasheet [PDF]](https://datasheet.lcsc.com/lcsc/1811151231_LENZE-ST17H26_C326547.pdf)). This is a OTP microcontroller with built-in BLE functions.

**EEPROM:** Atmel AT24C02N ([Datasheet [PDF]](https://www.datasheet-pdf.info/attach/1/8092160401.pdf)). 2K memory chip.

These are reference photos of the interior of the device.

![IMG_5148](https://user-images.githubusercontent.com/466460/154529818-287ebec6-6a67-422d-ba1e-d23f9935892a.jpg)

![IMG_5173](https://user-images.githubusercontent.com/466460/154529815-5be15a7e-8b00-4ce3-81fc-574e6d70fa02.jpg)

## Credit

Pymagicstrip is heavily based on elupus' [Fjäråskupan Bluetooth Control library](https://github.com/elupus/fjaraskupan).
