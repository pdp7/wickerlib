# Scripts

Documenting the scripts.

### Generate library list

This script checks all .kicad_mod footprint files in a specified directory, checks those files for 'Verified' and 'Finished' header lines, and creates a sorted table in Markdown that lists the name of the footprint and its status. 

The output can be <a href="https://github.com/wickerbox/wickerlib/tree/master/libraries/Wickerlib.pretty">seen in action here</a>, but you have to scroll down a lot. 

### Kingfisher

Kingfisher is the workhorse to automate creating KiCad projects, generating stencil and manufacturing files, creating bills of material, packaging everything so it's ready to upload for ordering, and building a beautiful documentation PDF.

**Create a New Project**

This creates a new subfolder in the current directory, and copies in the specified template and json file. 

`kf projectname -n`

To specify `crazy` or `wickerbox` project templates, use the `-t` flag:

`kf projectname -n -t wickerbox`

**Create the manufacturing files**

A .kicad_pcb file must exist but a netlist isn't necessary. The program creates a gerber preview. 

`kf projectname -m`

**Create the bill fo materials and assembly files**

A netlist must exist. The program creates an assembly diagram and all the bill of materials files. 

`kf projectname -b`

**Create the PDF documentation**

This will create a PDF from whatever exists. If it fails to incorporate some expected piece, it should warn you. 

`kf projectname -p`

**Create all output files at once**

The flags cann be combined, and the program will treat them as if called in the order so manufacturing files are first, then bill of materials, then the PDF. 

`kf projectname -b -m -p`
