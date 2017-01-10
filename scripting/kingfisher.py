#
# created by Jenner Hanni at Wickerbox Electronics
# http://wickerbox.net/
#
# This script automates some of the KiCad process, including:
# - generating stencil and manufacturing files
# - creating bills of material
# - packaging everything so it's ready to upload for ordering
# - building a beautiful documentation PDF
# - building a nice README with Markdown BOM table for Github
# 
# It depends on some assumptions of the Wickerlib environment,
# so pay attention to the 'data' object throughout. 
#
# For questions, please email me at jenner@wickerbox.net.
# 
# Released under the GPLv3.
#

import sys, os, zipfile, glob, argparse, re, datetime, json, Image
from shutil import copyfile
from subprocess import call
from pcbnew import *

# globals for proj.json locations
crazy_json = '/home/wicker/proj/Crazy-Circuits/Development/templates/crazy.json'
wickerbox_json = '/home/wicker/wickerlib/templates/wickerbox.json'
breakout_json = '/home/wicker/wickerlib/templates/breakout.json'

class Comp():
  ref = ''
  value = ''
  footprint = ''
  fp_library = ''
  symbol = ''
  sym_library = ''
  datasheet = ''
  fields = [('','')]

  def print_component(self):
    print '-------------------------'
    print 'Ref:',self.ref,'\t','Value:',self.value
    print self.datasheet
    print 'Symbol:',self.symbol, 'in' ,self.sym_library
    print 'Footprint:',self.footprint,'in',self.fp_library
    for f in self.fields:
      print f[0],f[1]

class BOMline():
  refs = ''
  qty = ''
  value = ''
  footprint = ''
  fp_library = ''
  symbol = ''
  sym_library = ''
  datasheet = ''
  mf_pn = ''
  mf_name = ''
  s1_pn = ''
  s1_name = ''

  def print_line(self):
    print self.refs,self.qty,self.value,self.footprint,self.fp_library,self.symbol,self.sym_library,self.datasheet,self.mf_name,self.mf_pn,self.s1_name,self.s1_pn

###########################################################
#
#                    update_version
#
# inputs:
# - existing project name
# - new version number
#
# what it does:
# - reads in data from the appropriate proj.json file
# - updates the version number
# - writes the updated data back to the proj.json file
# 
# returns nothing
# 
###########################################################

def update_version(name,version):

  filename = os.path.join(name,'proj.json')
  with open(filename,'r') as jsonfile:
    data = json.load(jsonfile)

  data['version'] = 'v'+version

  with open(filename, 'w') as jsonfile:
    json.dump(data, jsonfile, indent=4, sort_keys=True, separators=(',', ':'))
  
###########################################################
#
#              create_new_project
#
# inputs:
# - project name
# - json template name
# - version number
# 
# what it does:
# - creates a subfolder called projname
#   if one exists, it prompts to overwrite. this is messy.
# - creates the json file by copying existing template
# - prompts for additional information
# - creates a data dict to hold all that project information
#   that will be used throughout the rest of kingfisher
# - create README.md
# - copy over KiCad template files and rename to projname,
#   including using the proj.json info for page settings
# - replace the 'page settings' sections of sch and 
#   .kicad_pcb files
# 
# returns nothing
# 
###########################################################

