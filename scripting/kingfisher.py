# this script depends on a couple of objects -- the bomfile, the project, and the component

import sys, os, zipfile, glob, argparse, re, datetime, json, Image
from shutil import copyfile
from subprocess import call
from pcbnew import *

###########################################################
#
#              create_new_project
#
# inputs:
# - a bunch of raw input (for now)
# - library directory path
# - template directory path
# 
# what it does:
# - creates a subfolder called projname
# - collects input information by raw_input or test.json
# - creates a dict to hold all that project information
# - create proj.json
# - create README.md
# - copy over KiCad template files and rename to projname,
#   including using the proj.json info for page settings
#
# TODO: figure out best way to handle input information
# 
# returns nothing
# 
###########################################################

def create_new_project(projname):

  if not os.path.exists(projname):
          os.makedirs(projname)

  # use test.json for testing if it exists
  # otherwise, lots of raw_input!
  if os.path.isfile(projname+'/test.json'):
    with open('test.json') as jfile:    
      data = json.load(jfile) 
    print 'file exists!'

  else:
    print 'using test values'
    title = 'E202VAR VLF Receiver'
    version = '1.1'
    description = 'Natural radio receiver below 22Hz based on Romero E202'
    company = 'Wickerbox Electronics'
    email = 'jenner@wickerbox.net'
    website = 'http://wickerbox.net/'
    license = 'CERN Open Hardware License v1.2'
    now = datetime.datetime.now()
    date_create = now.strftime('%B %d, %Y')
    date_update = ''
    lib_dir = '/home/wicker/wickerlib/libraries/'
    template_dir = '/home/wicker/wickerlib/templates/'
    template_kicad = 'wickerbox-2layer'
    template_latex = 'wickerbox'
    bom_dir = 'bom'
    gerbers_dir = 'gerbers'

    data = {'projname':projname,
          'title':title,
          'version':version,
          'description':description,
          'company':company,
          'email':email,
          'website':website,
          'license':license,
          'date_create':date_create, 
          'date_update':date_update,
          'lib_dir':lib_dir,
          'template_dir':template_dir,
          'template_kicad':template_kicad,
          'template_latex':template_latex,
          'bom_dir':bom_dir,
          'gerbers_dir':gerbers_dir}

  # create README.md

  filename=os.path.join(data['projname'],'README.md')

  if os.path.exists(filename) is True:
    s = raw_input("README.md exists. Do you want to overwrite it? Y/N: ")
    if 'Y' in s or 'y' in s:
      print "great, we'll overwrite."
    else:
      print "okay, closing program."
      exit()
   
  with open(filename,'w') as o:
    o.write('# '+data['title']+' v'+data['version']+'\n')
    o.write(data['description']+'\n\n')
    o.write('## Introduction\n\n')
    o.write('Intro text.\n\n')
    o.write('<!--- start bom --->\n\n')
    o.write('<!--- end bom --->\n\n')
    o.write('![Assembly Diagram](assembly.png)\n\n')
    o.write('![Gerber Preview](preview.png)\n\n')

  # create proj.json

  filename=os.path.join(data['projname'],'proj.json')
  
  if os.path.exists(filename) is True:
    s = raw_input("proj.json exists. Do you want to overwrite it? Y/N: ")
    if 'Y' in s or 'y' in s:
      print "great, we'll overwrite."
    else:
      print "okay, closing program."
      exit()

  with open(filename, 'w') as outfile:
      json.dump(data, outfile, indent=4, sort_keys=True, separators=(',', ':'))

  # copy over the KiCad template files and fill in values

  print "\ncreating KiCad Project from template", data['template_kicad']

  templatesrc = data['template_dir']+data['template_kicad']+'/'+data['template_kicad']
  newpath = os.path.join(data['projname'],data['projname'])
  call(['cp',templatesrc+'.kicad_pcb',newpath+'.kicad_pcb'])
  call(['cp',templatesrc+'.pro',newpath+'.pro'])
  call(['cp',templatesrc+'.sch',newpath+'.sch'])
  call(['cp',data['template_dir']+data['template_kicad']+'/fp-lib-table',data['projname']+'/fp-lib-table'])

  # replace entire title block of .kicad_pcb file 

  f = newpath+'.kicad_pcb'
  f_temp = []
  title_flag = False

  with open(f,'r') as fixfile:
    for line in fixfile:

      if '  (title_block' in line:
        title_flag = True
      if title_flag is True:
        if '  )' in line:
          title_flag = False
          
          f_temp.append('  (title_block\n')
          f_temp.append('    (title "'+data['title']+'")\n')
          f_temp.append('    (date "'+data['date_create']+'")\n')
          f_temp.append(  '    (rev "'+data['version']+'")\n')
          f_temp.append('    (company "'+data['license']+'")\n')
          f_temp.append('    (comment 1 "'+data['email']+'")\n')
          f_temp.append('    (comment 2 "'+data['website']+'")\n')
          f_temp.append('    (comment 3 "'+data['company']+'")\n')
          f_temp.append('  )\n')
          
      else:
        f_temp.append(line)

  with open(f,'w') as fixfile:
    for line in f_temp:
      fixfile.write(line)

  # replace entire title block of .sch file

  f = newpath+'.sch'
  f_temp = []
  title_flag = False

  with open(f,'r') as fixfile:
    for line in fixfile:

      if 'Title ""' in line:
        title_flag = True
      if title_flag is True:
        if '$EndDescr' in line:
          title_flag = False
          
          f_temp.append('Title "'+data['title']+'"\n')
          f_temp.append('Date "'+data['date_create']+'"\n')
          f_temp.append('Rev"'+data['version']+'"\n')
          f_temp.append('Comp "'+data['license']+'")\n')
          f_temp.append('Comment1 "'+data['email']+'")\n')
          f_temp.append('Comment2 "'+data['website']+'")\n')
          f_temp.append('Comment3 "'+data['company']+'")\n')
          f_temp.append('Comment4 ""\n')
          f_temp.append('$EndDescr\n')
      else:
        f_temp.append(line)

  with open(f,'w') as fixfile:
    for line in f_temp:
      fixfile.write(line)

  exit()

