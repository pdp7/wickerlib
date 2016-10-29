'''
    This script is partly based on these KiCad example files:

      https://github.com/KiCad/kicad-source-mirror/tree/master/demos
      - plot_board.py
      - gen_gerber_drill_files_board.py 

    This script inherits the GPLv3 license from KiCad.
    Modifications were made by Jenner Hanni <jenner@wickerbox.net>

    This script is to be run from the command line to create:
      - gerber and drill files for manufacturing
      - bill of materials in Markdown and CSV formats
      - a zip file of gerbers with the version number
      - a zip file of stencil files with the version number
      - a zip file of the complete files ready for assembly
      - composite zip file with everything for assembly
      - SVG files for easy adding to Github repository READMEs      
      - one PDF file containing all info

'''

import sys

from pcbnew import *

# handles the argument and sets filename
# adds .kicad_pcb ending if necessary

if len(sys.argv) > 1:
  if '.kicad_pcb' not in sys.argv[1]:
    filename=sys.argv[1]+'.kicad_pcb'
  else:
    filename=sys.argv[1]
else:
  print "Error: This script needs the root project name.\nUsage: 'create_mfr_files.py filename'"
  exit()

print filename


