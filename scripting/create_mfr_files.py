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
      - SVG files for easy adding to Github repository READMEs      
      - one PDF file containing all info

    TODO: add warnings, such as empty edge.cuts files.

'''

import sys, os, zipfile, glob

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

# remove all files in the output dir
os.chdir(plotDir)
filelist = glob.glob('*')
for f in filelist:
  os.remove(f)
os.chdir('..')

# create plot controller objects

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
popt.SetSubtractMaskFromSilk(False)

popt.SetUseAuxOrigin(False)        # must be set true
# is this because I didn't set one in KiCad itself?
# all the pdfs were coming out empty

# Note: the middle value in plot_plan is an integer layer number:
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

pctl.SetLayer(F_Fab)
pctl.OpenPlotfile("AssyOutlinesTop", PLOT_FORMAT_PDF, "Assembly outline top")
pctl.PlotLayer()

# Close out the plot to safely free the object.
pctl.ClosePlot()

# Create Enhanced Excellon and PDF drill files

drlwriter = EXCELLON_WRITER( board )
drlwriter.SetMapFileFormat( PLOT_FORMAT_PDF )

mirror = False
minimalHeader = False
offset = wxPoint(0,0)

mergeNPTH = False 
metricFmt = True
genDrl = True
genMap = True

drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )
drlwriter.SetFormat( metricFmt )
drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), genDrl, genMap );

# Create the drill statistics report

rptfn = pctl.GetPlotDirName() + 'drill_report.rpt'
drlwriter.GenDrillReportFile( rptfn );

# Create bill of materials with position information

# Create zip file for OSH Park manufacturing

files = []

for ext in ('*.drl','*.gbl','*.gtl','*.gbo','*.gto','*.gbs','*.gts','*.gbr','*.gm1','*.gtp','*.gbp',):
  files.extend(glob.glob(os.path.join(plotDir, ext)))

os.chdir(plotDir)
ZipFile = zipfile.ZipFile(filename.rstrip('.kicad_pcb')+"-gerbers.zip", "w")
for f in files:
  ZipFile.write(os.path.basename(f))
os.chdir("..")

# Create zip file for OSH Stencils
# always using .gm1 (outline) and .gtp,.gbp (paste) files

files = []

for ext in ('*.gm1','*.gtp','*.gbp'):
  files.extend(glob.glob(os.path.join(plotDir, ext)))

os.chdir(plotDir)
ZipFile = zipfile.ZipFile(filename.rstrip('.kicad_pcb')+"-stencils.zip", "w")
for f in files:
  ZipFile.write(os.path.basename(f))
os.chdir("..")

# Create zip file of the complete assembly package

# Create images

plotDir = "."

pctl.SetLayer(F_Fab)
popt.SetTextMode(PLOTTEXTMODE_STROKE)
pctl.OpenPlotfile("Assembly", PLOT_FORMAT_SVG, "Assembly outline top")
pctl.PlotLayer()

# Fix up the images 
  # Definitely want to trim every svg in the folder to remove whitespace
  # plt.savefig("test.png",bbox_inches='tight')