def create_new_project(projname,which_template,version):

  if not os.path.exists(projname):
          os.makedirs(projname)

  # copy in the appropriate json file

  if which_template is None:
    which_template = raw_input("what is the absolute path to the json template file? ")
  elif 'crazy' in which_template:
    which_template = crazy_json
  elif 'breakout' in which_template:
    which_template = breakout_json
  elif 'wickerbox' in which_template:
    which_template = wickerbox_json
  else:
    which_template = raw_input("what is the absolute path to the json template file? ")

  call(['cp',which_template,projname+'/proj.json'])

  # load the proj.json file and make updates if necessary

  with open(projname+'/proj.json','r') as jsonfile:
    data = json.load(jsonfile)

  data['projname'] = projname
  now = datetime.datetime.now()
  data['date_create'] = data['date_update'] = now.strftime('%d %b %Y')
  if data['version'] is not version:
    data['version'] = version

  for item in data:
    if not data[item]:
      data[item] = raw_input('%s: ' %item)
    else:
      print item+': '+data[item]

  with open(projname+'/proj.json', 'w') as jsonfile:
    json.dump(data, jsonfile, indent=4, sort_keys=True, separators=(',', ':'))

  # create README.md

  filename=os.path.join(data['projname'],'README.md')

  if os.path.exists(filename) is True:
    s = raw_input("README.md exists. Do you want to overwrite it? Y/N: ")
    if 'Y' in s or 'y' in s:
      print "great, we'll overwrite."
    else:
      print "okay, closing program."
      exit()

  create_readme(filename, data)

  # copy over the KiCad template files and fill in values

  print "\ncreating KiCad Project from template", data['template_kicad']

  templatesrc = data['template_dir']+'/'+data['template_kicad']+'/'+data['template_kicad']
  newpath = os.path.join(data['projname'],data['projname'])
  call(['cp',templatesrc+'.kicad_pcb',newpath+'.kicad_pcb'])
  call(['cp',templatesrc+'.pro',newpath+'.pro'])
  call(['cp',templatesrc+'.sch',newpath+'.sch'])
  call(['cp',data['template_dir']+'/'+data['template_kicad']+'/fp-lib-table',data['projname']+'/fp-lib-table'])

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

###########################################################
#
#                 create_readme
#
# inputs:
# - relative file path
# - data object
# 
# what it does:
# - takes the values in data and writes to file path
#
# returns nothing
# 
###########################################################

def create_readme(filename,data):

  with open(filename,'w') as o:

    o.write('<!--- start title --->\n')
    o.write('# '+data['title']+' v'+data['version']+'\n')
    o.write(data['description']+'\n\n')
    o.write('\n')
    o.write('Updated: '+data['date_update']+'\n')
    o.write('\n')
    if 'author' in data:
      o.write('Author: '+data['author']+'\n')
    o.write('Website: '+data['website']+'\n')
    o.write('Company: '+data['company']+'\n')
    o.write('License: '+data['license']+'\n')
    o.write('\n')
    o.write('<!--- end title --->\n')
    o.write('Intro text.\n\n')
    o.write('### Bill of Materials\n\n')
    o.write('<!--- bom start --->\n')
    o.write('<!--- bom end --->\n')
    o.write('![Assembly Diagram](assembly.png)\n\n')
    o.write('![Gerber Preview](preview.png)\n\n')

###########################################################
#
#          sanitize_input_kicad_filename
#
# inputs:
# - filename that may or may not end in .kicad_pcb
# 
# what it does:
# - helper function to clean .kicad_pcb suffix
# 
# outputs:
# - tuple ('projname','filename') where 
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
#  - root name of the project, where the 
#    root of 'project.kicad_pcb' would be 'project'
#  - name of a subdirectory to put output files
# 
#  what it does:
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

  # make the output dir if it doesn't already exist  
  if not os.path.exists(plot_dir):
    os.makedirs(plot_dir)

  # remove all files in the output dir
  cwd = os.getcwd()
  os.chdir(plot_dir)
  filelist = glob.glob('*')
  for f in filelist:
    os.remove(f)
  os.chdir('..')
  print os.getcwd()

  # create board object
  board = LoadBoard(projname+'.kicad_pcb')

  # create plot controller objects
  pctl = PLOT_CONTROLLER(board)
  popt = pctl.GetPlotOptions()
  popt.SetOutputDirectory(plot_dir)

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

  # Create drill and map files

  drlwriter.SetOptions( mirror, minimalHeader, offset, mergeNPTH )
  drlwriter.SetFormat( metricFmt )
  drlwriter.CreateDrillandMapFilesSet( pctl.GetPlotDirName(), genDrl, genMap );

  # Create the drill statistics report

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
# TODO: handle circle boards!
#
###########################################################

