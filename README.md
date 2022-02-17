# pymagicstrip

## Purpose

Minimal python library for controlling LED controllers that use the MagicStrip iOS/Android app. These are inexpensive, white labeled controllers available on Amazon, AliExpress, etc.

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

## Credit

Pymagicstrip is heavily based on elupus' [Fjäråskupan Bluetooth Control library](https://github.com/elupus/fjaraskupan).
