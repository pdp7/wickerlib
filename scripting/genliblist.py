# Scan all parts and build a Markdown table list
# Create a README file in the footprint library directory
# Table looks like this:
# |Footprint|Verified|

import os
import glob
import datetime

# collect a list of all filenames 

libdir = "/home/wicker/wickerlib/libraries/Wickerlib.pretty/"
modules = glob.glob(libdir+'*.kicad_mod')
modules = sorted(modules)

liblist_output = []

# search all files in the glob for the verified status

for module_path in modules:
  with open(module_path, 'r') as module:
    for line in module:
      if 'Verified' in line:
        line_verify = line.lstrip('# Verified: ').rstrip('\n')
        if 'ICSP' in line:
          mod_name = 'ARDUINO-UNO-WITH-ICSP'
        else:
          mod_name = module_path.lstrip(libdir).rstrip('.kicad_mod')
        liblist_output.append('| '+mod_name+' | '+line_verify+' |')

outfile_path = 'README.md'
today = datetime.datetime.today()
dt = today.strftime("%d %B %Y")

with open(outfile_path,'w') as o:
  o.write("# Wickerlib.pretty KiCad Module (Footprint) Library")
  o.write("\nThese modules have been edited to have fabrication information for wickerlib. They all come with comments in the headers of each that includes attribution, the appropriate license, and whether the footprint has been used successfully in a project.")
  o.write("\nIt is always the end user's responsibility to verify the package.") 
  o.write("\n\nThis list is updated each time the repository is updated.")
  o.write("\n\nLast updated: "+dt)
  o.write("\n\n|Module Name|Verified|")
  o.write("\n|------|--------|")
  for l in liblist_output:
    o.write("\n"+l)