def get_board_size(projname,plot_dir):

  fp = os.path.join(plot_dir,projname+'-Edge.Cuts.gko')
  
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

  width_mm = '%.2f' % x
  height_mm = '%.2f' % y

  width_in = '%.2f' % float(x*0.03937)
  height_in = '%.2f' % float(y*0.03937)

  if x is 0 or y is 0:
    print "This may be a circular board, can't deal with it yet."
    print "can't continue."
    exit()
  else:
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
    pf.write("(define-layer! 1 (cons \'filename \""+projname+"-Edge.Cuts.gko\")(cons \'visible #t)(cons \'color #(0 0 0)))\n")
    pf.write("(define-layer! 0 (cons \'filename \""+projname+".xln\")(cons \'visible #t)(cons \'color #(65535 65535 65535))(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 0) (list \'digits \'Integer 4))))\n")
    pf.write("(define-layer! -1 (cons \'filename \""+cwd+"\")(cons \'visible #f)(cons \'color #(0 0 0)))\n")
    pf.write("(set-render-type! 3)")

  call(['gerbv','-x','png','--project',plotdir+'/'+projfile,'-w',width_pixels+'x'+height_pixels,'-o','preview-top.png','-B=0'])
  #call(['convert','preview-top.png','-bordercolor','White','-border','10x10','test.png'])
  call(['convert','preview-top.png','-fill','White','-draw','color 1,1 floodfill','preview-top.png'])
  call(['convert','preview-top.png','-fill','Black','-opaque','#E2DCB1','preview-top.png']) # fill most of drill circles
  call(['convert','preview-top.png','-fill','Black','-opaque','#B1B1B1','preview-top.png']) # clean up drill circle edge
  call(['convert','preview-top.png','-fill','Black','-opaque','#F6F4E7','preview-top.png']) # clean up extra copper ring
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
    pf.write("(define-layer! 1 (cons \'filename \""+projname+"-Edge.Cuts.gko\")(cons \'visible #t)(cons \'color #(0 0 0)))\n")
    pf.write("(define-layer! 0 (cons \'filename \""+projname+".xln\")(cons \'visible #t)(cons \'color #(0 0 0))(cons \'attribs (list (list \'autodetect \'Boolean 1) (list \'zero_supression \'Enum 1) (list \'units \'Enum 0) (list \'digits \'Integer 4))))\n")
    pf.write("(define-layer! -1 (cons \'filename \""+cwd+"\")(cons \'visible #f)(cons \'color #(0 0 0)))\n")
    pf.write("(set-render-type! 0)")

  call(['gerbv','-x','png','--project',plotdir+'/'+projfile,'-w',width_pixels+'x'+height_pixels,'-o','preview-bottom.png','-B=0'])
  call(['convert','preview-bottom.png','-flop','preview-bottom.png'])
  call(['convert','preview-bottom.png','-fill','White','-draw','color 1,1 floodfill','preview-bottom.png'])
  call(['convert','preview-bottom.png','-fill','Black','-opaque','#E2DCB1','preview-bottom.png']) # fill most of drill circles
  call(['convert','preview-bottom.png','-fill','Black','-opaque','#B1B1B1','preview-bottom.png']) # clean up drill circle edge
  call(['convert','preview-bottom.png','-fill','Black','-opaque','#F6F4E7','preview-bottom.png']) # clean up extra copper ring
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
#           create_component_list_from_netlist            
#
# inputs:
# - data object
#
# what it does:
# - opens the netlist file
# - TODO: handle error if netlist is not present
# - for every line in the netlist, create a component line
#   there is no handling of duplicate entries; this is a 
#   raw list right from the netlist.
#
# returns:
# - list of components
# 
###########################################################

