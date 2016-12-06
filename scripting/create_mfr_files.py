'''
    This program is partly based on these KiCad example files:

      https://github.com/KiCad/kicad-source-mirror/tree/master/demos
      - plot_board.py
      - gen_gerber_drill_files_board.py 

    This program inherits the GPLv3 license from KiCad.
    Modifications were made by Jenner Hanni <jenner@wickerbox.net>

    This program is to be run from the command line to create:
      - gerber and drill files for manufacturing
      - bill of materials in Markdown and CSV formats
      - a zip file of gerbers with the version number
      - a zip file of stencil files with the version number
      - a zip file of the complete files ready for assembly
      - SVG files for easy adding to Github repository READMEs      
      - one PDF file containing all info

'''

import sys, os, zipfile, glob, argparse, re
from shutil import copyfile
from subprocess import call
from pcbnew import *

class Project():
  name = ''
  filename = ''
  version = ''
  board = ''
  height_mm = ''
  width_mm = '' 

# project global
proj = Project()
plotDir = "gerbers/"

# capture command line arguments
parser = argparse.ArgumentParser()
parser.add_argument("-n","--name", nargs=1, help="project name", required=True)
parser.add_argument("-v","--version", nargs=1, help="version number, 'v1.1'")
args = parser.parse_args()

###########################################################
#
#                 parse_arguments()
#
# - handles the argument and sets filename
# - adds .kicad_pcb ending if necessary
# - figures out which particular zip files to create
# 
###########################################################

def parse_arguments():
  if args.version:
    proj.version = args.version[0]
  else:
    proj.version = ''

  if '.kicad_pcb' not in args.name[0]:
    proj.filename=args.name[0]+'.kicad_pcb'
    proj.name = args.name[0]
  else:
    proj.filename=args.name[0]
    proj.name = args.name[0].replace('.kicad_pcb','')

###########################################################
#
#              plot_gerbers               
#
#  - clean the output dir by removing all files
#  - set plot options
#  - create plot layers
#  - safely close the plot object
#
###########################################################

def plot_gerbers(board):

  if not os.path.exists(plotDir):
      os.makedirs(plotDir)

  # remove all files in the output dir
  os.chdir(plotDir)
  filelist = glob.glob('*')
  for f in filelist:
    os.remove(f)
  os.chdir('..')

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
  # all the pdfs were coming out empty
  # is this because I didn't set one in KiCad itself?

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

###########################################################
#
#              create_drill_files                         
#
#  - create enhanced excellon files
#  - create PDF drill files
#
###########################################################

def create_drill_files(board,popt,pctl):
 
  drlwriter = EXCELLON_WRITER(board)
  drlwriter.SetMapFileFormat(PLOT_FORMAT_PDF)

  mirror = False
  minimalHeader = False
  offset = wxPoint(0,0)

  mergeNPTH = True
  metricFmt = True
  genDrl = True
  genMap = True

  # Create drill and map files

  drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )
  drlwriter.SetFormat( metricFmt )
  drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), genDrl, genMap );

  # Create the drill statistics report

  rptfn = pctl.GetPlotDirName() + 'drill_report.rpt'
  drlwriter.GenDrillReportFile( rptfn );

##########################################################
#
#                      get_board_size                     
#
# - report the size of the board
#
# Note: the code in this section is derived from Wayne 
# and Layne's script to get Gerber file outer dimensions, 
# which is public domain. > wayneandlayne.com, accessed 2016
#
###########################################################

