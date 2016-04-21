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