def create_component_list_from_netlist(data):

  netfile_name = data['projname']+'.net'

  components = []

  comp_flag = False
  comp_count = 0
  fields_flag = False

  with open(netfile_name,'r') as netfile:
    for line in netfile:
      if 'components' in line:
          comp_flag = True
      if 'libparts' in line:
        comp_flag = False

      if comp_flag is True:
        if 'comp' in line and 'components' not in line:
          comp = Comp()
          comp_count = comp_count + 1
          comp.ref = line.replace(')','').replace('\n','').replace('(comp (ref ','').lstrip(' ')
        if 'value' in line: 
          comp.value = line
          comp.value = line.replace(')','').replace('\n','').strip('(value ').lstrip(' ')
        if 'footprint' in line: 
          if ':' not in line:
            comp.footprint = line.replace('(footprint ','').replace(')\n','').lstrip(' ')
            comp.fp_library = 'None'
          else:
            line = line.replace('(footprint','').replace(')\n','').lstrip(' ').split(':')
            comp.footprint = line[1]
            comp.fp_library = line[0]
        if 'datasheet' in line: 
          comp.datasheet = line.replace('(datasheet ','').lstrip(' ').replace(')\n','')
        if 'libsource' in line:
          fields_flag = False
          line = line.replace('(libsource (lib ','').replace('))','').lstrip(' \n').split(') (')
          comp.sym_library = line[0]
          comp.symbol = line[1].lstrip('part ').replace('\n','')
          components.append(comp)

        if 'fields' in line:
          fields_flag = True
          del comp.fields[:]
          comp.fields = []
        if fields_flag is True:
          if 'fields' not in line:
            line = line.replace('(field (name ','').replace(')\n','').replace('"','').lstrip(' ')
            line = line.rstrip(')').split(') ')
            comp.fields.append((line[0],line[1]))

  return components

###########################################################
#
#             create_bill_of_materials 
# 
# inputs: 
# - data object
#
# what it does:
# - create a components list organized by refdes
# - figures out which vendors are necessary
# - create the master BOM object made up of BOM lines
# - create a master CSV file with all possible info 
# - create a CSV file in the Seeed format
# - create CSV files for each vendor
# - create one Markdown file with tables
# 
###########################################################