def get_board_size():

  xmin = None
  xmax = None
  ymin = None
  ymax = None
  for line in file('gerbers/'+proj.name+'-Edge.Cuts.gm1'):
      results = re.search("^X([\d-]+)Y([\d-]+)", line.strip())
      if results:
          x = int(results.group(1))
          y = int(results.group(2))
          xmin = min(xmin, x) if xmin else x
          xmax = max(xmax, x) if xmax else x
          ymin = min(ymin, y) if ymin else y
          ymax = max(ymax, y) if ymax else y

  x = (xmax-xmin)/10000000.0
  y = (ymax-ymin)/10000000.0

  width_in = '%.2f' % x
  height_in = '%.2f' % y

  dim_ratio = x/y

  if x > y:
    outw = 700
    outh = outw/dim_ratio
  else:
    outh = 700
    outw = outh*dim_ratio

  proj.width_mm = str(outw)
  proj.height_mm = str(outh)

  print '\nThis board is '+width_in+' x '+height_in+' inches'
 
###########################################################
#
#            create_image_preview                         
#
# - create GerbV .gvp project file
# - create the composite top image in GerbV
# - use ImageMagick to flip the images 
#   because GerbV command line doesn't support mirroring.
# 
###########################################################

def create_image_preview():

  projfile = 'top.gvp'
  cwd = os.getcwd()
  print cwd 

  with open('gerbers/'+projfile,'w') as pf:
    pf.write("(gerbv-file-version! \"2.0A\")\n")
    pf.write("(define-layer! 4 (cons \'filename \""+proj.name+"-F.Cu.gtl\")(cons \'visible #t)(cons \'color #(59110 51400 0)))\n")
    pf.write("(define-layer! 3 (cons \'filename \""+proj.name+"-F.Mask.gts\")(cons \'inverted #t)(cons \'visible #t)(cons \'color #(21175 0 23130)))\n")
    pf.write("(define-layer! 2 (cons \'filename \""+proj.name+"-F.Silk.gto\")(cons \'visible #t)(cons \'color #(65535 65535 65535)))\n")
    pf.write("(define-layer! 1 (cons \'filename \""+proj.name+"-Edge.Cuts.gm1\")(cons \'visible #t)(cons \'color #(0 0 0)))\n")
    pf.write("(define-layer! 0 (cons \'filename \""+proj.name+".drl\")(cons \'visible #t)(cons \'color #(0 0 0))(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 0) (list \'digits \'Integer 4))))\n")
    pf.write("(define-layer! -1 (cons \'filename \""+cwd+"\")(cons \'visible #f)(cons \'color #(0 0 0)))\n")
    pf.write("(set-render-type! 0)")

  # create the composite top image
  call(['gerbv','-x','png','--project','gerbers/'+projfile,'-w',proj.width_mm+'x'+proj.height_mm,'-o','preview.png','-B=0'])

###########################################################
#
#            create_assembly_diagrams                      
#
# - wickerlib includes all the assembly info on Fab layers
# - no need to use a GerbV project for this, 
#   just directly work on the Fab file
#
###########################################################

def create_assembly_diagrams():

  call(['gerbv','-x','png','gerbers/'+proj.name+'-F.Fab.gbr','-b#ffffff','-f#000000','-w',proj.width_mm+'x'+proj.height_mm,'-o','assembly-top.png'])
  call(['gerbv','-x','png','gerbers/'+proj.name+'-B.Fab.gbr','-b#ffffff','-f#000000','-w',proj.width_mm+'x'+proj.height_mm,'-o','assembly-bottom.png'])

###########################################################
#       create_individual_layer_images                    #
###########################################################

def create_individual_layer_images():

  # replaced by project file solutions
  # but this is code to create an individual image for all the layers
  
  gerber_images = [['-F.Fab.gbr','assembly.png','#ffffff','#000000'],
                     ['-Edge.Cuts.gm1','outline.png','#ffffff','#000000'],
                     ['-F.Cu.gtl','top-copper.png','#ffffff','#b18883'],
                     ['-B.Cu.gbl','bottom-copper.png','#ffffff','#b18883'],
                     ['-F.Silk.gto','top-silk.png','#ffffff','#401264'],
                     ['-B.Silk.gbo','bottom-silk.png','#ffffff','#401264'],
                     ['-F.Mask.gts','top-mask.png','#ffffff','#401264'],
                     ['-B.Mask.gbs','bottom-mask.png','#ffffff','#401264'],
                     ['.drl','drills.png','#ffffff','#000000']]
  
  for t in gerber_images:
    call(['gerbv','-x','png','gerbers/'+proj.name+t[0],'-b'+t[2],'-f'+t[3],'-o',t[1]])
    call(['convert',t[1],'-transparent',t[2],t[1]])

