# DIP template for the C.H.I.P. $9 Computer

This is a KiCad template set up with OSH Park's design rules to simplify making DIP daughter boards (wings, shields, hats, etc.) 

### CHIP DIP Shield Blank Template

This is the blank template. You can download the zip file containing the project and libraries here.

To use the template:

1. Download and extract the zip into a folder.
1. Rename all the files to replace `chip-dip-blank` with your filename. 
1. Open the project file in KiCad.
1. Add your libraries, add your parts, wire them up.
1. When you're ready to start layout, create the new netlist. 
1. Go to PCBNew and import the new netlist. 
1. Lay out your board! The existing headers are locked in place, but don't try to move them.
1. You can upload the .kicad_pcb file directly to oshpark.com to check the preview images.

### CHIP DIP Protoboard Example

Using the blank template, I followed those steps to create an empty protoboard. None of the inner holes are connected, so you can solder them any way you'd like. You can also add a mini breadboard instead of soldering in place, at least at first.

<img src="chip-dip-schematic.png">

<img src="chip-dip-oshpreview.png">

**Bill of Materials**

The board costs $17.50 for a set of three boards.

To make three full protoboards, you'll need 2x20 0.1" headers. I recommend <a href="http://www.digikey.com/product-detail/en/sullins-connector-solutions/SFH11-PBPC-D20-ST-BK/S9200-ND/1990093">these Sullins connectors</a> from Digikey, but any compatible ones will work.  