def create_bill_of_materials(data):

  if not os.path.exists(data['bom_dir']):
    os.makedirs(data['bom_dir'])

  components = create_component_list_from_netlist(data)

  bom_outfile_csv = data['bom_dir']+'/'+data['projname']+'-'+data['version']+'-bom-master.csv'
  bom_outfile_seeed_csv = data['bom_dir']+'/'+data['projname']+'-'+data['version']+'-bom-seeed.csv'
  bom_outfile_md = data['bom_dir']+'/'+data['projname']+'-'+data['version']+'-bom-readme.md'

  vendors = []
  optional_fields = []
  bom = []

  # get the list of field names
  # and figure out what vendors are necessary

  for c in components:
    for f in c.fields:
      if f[0] not in optional_fields: 
        optional_fields.append(f[0])
      if 'S1_Name' in f[0]:
        vendors.append(f[1])

  vtemp = []
  vendors = set(vendors)
  for v in vendors:
    vtemp.append(v)

  vendors = vtemp

  # create the master BOM object
   
  bom = []

  for c in components:

    exists_flag = False

    if bom:
      for line in bom:
        if line.symbol in c.symbol:
          line.qty = line.qty + 1
          line.refs = line.refs+' '+c.ref
          exists_flag = True
          break
          

    if not exists_flag:
      bomline = BOMline()
      bomline.refs = c.ref
      bomline.qty = 1
      bomline.value = c.value
      bomline.footprint = c.footprint
      bomline.fp_library = c.fp_library
      bomline.symbol = c.symbol
      bomline.sym_library = c.sym_library
      bomline.datasheet = c.datasheet
      bomline.fields = c.fields
      bom.append(bomline)

  # sort bom ref entries by alphabet
  # ex: C1 C2 C5 instead of C2 C5 C1

  # sort bom list by ref
  # ex: C1 C2 ~~~~
  #     C3    ~~~~
  #     D1 D2 ~~~~
  #     S1    ~~~~
  #     
  bom.sort(key=lambda x: x.refs)

  title_string = 'Ref,Qty,Value,Footprint,Footprint Library,Symbol,Symbol Library,Datasheet'

  # create master output string including the dynamic fields

  for f in optional_fields:
    title_string = title_string+','+f
  title_string = title_string+'\n'

  # write to the master output file

  outfile = bom_outfile_csv

  with open(outfile,'w') as obom:
    obom.write(title_string)
    for b in bom:
      
      obom.write(b.refs+','+str(b.qty)+','+b.value+','+b.footprint+','+b.fp_library+','+ \
                 b.symbol+','+b.sym_library+','+b.datasheet)

      for of in optional_fields:
        for bf in b.fields:
          if of == bf[0]:
            obom.write(','+bf[1])
      obom.write('\n')

  # Create the master Seeed output

  outfile = bom_outfile_seeed_csv
  
  with open(outfile,'w') as obom:
    obom.write('Location,MPN/Seeed SKU,Quantity\n')
    for b in bom:
      obom.write(b.refs+',')

      for bf in b.fields:
        if bf[0] == 'MF_PN':
          obom.write(bf[1]+',')

      obom.write(str(b.qty)+'\n')

  # Create a markdown file for github with each vendor
  # given its own table for easy reading
  # Also create the vendor-specific csv files

  outbom_list = []
  outcsv_list = []
  outfile_md = bom_outfile_md

  for v in vendors:

    outfile_csv = data['bom_dir']+'/'+data['projname']+'-'+data['version']+'-bom-'+v.lower()+'.csv'
    which_line = 0

    for line in bom:
      if which_line is 0:
        outcsv_list.append('Ref,Qty,Description,Digikey PN')
        outbom_list.append('|Ref|Qty|Description|'+v.capitalize()+' PN|')
        outbom_list.append('|---|---|-----------|------|')
        which_line = 1

      for f in line.fields:
        if f[1] == v.capitalize():
          md_line_string = '|'+line.refs+'|'+str(line.qty)+'|'
          csv_line_string = line.refs+','+str(line.qty)+','
          for i in line.fields:
            if i[0] == 'Description':
              md_line_string = md_line_string + i[1]+'|'
              csv_line_string = csv_line_string + i[1]+','
          for i in line.fields:
            if i[0] == 'S1_PN':
              md_line_string = md_line_string+i[1]+'|'
              csv_line_string = csv_line_string+i[1] 
          outbom_list.append(md_line_string)
          outcsv_list.append(csv_line_string)

    outbom_list.append('')

    with open(outfile_csv,'w') as ocsv:
      for line in outcsv_list:
        ocsv.write(line+'\n')

    if v == vendors[-1]:
      outbom_list.append('')
    
  with open(outfile_md,'w') as obom:
    for line in outbom_list:
      obom.write(line+'\n')

###########################################################
#
#                   create_zip_files 
#
# inputs:
# - data object
# 
# what it does:
# - creates generic zip file for boards (gko, xln)
# - creates zip file for osh stencils (gko, gtp, gbp)
#
###########################################################

def create_zip_files(data):

  # Create zip file for OSH Park and Seeed manufacturing

  files = []

  for ext in ('*.xln','*.gbl','*.gtl','*.gbo','*.gto','*.gbs',
              '*.gts','*.gbr','*.gko','*.gtp','*.gbp',):
    files.extend(glob.glob(os.path.join(data['gerbers_dir'], ext)))

  os.chdir(data['gerbers_dir'])
  ZipFile = zipfile.ZipFile(data['projname']+'-'+data['version']+"-gerbers.zip", "w")
  for f in files:
    ZipFile.write(os.path.basename(f))
  os.chdir("..")

  # Create zip file for stencils
  # always using .gko (outline) and .gtp,.gbp (paste) files

  files = []

  for ext in ('*.gko','*.gtp','*.gbp'):
    files.extend(glob.glob(os.path.join(data['gerbers_dir'], ext)))

  os.chdir(data['gerbers_dir'])
  ZipFile = zipfile.ZipFile(data['projname']+'-'+data['version']+"-stencil.zip", "w")
  for f in files:
    ZipFile.write(os.path.basename(f))
  os.chdir("..")