###########################################################
#             create_bill_of_materials                    #
###########################################################

def create_bill_of_materials():
  bomfile = proj.name+'.csv'
  bom_outfile_csv = proj.name+'-bom.csv'
  bom_outfile_md = proj.name+'-bom.md'

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
  outfile = proj.name+'-bom.csv'

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
  outfile = proj.name+'-bom.md'

  for v in vendors:
    which_line = 0
    with open(bomfile,'r') as ibom:
      for line in ibom:
        if which_line is 0:
          outbom_list.append('|Ref|Qty|Description|'+v.capitalize()+' PN|')
          outbom_list.append('|---|---|-----------|------|')
          which_line = 1
        else:
          l = line.split(',')
          if l[9] == v.capitalize():
            outbom_list.append('|'+l[0]+'|'+l[3]+'|'+l[11]+'|'+l[10]+'|')
      outbom_list.append('')

  with open(outfile,'w') as obom:
    for line in outbom_list:
      obom.write(line+'\n')

  # Create a separate csv for each vendor site

  for v in vendors:
    outbom_list = []
    outfile = proj.name+'-bom-'+v+'.csv'

    which_line = 0
    with open(bomfile,'r') as ibom:
      for line in ibom:
        l = line.split(',')
        if l[9] == v:
          outbom_list.append(l[0]+','+l[3]+','+l[11]+','+l[7]+','+l[8]+','+l[10])

    with open(outfile,'w') as obom:
      for line in outbom_list:
        obom.write(line+'\n') 

 
###########################################################
#                   create_zip_files                      #
###########################################################

def create_zip_files():

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

###########################################################
#                    create_pos_file                      #
###########################################################

def create_pos_file():
  print "create pos file"


###########################################################
#                     update_README                       
#
#   - append BOM to README if there's a commented section
#
###########################################################

def update_README():

  readme = 'README.md'
  newbomlinefile = proj.name+'-bom.md'

  tempfile = []
  newbomlines = []

  with open(newbomlinefile,'r') as f:
    for line in f:
      newbomlines.append(line)

  write_bom = False

  with open(readme,'r') as f:
    for line in f:
      if write_bom is False:
        tempfile.append(line)
        if '<!--- bom start' in line:
          write_bom = True
          for bomline in newbomlines:
            tempfile.append(bomline)
      else:
        if '<!--- bom end' in line:
          tempfile.append(line)
          write_bom = False

  with open(readme,'w') as f:
    for line in tempfile:
      f.write(line)


###########################################################
#                      create_PDF                         #
###########################################################

def create_pdf():
  call(['pandoc','-V','geometry:margin=1in','README.md','-o',proj.name+version+'.pdf']) 

###########################################################
#                      main                               #
###########################################################

if __name__ == "__main__":

  parse_arguments()
  print 'filename:\t',proj.filename
  print 'proj name:\t',proj.name+'-'+proj.version
  print ''

  # create global board object
  board = LoadBoard(proj.filename)
  
  # create global plot controller objects
  pctl = PLOT_CONTROLLER(board)
  popt = pctl.GetPlotOptions()
  popt.SetOutputDirectory(plotDir)

  
  plot_gerbers(board)    
  create_drill_files(board,popt,pctl)

  get_board_size()

  create_image_preview()
  create_assembly_diagrams()
  create_individual_layer_images()
  create_bill_of_materials()
  create_zip_files()
  create_pos_file()
  update_README()
  create_pdf()

  exit()

