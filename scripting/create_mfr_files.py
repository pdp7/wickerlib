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
    TODO: integrate position information to create assembly zip file
    TODO: automatically trim whitespace away from SVG files

'''

import sys, os, zipfile, glob, argparse

from pcbnew import *

# capture command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n","--name", nargs=1, help="project name", required=True)
parser.add_argument("-v","--version", nargs=1, help="version number, 'v1.1'")

args = parser.parse_args()

# handles the argument and sets filename
# adds .kicad_pcb ending if necessary

if args.version:
  version = '-'+args.version[0]
else:
  version = ''

if '.kicad_pcb' not in args.name[0]:
  filename=args.name[0]+'.kicad_pcb'
else:
  filename=args.name[0]

board = LoadBoard(filename)
plotDir = "gerbers/"

if not os.path.exists(plotDir):
    os.makedirs(plotDir)

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
popt.SetExcludeEdgeLayer(True)
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

mergeNPTH = True
metricFmt = True
genDrl = True
genMap = True

drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )
drlwriter.SetFormat( metricFmt )
drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), genDrl, genMap );

# Create the drill statistics report

rptfn = pctl.GetPlotDirName() + 'drill_report.rpt'
drlwriter.GenDrillReportFile( rptfn );

# Create bill of materials 

bomfile = args.name[0]+'.csv'
bom_outfile_csv = args.name[0]+'-bom.csv'
bom_outfile_md = args.name[0]+'-bom.md'

vendors = []

# figure out what vendors are necessary

which_line = 0
with open(bomfile,'r') as ibom:
  for line in ibom:
    if which_line is 0:
      which_line = 1
    else:
      l = line.split(',')
      vendors.append(l[9].lower())
  vendors = set(vendors)

# create the master CSV with vendor information
 
outbom_list = []
outfile = args.name[0]+'-bom.csv'

which_line = 0
with open(bomfile,'r') as ibom:
  for line in ibom:
    l = line.split(',')
    outbom_list.append(l[0]+','+l[3]+','+l[11]+','+l[7]+','+l[8]+','+l[9]+','+l[10])

with open(outfile,'w') as obom:
  for line in outbom_list:
    obom.write(line+'\n')

# Create a markdown file for github with each vendor
# given its own table for easy reading

outbom_list = []
outfile = args.name[0]+'-bom.md'

for v in vendors:
  which_line = 0
  with open(bomfile,'r') as ibom:
    for line in ibom:
      if which_line is 0:
        outbom_list.append('|Ref|Qty|Description|'+v+' PN|')
        outbom_list.append('|---|---|-----------|------|')
        which_line = 1
      else:
        l = line.split(',')
        if l[9] == v:
          outbom_list.append('|'+l[0]+'|'+l[3]+'|'+l[11]+'|'+l[10]+'|')
    outbom_list.append('')

with open(outfile,'w') as obom:
  for line in outbom_list:
    obom.write(line+'\n')

# Create a separate csv for each vendor site

for v in vendors:
  outbom_list = []
  outfile = args.name[0]+'-bom-'+v+'.csv'

  which_line = 0
  with open(bomfile,'r') as ibom:
    for line in ibom:
      l = line.split(',')
      if l[9] == v:
        outbom_list.append(l[0]+','+l[3]+','+l[11]+','+l[7]+','+l[8]+','+l[10])

  with open(outfile,'w') as obom:
    for line in outbom_list:
      obom.write(line+'\n') 
  
# Create zip file for OSH Park manufacturing

files = []

for ext in ('*.drl','*.gbl','*.gtl','*.gbo','*.gto','*.gbs','*.gts','*.gbr','*.gm1','*.gtp','*.gbp',):
  files.extend(glob.glob(os.path.join(plotDir, ext)))

os.chdir(plotDir)
ZipFile = zipfile.ZipFile(filename.rstrip('.kicad_pcb')+version+"-gerbers.zip", "w")
for f in files:
  ZipFile.write(os.path.basename(f))
os.chdir("..")

# Create zip file for OSH Stencils
# always using .gm1 (outline) and .gtp,.gbp (paste) files

files = []

for ext in ('*.gm1','*.gtp','*.gbp'):
  files.extend(glob.glob(os.path.join(plotDir, ext)))

os.chdir(plotDir)
ZipFile = zipfile.ZipFile(filename.rstrip('.kicad_pcb')+version+"-stencils.zip", "w")
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