###########################################################
#
#                    create_pos_file    
#
# TODO: figure out how to get the pos file by 
#       command line out of pcbnew module
#
###########################################################

def create_pos_file():
  print "unable to create pos file at this time"

###########################################################
#
#                     update_readme
#
# inputs:
# - data object
# 
# what it does:
# - creates README.md if it doesn't already exist
# - appends BOM to README if there's a commented section
#
# returns nothing
#
###########################################################

def update_readme(data):

  # create the README if we don't have one

  readme = 'README.md'
  if not os.path.isfile(readme):
    create_readme(readme,data)

  # now update the README

  newbomlinefile = data['bom_dir']+'/'+data['projname']+'-'+data['version']+'-bom-readme.md'

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
#
#                      create_pdf                      
#
# inputs: 
# - data object
#
# what it does:
# - creates a temporary file which will be pandoc input
# - copies over the README to the temporary file, 
#   ignoring anything in the title 
# - uses the appropriate LaTeX template
# - calls pandoc to create the PDF from temporary file
# - remove the temporary file 
# 
# TODO: make adjustment to the image width by argument
#
# returns nothing
#
###########################################################

def create_pdf(data):

  tempfile = 'temporary.md' 
  src = 'README.md'
  src_list = []
  title_flag = False
 
  with open(src,'r') as s:
    for line in s:
      if 'start title' in line:
        title_flag = True

      if title_flag is True:
        if 'end title' in line:
          title_flag = False
      else:
        if 'assembly.png' in line:
          src_list.append('\ \n')
          src_list.append('\n')
          line = line.replace('assembly.png)','assembly.png)')
          src_list.append(line)
          src_list.append('\n')
        elif 'schematic.png' in line:
          src_list.append('\ \n')
          src_list.append('\n')
          line = line.replace('schematic.png)','schematic.png){width=60%}')
          src_list.append(line)
          src_list.append('\n')
        elif 'preview.png' in line:
          src_list.append('\ \n')
          src_list.append('\n')
          line = line.replace('preview.png)','preview.png)')
          src_list.append(line)
          src_list.append('\n')
        elif '.png' in line:
          src_list.append('\ \n')
          src_list.append('\n')
          line = line.replace('.png)','.png){width=48%}')
          src_list.append(line)
          src_list.append('\ \n')
          src_list.append('\n')
        else:
          src_list.append(line)
 
  with open(tempfile,'w') as tfile:
    tfile.write('---\n')
    tfile.write('title: '+data['title']+'\n')
    tfile.write('version: '+data['version']+'\n')
    tfile.write('description: '+data['description']+'\n')
    tfile.write('company: '+data['company']+'\n')
    tfile.write('email: '+data['email']+'\n')
    tfile.write('website: '+data['website']+'\n')
    tfile.write('license: '+data['license']+'\n')
    if 'author' in data:
      tfile.write('author: '+data['author']+'\n')
    tfile.write('---\n')
    tfile.write('\n')

    for line in src_list:
      tfile.write(line)

  latex_template_dir = data['template_dir'][:-9]

  # create PDF
  call(['pandoc','-fmarkdown-implicit_figures','-R','--data-dir='+latex_template_dir,'--template='+data['template_latex'],'-V','geometry:margin=1in',tempfile,'-o',data['projname']+'-'+data['version']+'.pdf']) 

  # remove input file
  call(['rm',tempfile])

###########################################################
#
#                 create_release_zipfile                      
#
# inputs: 
# - data object
#
# what it does:
# - creates the final release containing
#   - seeed .csv bom
#   - gerbers zip
#   - stencil zip
#   - project PDF 
# 
# returns nothing
#
###########################################################

