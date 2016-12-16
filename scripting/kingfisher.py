import sys, os, zipfile, glob, argparse, re
from shutil import copyfile
from subprocess import call
from pcbnew import *
import Image

###########################################################
#
#              plot_gerbers_and_drills
#
#  inputs:
#  - filename that may or may not end in .kicad_pcb
#  - name of a subdirectory to put output files
# 
#  what it does:
#  - adds .kicad_pcb suffix if necessary
#  - clean the output dir by removing all files
#  - set plot options
#  - create plot layers in output directory
#  - safely close the plot object
#  - set drill options
#  - create drill and map files
#  - create drill statistics report
#
###########################################################

def plot_gerbers_and_drills(filename, plot_dir):

  projname = ''

  # filename: projname.kicad_pcb
  if '.kicad_pcb' not in filename:
    projname = filename
    filename = filename+'.kicad_pcb'
  else:
    projname = filename.split('.')[0]

  # create board object
  board = LoadBoard(filename)
  
  # create plot controller objects
  pctl = PLOT_CONTROLLER(board)
  popt = pctl.GetPlotOptions()
  popt.SetOutputDirectory(plot_dir)
  
  if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

  # remove all files in the output dir
  os.chdir(plot_dir)
  filelist = glob.glob('*')
  for f in filelist:
    os.remove(f)
  os.chdir('..')

  # set plot options

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

  # this option in the reference example said 'must be set true'
  # but all the PDFs were coming out empty; is this because 
  # there was no aux origin applied in my .kicad_pcb file? 
  # in any case, now it works when set to false. 
  popt.SetUseAuxOrigin(False)  

  # note: the middle value in plot_plan is an integer layer number:
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

  # generate all gerbers
  for layer_info in plot_plan:
      pctl.SetLayer(layer_info[1])
      pctl.OpenPlotfile(layer_info[0], PLOT_FORMAT_GERBER, layer_info[2])
      pctl.PlotLayer()

  # generate internal copper layers, if any
  lyrcnt = board.GetCopperLayerCount();

  for innerlyr in range ( 1, lyrcnt-1 ):
      pctl.SetLayer(innerlyr)
      lyrname = 'In.%s' % innerlyr
      pctl.OpenPlotfile(lyrname, PLOT_FORMAT_GERBER, "Inner")
      #print 'plot %s' % pctl.GetPlotFileName()
      if pctl.PlotLayer() == False:
          print "Plot Error: Layer Missing?"

  # close out the plot to safely free the object.

  pctl.ClosePlot()

  # create drill object and set options

  drlwriter = EXCELLON_WRITER(board)
  drlwriter.SetMapFileFormat(PLOT_FORMAT_PDF)

  mirror = False
  minimalHeader = False
  offset = wxPoint(0,0)

  mergeNPTH = True
  metricFmt = True
  genDrl = True
  genMap = True

  # create drill and map files

  drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )
  drlwriter.SetFormat( metricFmt )
  drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), genDrl, genMap );

  # create the drill statistics report

  rptfn = pctl.GetPlotDirName() + 'drill_report.rpt'
  drlwriter.GenDrillReportFile( rptfn );

  # rename the drill and outline files

  path = os.path.join(plot_dir,projname)
  call(['mv',path+'-Edge.Cuts.gm1',path+'-Edge.Cuts.gko'])
  call(['mv',path+'.drl',path+'.xln'])

  

###########################################################
#                      main                               #
###########################################################

if __name__ == '__main__':

  parser = argparse.ArgumentParser('Kingfisher automates KiCad project management.\n')
  parser.add_argument('proj_name',action='store',help="Name of the project")
  parser.add_argument('plot_dir',action='store',help="Subdirectory to place output files.")
  args = parser.parse_args()

  plot_gerbers_and_drills(args.proj_name,args.plot_dir)

  
