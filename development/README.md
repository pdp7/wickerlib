## Creating Wickerlib 
Creating the wickerlib.lib, wickerlib.dcm, and Wickerlib.pretty libraries. 

##### Create a Reference List of Parts

I created an inventory CSV file with the following categories: 

- WBoxSKU
- Reference
- Description
- Value
- KiCadFootprint
- Datasheet
- Package
- MF_Name
- MF_PN
- S1_Name
- S1_PN
- Verified

I created a script that will only read in inventory.csv rows where the Reference is a letter, so it ignores the title line and lines where Reference is a dash or empty.

##### Ways to Use the Libs

1. I create a wickerlib component library of just the symbols with empty fields. The fields are there so they come into the schematic but they're empty. I lay out the schematic, I create new symbols where required, and then when I'm ready, I can start filling in the part information. I could reference my own inventory at that point if I wanted to, but I'd still have to add in the information for every part individually, which can be tedious and error-prone. Still, it would work. I would associate footprints at that point, and then I would create a beautiful BOM.

1. I create a wickerlib component library of actual components based on WBox SKU parts with all the information. There are very quickly several hundred components based on only about 150 symbols pictures. Placing a component involves choosing the final footprint, or at least choosing a placeholder and knowing I need to come back to it later. This could also be error-prone. 

  1. The error might be limited by adding a field called FINAL and leaving it blank until the final footprint is chosen. Updates in the schematic don't affect the original libraries.

  1. One use case that worries me is if I add a bunch of parts and then need to change some info on them. If I've got them as full components associated with SKUs in the first place, I can just delete the existing and replace directly with another existing library component. If I only have the symbol, I'll have to manually edit the fields to make the change.  


##### Get the list of symbols

The name of the symbol comes from the Value field. 

For wickerlib, the Value field needs to use dashes instead of spaces. Here's a full list of the symbols we're about to create 131 symbols we need to create:

- 2PIN-SHUNT
- 74HC4050
- 74HC595
- AAT3221
- AD9833
- ADAFRUIT PRO MINI 5V
- ANTENNA
- AP3012
- ARDU PRO MINI 5V
- ARDUINO UNO R3
- ARDUINO-101
- ARDUINOSHIELD
- ATMEGA1284-44TQFP
- ATMEGA328-32TQFP
- ATTINY85
- ATTINY861V
- BATTERY
- BU33SD5WG
- C707SIM
- CAP
- CONN-1x01
- CONN-1x02
- CONN-1x03
- CONN-1x04
- CONN-1x05
- CONN-1x06
- CONN-1x07
- CONN-1x08
- CONN-1x09
- CONN-1x10
- CONN-1x11
- CONN-1x12
- CONN-1x13
- CONN-1x14
- CONN-1x15
- CONN-1x16
- CONN-1x17
- CONN-1x18
- CONN-1x19
- CONN-1x20
- CONN-1x25
- CONN-2x02
- CONN-2x03
- CONN-2x05
- CONN-2x09
- CONN-2x15
- CONN-2x20
- CONN-2x25
- CONN-2x5-JTAG
- CONN-3x04
- CONN-BNC
- CONN-DB9-FEMALE
- CONN-DB9-MALE
- CONN-SD
- CONN-SMA
- CONN-USB-A
- CP2102
- DIODE
- DIODE-SCHOTTKY
- DIODE-TVS
- DIODE-ZENER
- EM-506-GPS
- FONA-808
- FT232H
- FTDIFRIEND
- GPS MTK3329
- HALL
- IND-SINGLE
- JACK-BARREL
- JACK-STEREO
- KEYPAD
- LAMP
- LCD-1602
- LD29300
- LED
- LED-2-COMMON-CAT
- LED-3-COMMON-ANODE
- LED-NEOPIXEL-4PIN
- LM1117
- LM317
- LM339PWR
- LM358
- LT1115
- MAX2769
- MAX31855
- MC7809
- MCP1703
- MCP23008
- MCP2551
- MCP73831T-2ACI/OT
- MCP73833
- MIC
- MMA7660
- MPU6000
- MPU9150
- NANITE841
- NCP1117
- NCP7805
- NJM386
- OPA356
- OSC-2PIN
- OSC-4PIN
- RESISTOR
- SN74CB3Q3257
- SPEAKER
- SPX29300
- STM32F042-32LQFP
- STM32F407-100LQFP
- STN1110
- SWITCH-5WAYNAV
- SWITCH-SPDT
- SWITCH-SPST
- SWITCH-TPA511GS
- TC2185
- TEENSY2.0
- TEENSY3.1
- TEENSY3.2
- TL081CP
- TLE2426
- TMP36
- TRANS-BJT-NPN
- TRANS-BJT-PNP
- TRANS-FET-N
- TRANS-FET-P
- TRIMPOT-3PIN
- TXB0104
- UC15
- USB-MICRO-B
- USB-PHY-3318
- VNH5019
- XC9140

##### What does wickerlib.lib look like?



##### What symbols de we need for most of the items?