def create_release_zipfile(data):

  release_zip = zipfile.ZipFile(data['projname']+'-'+data['version']+'.zip','w')

  os.chdir(data['bom_dir'])
  release_zip.write(data['projname']+'-'+data['version']+'-bom-seeed.csv')

  os.chdir('../'+data['gerbers_dir'])
  release_zip.write(data['projname']+'-'+data['version']+'-gerbers.zip')
  release_zip.write(data['projname']+'-'+data['version']+'-stencil.zip') 
  
  os.chdir('..')
  release_zip.write(data['projname']+'-'+data['version']+'.pdf') 

###########################################################
#
#                      main
#
# you can either create a new project
# or you can generate manufacturing files, boms, and PDF
# from an existing project
#
# they are mutually exclusive options
#
###########################################################

if __name__ == '__main__':

  parser = argparse.ArgumentParser('Kingfisher automates KiCad project management.\n')
  parser.add_argument('name',action='store',help="Name of the project")
  parser.add_argument('-n','--new',action='store_true',default=False,dest='new',help='create a new project')
  parser.add_argument('-m','--mfr',action='store_true',default=False,dest='mfr',help='create manufacturing output files')
  parser.add_argument('-b','--bom',action='store_true',default=False,dest='bom',help='create bill of materials output files')
  parser.add_argument('-p','--pdf',action='store_true',default=False,dest='pdf',help='create output PDF file')
  parser.add_argument('-v',action='store',dest='version',help='update existing version in proj.json')
  parser.add_argument('-t',action='store',dest='template',help='only used with new project; which template?')
  args = parser.parse_args()

  if args.new:
    if (args.mfr or args.bom or args.pdf):
      print "Creating a new project but not performing any other operations."
      print "Try again without the -n file to create output files."
    else:
      print "Creating a new project."
    if os.path.exists(args.name):
      x = raw_input("This folder exists. Do you want to remove it and start fresh? Y/N: ")
      if 'y' or 'Y' in x:
        call(['rm','-rf',args.name])
        print 
      else:
        print "Try again with a different project name. Exiting program."
    if args.version:
      version = 'v'+args.version
    else:
      version = 'v1.0'
    create_new_project(args.name,args.template,version)

  else:

    # read in the proj.json if it exists
    # error gracefully if it does not
    if os.path.isfile(args.name+'/proj.json'):
      with open(args.name+'/proj.json') as jfile:
        if args.version:
          update_version(args.name,args.version)
          print "Remember! The README.md does not update version automatically."
          print "Update it before you generate the PDF!"
        data = json.load(jfile)
    else:
      print "This project is missing a proj.json file. Leaving program."
      exit()

    print 'This is the',data['title'],'project:'
    print data['description']+'\n'

    # all plotting is done from the same dir as the kicad files
    cwd = os.getcwd()
    os.chdir(data['projname'])

    if args.mfr:
      print "Creating the manufacturing file outputs."
      plot_gerbers_and_drills(data['projname'],data['gerbers_dir'])
      board_dims = get_board_size(data['projname'],data['gerbers_dir'])
      
      width_in = board_dims[0]
      height_in = board_dims[1]
      width_mm = board_dims[2]
      height_mm = board_dims[3]
      width_pixels = board_dims[4]
      height_pixels = board_dims[5]

      print '\nThis board is '+width_in+' x '+height_in+' inches (' \
            +width_mm+' x '+height_mm+' mm)'

      create_assembly_diagrams(data['projname'],data['gerbers_dir'],width_pixels, height_pixels) 
      create_image_previews(data['projname'],data['gerbers_dir'],width_pixels, height_pixels) 
      
    if args.bom:
      print "Creating the bill of materials, which will update the README."
      create_bill_of_materials(data)
      create_zip_files(data)
      create_pos_file()
      update_readme(data)

    if args.pdf: 
      print "Creating or updating the PDF."
      create_pdf(data)
      create_release_zipfile(data)

  print "\nProgram completed running successfully."
  exit()