###########################################################
#
#          sanitize_input_kicad_filename
#
# inputs:
# - filename that may or may not end in .kicad_pcb
# 
# outputs:
#projrojname and filename where
#   filename = projname.kicad_pcb
# 
###########################################################

def sanitize_input_kicad_filename(filename):

  # sort out the project name
  # filename: projname.kicad_pcb
  projname = ''

  if '.kicad_pcb' in filename:
    projname = filename.split('.')[0]
  else:
    projname = filename
    filename = filename+'.kicad_pcb'

  x = raw_input("The root project name is "+projname+", is this correct? Y/N: ")
  if 'N' in x or 'n' in x:
    projname = raw_input("Enter the project name: ")
    filename = projname+'.kicad_pcb'

  return (projname, filename)

###########################################################
#
#              plot_gerbers_and_drills
#
#  inputs:
#  - root name of the project 
#    root of 'project.kicad_pcb' would be 'project'
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
#  returns nothing
#
###########################################################

def plot_gerbers_and_drills(projname, plot_dir):

  projname_full = projname+'.kicad_pcb'

  # create board object
  board = LoadBoard(projname_full)
  
  # create plot controller objects
  pctl = PLOT_CONTROLLER(board)
  popt = pctl.GetPlotOptions()
  popt.SetOutputDirectory(plot_dir)

  # make the output dir if it doesn't already exist  
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

##########################################################
#
#                get_board_size                     
#
# inputs:
#  - root name of the project 
#    root of 'project.kicad_pcb' would be 'project'
#  - name of a subdirectory to put output files
#
# what it does:
# - open the board outline file (ends in .gko)
#   which is in KiCad export format
# - calculate the size of the board outline
#
# returns:
# - a list in format:
#   [width (inch), height (inch),      # actual board 
#    width (mm), height (mm),          # actual board
#    width (pixels), height (pixels)]  # preview images
#   
# Note: the code in this section is derived from Wayne 
# and Layne's script to get Gerber file outer dimensions, 
# which is public domain. > wayneandlayne.com, accessed 2016
#
###########################################################

def get_board_size(projname,plot_dir):

  fp = plot_dir+'/'+projname+'-Edge.Cuts.gko'
  print fp 

  xmin = None
  xmax = None
  ymin = None
  ymax = None
  with open(fp, 'r') as f:
    for line in f:
      results = re.search("^X([\d-]+)Y([\d-]+)", line.strip())
      if results:
        x = int(results.group(1))
        y = int(results.group(2))
        xmin = min(xmin, x) if xmin else x
        xmax = max(xmax, x) if xmax else x
        ymin = min(ymin, y) if ymin else y
        ymax = max(ymax, y) if ymax else y

  x = (xmax-xmin)/1000000.0
  y = (ymax-ymin)/1000000.0

  print type(x)

  width_mm = '%.2f' % x
  height_mm = '%.2f' % y

  width_in = '%.2f' % float(x*0.03937)
  height_in = '%.2f' % float(y*0.03937)

  dim_ratio = x/y

  if x > y:
    scaled_w = 700
    scaled_h = int(scaled_w/dim_ratio)
  else:
    scaled_h = 700
    scaled_w = int(scaled_h*dim_ratio)

  ret_list = [width_in,height_in,width_mm,height_mm,scaled_w,scaled_h]

  return ret_list

