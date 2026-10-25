## Components

```text
Component                         Quantity / purpose
Arduino UNO R4 Minima              1; controller and built-in clock
MG995 positional servo            1; both geared jaws
MG90S positional servo            1; tongue drum
External regulated 4.8 V supply    1; sized for both servos' peak current
USB-C cable + USB power           1; Arduino power/programming
Wires and power connectors        As needed; shared ground
Printed V6 parts                  Head, gears, tongue, stem, rims, clips,
                                  push pins, separate teeth and custom hubs
Nonstretch string                 0.4-0.6 mm; start with at least 500 mm
Soft elastic                      About 0.8 mm; six ~80 mm pieces + spare
Cardboard or curved foamcore      98 mm-high pot sleeve, plus seam
Optional DS3231 RTC + battery      1; retain time while power is off
Optional TM1637 display            1; show the time
Optional passive piezo + 1 kOhm    1 each; two-note cuckoo sound
```

## The mechanism

The head moves about 50 degrees and the lower jaw about 12.5 degrees in the opposite direction. Only the working quadrant of the larger gear is printed. The tongue has seven sections with captive hinges, so it prints as one assembly and needs its string and elastic threaded through it.

To save material, the teeth slot into the jaws separately, the connector pins print flat, and the pot uses printed rims around a sheet-material sleeve. The parts are arranged across eight 240 x 240 mm print beds.

## Wiring

```text
Connection                        Destination
MG995 signal (orange/yellow)       UNO D7
MG90S signal (orange/yellow)       UNO D6
Both servo red wires              External 4.8 V supply +
Both servo brown/black wires      External supply -
UNO GND                           External supply - (common ground)
UNO USB-C                         Computer / USB power supply
```

```text
UNO D7 --------------------------- MG995 signal
UNO D6 --------------------------- MG90S signal
External 4.8 V + ----+------------- MG995 red
                    +------------- MG90S red
External supply - --+------------- Both servo grounds
                    +------------- UNO GND
USB ------------------------------ UNO USB-C
```

The servos use their own supply with a common ground, following [Arduino's servo power guidance](https://support.arduino.cc/hc/en-us/articles/360017053760-Troubleshoot-servo-motors). They do not run from the UNO's 5 V pin. The required peak current still needs measuring on the assembled mechanism.

