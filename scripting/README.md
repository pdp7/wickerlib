# Scripts

Documenting the scripts.

### Generate library list

This script checks all .kicad_mod footprint files in a specified directory, checks those files for 'Verified' and 'Finished' header lines, and creates a sorted table in Markdown that lists the name of the footprint and its status. 

The output can be <a href="https://github.com/wickerbox/wickerlib/tree/master/libraries/Wickerlib.pretty">seen in action here</a>, but you have to scroll down a lot. 

### Kingfisher

Kingfisher is the workhorse to automate creating KiCad projects, generating stencil and manufacturing files, creating bills of material, packaging everything so it's ready to upload for ordering, and building a beautiful documentation PDF.



