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

board = LoadBoard(filename)

plotDir = "gerbers/"

pctl = PLOT_CONTROLLER(board)
popt = pctl.GetPlotOptions()
popt.SetOutputDirectory(plotDir)

# Set plot options

popt.SetPlotFrameRef(False)        # do not change it
popt.SetLineWidth(FromMM(0.35))
popt.SetAutoScale(False)           # do not change it
popt.SetScale(1)                   # do not change it
popt.SetMirror(False)
popt.SetUseGerberAttributes(True)
popt.SetUseGerberProtelExtensions(True)
popt.SetExcludeEdgeLayer(False)
popt.SetScale(1)
popt.SetUseAuxOrigin(True)
popt.SetSubtractMaskFromSilk(False)

# this doesn't generate anything with F_Fab or F_SilkS
# I want it on the Fab layer since that's where my assy info is
# It might just be out of place
#pctl.SetLayer(F_Fab)
#pctl.OpenPlotfile("Fab", PLOT_FORMAT_PDF, "Assembly diagram")
#pctl.PlotLayer()

# The middle value is an integer layer number:
# F.Cu      0
# B.Cu      31
# F.Paste   35
# B.Paste   34
# F.Silk    37
# B.Silk    36
# F.Mask    39
# B.Mask    38
# Edge.Cuts 44
# F.Fab     49
# B.Fab     48

plot_plan = [
    ( "F.Cu", F_Cu, "Top layer" ), 
    ( "B.Cu", B_Cu, "Bottom layer" ),
    ( "F.Paste", F_Paste, "Paste top" ),
    ( "B.Paste", B_Paste, "Paste Bottom" ),
    ( "F.Silk", F_SilkS, "Silk top" ),
    ( "B.Silk", B_SilkS, "Silk top" ),
    ( "F.Mask", F_Mask, "Mask top" ),
    ( "B.Mask", B_Mask, "Mask bottom" ),
    ( "Edge.Cuts", Edge_Cuts, "Board outline" ),
    ( "F.Fab", F_Fab, "Assembly top" ),
    ( "B.Fab", B_Fab, "Assembly bottom" ),
]

# Generate all gerbers
for layer_info in plot_plan:
    pctl.SetLayer(layer_info[1])
    pctl.OpenPlotfile(layer_info[0], PLOT_FORMAT_GERBER, layer_info[2])
    pctl.PlotLayer()

#generate internal copper layers, if any
lyrcnt = board.GetCopperLayerCount();

for innerlyr in range ( 1, lyrcnt-1 ):
    pctl.SetLayer(innerlyr)
    lyrname = 'In.%s' % innerlyr
    pctl.OpenPlotfile(lyrname, PLOT_FORMAT_GERBER, "Inner")
    #print 'plot %s' % pctl.GetPlotFileName()
    if pctl.PlotLayer() == False:
        print "Plot Error: Layer Missing?"

# Close out the plot to safely free the object.
pctl.ClosePlot()