###########################################################
#
#            create_assembly_diagrams                      
#
# note: the assembly diagrams are created from F.Fab and 
#       B.Fab layers. 
# todo: support using another layer instead
#
# inputs:
#  - root name of the project 
#    root of 'project.kicad_pcb' would be 'project'
#  - name of a subdirectory to put output files
#  - height of board in pixels
#  - width of board in pixels
#
# what it does:
# - uses gerbv to export F.Fab and B.Fab images  
# - remove empty layers 
# - create the output file from non-empty layers,
#   stitching them together side by side depending
#   on whether the images are portrait or landscape 
#
# returns nothing
#   
###########################################################

def create_assembly_diagrams(projname,plotdir,width,height):

  width = str(width)
  height = str(height)

  call(['gerbv','-x','png',plotdir+'/'+projname+'-F.Fab.gbr','-b#ffffff','-f#000000','-w',width+'x'+height,'-o','assembly-top.png'])
  call(['gerbv','-x','png',plotdir+'/'+projname+'-B.Fab.gbr','-b#ffffff','-f#000000','-w',width+'x'+height,'-o','assembly-bottom.png'])

  img = Image.open('assembly-top.png')
  extrema = img.convert("L").getextrema()
  if extrema[0] == extrema[1]:
    call(['rm','assembly-top.png'])
  img = Image.open('assembly-bottom.png')
  extrema = img.convert("L").getextrema()
  if extrema[0] == extrema[1]:
    call(['rm','assembly-bottom.png'])

  # create preview.png file from one or both 
  f1 = os.path.isfile('assembly-top.png')
  f2 = os.path.isfile('assembly-bottom.png')

  if f1 is True and f2 is True:
    new_w = str(int(width) + 20)
    new_h = str(int(height) + 20)

    if width > height:
      call(['convert','assembly-top.png','-bordercolor','white','-extent',width+'x'+new_h,'assembly-top.png'])
      call(['convert','assembly-top.png','assembly-bottom.png','-append','assembly.png'])
    else:
      call(['convert','assembly-top.png','-bordercolor','white','-extent',new_w+'x'+height,'assembly-top.png'])
      call(['convert','assembly-top.png','assembly-bottom.png','+append','assembly.png'])
    call(['rm','assembly-top.png','assembly-bottom.png'])
  elif f1 is True:
    call(['mv','assembly-top.png','assembly.png'])
  elif f2 is True:
    call(['mv','assembly-bottom.png','assembly.png'])
  else:
    print "no assembly diagrams."


###########################################################
#
#            create_image_previews 
#
# inputs:
#  - root name of the project 
#    root of 'project.kicad_pcb' would be 'project'
#  - name of a subdirectory to put output files
#  - height of board in pixels
#  - width of board in pixels
#
# what it does:
# - create GerbV .gvp project file
# - create the composite top image in GerbV
# - use ImageMagick to flip the bottom-side images 
#   because GerbV command line doesn't support mirroring.
# - create composite bottom image in GerbV
# - merge the two images depending on whether they're
#   oriented as portraits or landscapes
#
# inpired by this code for the one liner
# - https://github.com/lukeweston/eagle-makefile/blob/master/makefile
#
# inspired by this code for the project-based solution
# - https://gist.github.com/docprofsky/70b718b434d7d184c59729263d436a3d#file-heliopsis-gvp
# 
###########################################################

