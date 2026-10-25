# UNO R4 Minima wiring and firmware

Open [geared_clock.ino](../firmware/geared_clock/geared_clock.ino) in Arduino IDE, select **Arduino UNO R4 Minima**, and install **Servo by Arduino**. `RTC` and `Wire` come with the UNO R4 board package. Serial Monitor: **115200 baud**, newline or both NL & CR.

The default build uses the UNO R4 Minima's built-in clock, one MG995 for both geared jaws, and one MG90S for the tongue drum. This sketch requires `SET` after each reset/upload in built-in-clock mode. The Minima has no exposed RTC battery-backup pin. A DS3231 is optional for retaining time through power loss.

## Wiring table

| Part / terminal | Connect to | Purpose |
|---|---|---|
| MG995 signal, usually orange/yellow | UNO D7 | Both geared jaws |
| MG90S signal, usually orange/yellow | UNO D6 | Tongue drum |
| Both servo red wires | External regulated 4.8 V supply + | Motor power |
| Both servo brown/black wires | External supply - | Motor return |
| UNO GND | External supply - | Shared signal reference |
| UNO USB-C | Computer or USB supply | Board power |
| Optional DS3231 SDA / SCL | UNO SDA (A4) / SCL (A5) | I2C clock module |
| Optional DS3231 VCC / GND | UNO 5 V / GND | Compatible 5 V breakout only |
| Optional TM1637 CLK / DIO | UNO D3 / D4 | Display interface |
| Optional TM1637 VCC / GND | UNO 5 V / GND | Compatible 5 V module |
| Optional passive piezo + / - | D8 through 1 kOhm / GND | Two-note cuckoo |

Use a separate regulated **4.8 V servo supply** sized for both servos' peak current. The required current has not been measured on the assembled mechanism. Run motor power directly from the supply using suitable wire/connectors. **Do not power either servo from the UNO 5 V pin.** Keep the external positive rail separate from the UNO's USB-powered 5 V rail; join their grounds. Verify connector polarity because wire colors vary.

```text
USB ----------------------------- UNO R4 Minima
UNO D7 -------------------------- MG995 signal
UNO D6 -------------------------- MG90S signal
External 4.8 V + -----+----------- MG995 red
                     +----------- MG90S red
External supply - ---+----------- MG995 brown/black
                     +----------- MG90S brown/black
                     +----------- UNO GND
```

The optional sound output is for a passive piezo element with a 1 kOhm series resistor, not an 8-ohm speaker or a high-current buzzer. Choose the DS3231 battery according to the breakout's charging circuit and documentation.

## Optional modules

Set `USE_DS3231`, `USE_DISPLAY`, or `USE_BUZZER` to `true` for the modules you connect. All default to `false`. DS3231/TM1637 interface code is included; no extra libraries are needed. With `USE_DS3231=true`, `SET` updates the external clock. Missing/invalid RTC data disables hourly triggering but not `DEMO`. An enabled display shows four dashes when time is invalid.

## Calibration

1. Leave the MG995 carrier/custom hub off its shaft and the string off the MG90S drum. Upload. By default there are **no servo pulses at startup**. The first `HOME`, `JAW`, or `TONGUE` command attaches the corresponding servo(s), which may move immediately; start unloaded.
2. Send `JAW 1500` or `TONGUE 1500` to position one bare servo. Change in small increments, such as 10 microseconds, while checking direction and available travel. These commands move immediately and are for disconnected drives. The accepted 800..2350 microsecond range is a software input limit, not a guaranteed safe range for your servo.
3. Replace the four endpoint constants with measured values. Current estimates are jaw **1100 to 1656 microseconds**, tongue **850 to 2313 microseconds**. Target a 50-degree upper-jaw swing (lower jaw moves 12.5 degrees oppositely) and about 131.7 degrees at the 10 mm drum, taking up about 23.0 mm of string. Reverse the corresponding endpoint pair if rotation is reversed. Never force a servo against its stop.
4. Send `HOME` unloaded and wait about 3 seconds. Turn power off, fit the custom hubs at the closed-jaw/curled-tongue datum, install the printed keepers and connect the string. Start the assembled mechanism in this rest pose. Test initially with reduced travel, then increase gradually.
5. Send `HOME`, wait for `STATUS` to report `homed=1 stage=0`, then `ARM` and `DEMO`. Verify that the tongue physically curls fully before jaw closure. Increase `TONGUE_IN_MS` if needed and tune the elastic/friction. `homed=1` means the commanded return finished; no sensor confirms position.

Manual calibration commands do not save settings to flash. Put final endpoints into the sketch and upload again. If the MG90S cannot achieve the required travel comfortably, revise the drum/mechanical setup before connecting its tendon.

## Commands

| Command | Behavior |
|---|---|
| `SET 2026-10-25 14:59:50` | Example only: replace with actual local time |
| `STATUS` | Reports time, armed state, commanded-home state and stage |
| `HOME` | Disarms, releases tendon, then closes jaw; first use may move immediately |
| `ARM` | Enables cycles after HOME completes |
| `DEMO` | One cycle when armed and idle; works without time set |
| `DISARM` | Stops sequence/sound; servos keep holding the last commanded positions |
| `JAW 1500` / `TONGUE 1500` | Immediate unloaded calibration, only while disarmed and idle |
| `HELP` | Prints command list |

Timing: 1200 ms jaw opening, 900 ms tongue extension, 520 ms hold/chirp, 1200 ms tongue return, 1200 ms jaw closure, 350 ms rest. Motion uses `millis()` and smooth interpolation. Neither `DISARM` nor `HOME` cuts motor power or senses an obstruction.

Hourly cycles run from 08:00 through 21:00, repeating 1-12 times to match the hour. Missed hours are not replayed; `DEMO` ignores quiet hours. Time is local, with no automatic daylight-saving adjustment. The sketch starts disarmed after reset. `AUTO_ARM_AFTER_CALIBRATION=true` attaches both servos at rest and arms on startup; use only after testing because startup can move them. Internal-clock mode still needs `SET` after reset. Use a valid battery-backed DS3231 for unattended timekeeping through power loss.

## References and verification

- [Arduino Minima RTC guide](https://docs.arduino.cc/tutorials/uno-r4-minima/rtc/) and [UNO board comparison](https://support.arduino.cc/hc/en-us/articles/9350551575964-What-s-the-difference-between-UNO-R3-and-UNO-R4-boards).
- [Arduino servo power/common-ground guidance](https://support.arduino.cc/hc/en-us/articles/360017053760-Troubleshoot-servo-motors).
- [TowerPro MG90S specifications](https://towerpro.com.tw/product/mg90s-3/) list 4.8 V operation and an external adapter.

See [firmware validation](../validation/firmware.json) for compile results. Compilation does not verify physical travel, spline grip, elastic return, current demand or sound. The code has not been uploaded or bench-tested by this workflow.
