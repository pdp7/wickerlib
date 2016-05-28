# KiCad DIP Template for the C.H.I.P Computer

This is a KiCad template to simplify making DIP daughter boards (wings, shields, hats, etc.) 

It comes with all the design rules to meet the 2-layer OSH Park specs and stackup.

- <a href="http://docs.oshpark.com/services/two-layer/">OSH Park Two Layer Specs</a>
- <a href="http://docs.oshpark.com/design-tools/kicad">OSH Park KiCad Help</a>
- <a href="https://getchip.com/pages/chip">CHIP Homepage</a>
- <a href="http://www.chip-community.org/index.php/DIPs">CHIP Community DIPS page</a>

### Instructions

1. Open KiCad.
1. Open Preferences > Configure Paths and note the value of 'KICAD_PTEMPLATES'.
1. <a href="https://github.com/wickerbox/wickerlib/blob/master/templates/chip-dip-template.zip?raw=true">Download the template zip</a> and extract into the location of 'KICAD_PTEMPLATES'.
1. Cut and paste the .lib and .dcm files into your component/symbol library folder. 
1. Cut and paste the .pretty folder into your your module/footprint library folder. 
1. In KiCad, open File > New Project > New Project from Template.
1. Select the location of your new project. The name of the folder will be the name of your project.
1. The templates with folders in the 'KICAD_PTEMPLATES' are listed under 'Portable Templates" tab.
1. Select the template and click 'OK'.
1. Your project now exists, so you can open EESchema and PCBNew and design as usual.

### CHIP DIP Protoboard Example

Using the blank template, I followed those steps to create an empty protoboard, which is available <a href="https://github.com/wickerbox/Protoboard-DIP-for-CHIP">in its own repo here</a>.