def create_image_previews(projname,plotdir,width_pixels,height_pixels):

  width_pixels = str(width_pixels)
  height_pixels = str(height_pixels)

  # top side

  projfile = 'top.gvp'
  cwd = os.getcwd()

  with open(plotdir+'/'+projfile,'w') as pf:
    pf.write("(gerbv-file-version! \"2.0A\")\n")
    pf.write("(define-layer! 4 (cons \'filename \""+projname+"-F.Cu.gtl\")(cons \'visible #t)(cons \'color #(59110 51400 0)))\n")
    pf.write("(define-layer! 3 (cons \'filename \""+projname+"-F.Mask.gts\")(cons \'inverted #t)(cons \'visible #t)(cons \'color #(21175 0 23130)))\n")
    pf.write("(define-layer! 2 (cons \'filename \""+projname+"-F.Silk.gto\")(cons \'visible #t)(cons \'color #(65535 65535 65535)))\n")
    pf.write("(define-layer! 1 (cons \'filename \""+projname+"-Edge.Cuts.gm1\")(cons \'visible #t)(cons \'color #(0 0 0)))\n")
    pf.write("(define-layer! 0 (cons \'filename \""+projname+".drl\")(cons \'visible #t)(cons \'color #(0 0 0))(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 0) (list \'digits \'Integer 4))))\n")
    pf.write("(define-layer! -1 (cons \'filename \""+cwd+"\")(cons \'visible #f)(cons \'color #(0 0 0)))\n")
    pf.write("(set-render-type! 3)")

  call(['gerbv','-x','png','--project',plotdir+'/'+projfile,'-w',width_pixels+'x'+height_pixels,'-o','preview-top.png','-B=0'])
  call(['rm',plotdir+'/top.gvp'])

  # bottom side

  projfile = 'bottom.gvp'
  cwd = os.getcwd()
  print cwd 

  with open(plotdir+'/'+projfile,'w') as pf:
    pf.write("(gerbv-file-version! \"2.0A\")\n")
    pf.write("(define-layer! 4 (cons \'filename \""+projname+"-B.Cu.gbl\")(cons \'visible #t)(cons \'color #(59110 51400 0)))\n")
    pf.write("(define-layer! 3 (cons \'filename \""+projname+"-B.Mask.gbs\")(cons \'inverted #t)(cons \'visible #t)(cons \'color #(21175 0 23130)))\n")
    pf.write("(define-layer! 2 (cons \'filename \""+projname+"-B.Silk.gbo\")(cons \'visible #t)(cons \'color #(65535 65535 65535)))\n")
    pf.write("(define-layer! 1 (cons \'filename \""+projname+"-Edge.Cuts.gm1\")(cons \'visible #t)(cons \'color #(0 0 0)))\n")
    pf.write("(define-layer! 0 (cons \'filename \""+projname+".drl\")(cons \'visible #t)(cons \'color #(0 0 0))(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 0) (list \'digits \'Integer 4))))\n")
    pf.write("(define-layer! -1 (cons \'filename \""+cwd+"\")(cons \'visible #f)(cons \'color #(0 0 0)))\n")
    pf.write("(set-render-type! 0)")

  call(['gerbv','-x','png','--project',plotdir+'/'+projfile,'-w',width_pixels+'x'+height_pixels,'-o','preview-bottom.png','-B=0'])
  call(['convert','preview-bottom.png','-flop','preview-bottom.png'])
  call(['rm',plotdir+'/bottom.gvp'])

  # create stitched-together previews based on whether they're portrait or landscape

  new_w = str(int(width_pixels) + 20)
  new_h = str(int(height_pixels) + 20)

  if width_pixels > height_pixels:
    call(['convert','preview-top.png','-bordercolor','white','-extent',width_pixels+'x'+new_h,'preview-top.png'])
    call(['convert','preview-top.png','preview-bottom.png','-append','preview.png'])
  else:
    call(['convert','preview-top.png','-bordercolor','white','-extent',new_w+'x'+height_pixels,'preview-top.png'])
    call(['convert','preview-top.png','preview-bottom.png','+append','preview.png'])

  # cleanup

  call(['rm','preview-top.png','preview-bottom.png'])

###########################################################
#
#                      create_pdf                      
#
# inputs: 
# - name of template with .tex extension
# - project name
# - project version
#
# what it does:
# - calls pandoc to create an output PDF file from README.md
#   using the input template given
# 
# TODO: accommodate flags, let it use proj.json if one exists
#
###########################################################

def create_pdf(projname,version,template):

  inputfile = 'README.md'
  
  call(['pandoc','-fmarkdown-implicit_figures','-R','--template='+template,'-V','geometry:margin=1in',inputfile,'-o',projname+'-'+version+'.pdf']) 

###########################################################
#                      main                               #
###########################################################

if __name__ == '__main__':

  parser = argparse.ArgumentParser('Kingfisher automates KiCad project management.\n')
  parser.add_argument('proj_name',action='store',help="Name of the project")
  parser.add_argument('plot_dir',action='store',help="Subdirectory to place output files.")
  parser.add_argument('version',action='store',help="Version number (i.e. '1.1')")
  args = parser.parse_args()

  create_new_project(args.proj_name)

  exit()
  plot_gerbers_and_drills(args.proj_name,args.plot_dir)
  board_dims = get_board_size(args.proj_name,args.plot_dir)
  
  width_in = board_dims[0]
  height_in = board_dims[1]
  width_mm = board_dims[2]
  height_mm = board_dims[3]
  width_pixels = board_dims[4]
  height_pixels = board_dims[5]

  print '\nThis board is '+width_in+' x '+height_in+' inches (' \
        +width_mm+' x '+height_mm+' mm)'

  create_assembly_diagrams(args.proj_name,args.plot_dir,width_pixels, height_pixels) 
  create_image_previews(args.proj_name,args.plot_dir,width_pixels, height_pixels) 

  template = 'rewire.tex'

  create_pdf(args.proj_name,args.version,template)
