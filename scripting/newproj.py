#!/usr/bin/python

import os,json,subprocess,datetime

projname = 'test-project'
title = 'Test Project'
version = '1.0'
description = 'A super cool new hardware design for counting kittens.'
company = 'Wickerbox Electronics'
author = 'Jenner Hanni'
email = 'jenner@wickerbox.net'
website = 'http://wickerbox.net/'
license = 'CERN Open Hardware License v1.2'
template = 'wickerbox-2layer'
now = datetime.datetime.now()
date_create = now.strftime('%B %d, %Y')
date_update = ''

dirWickerlib = '/home/wicker/wickerlib/'
dirTemplates = '/home/wicker/wickerlib/templates/'

data = {'projname':projname,
        'title':title,
        'author':author,
        'version':version,
        'description':description,
        'company':company,
        'email':email,
        'website':website,
        'license':license,
        'template':template,
        'date_create':date_create, 
        'date_update':date_update}

def create_README():

  filename='README.md'

  if os.path.exists(filename) is True:
    s = raw_input("README.md exists. Do you want to overwrite it? Y/N: ")
    if 'Y' in s or 'y' in s:
      print "great, we'll overwrite."
    else:
      print "okay, closing program."
      exit()
   
  with open(filename,'w') as o:
    o.write('# '+title+' v'+version+'\n')
    o.write(description+'\n\n')
    o.write('## Introduction\n\n')
    o.write('Intro text.\n\n')
    o.write('<!--- start bom --->\n\n')
    o.write('<!--- end bom --->\n\n')
    o.write('![Assembly Diagram](assembly.png)\n\n')
    o.write('![Gerber Preview](preview.png)\n\n')

def create_proj_json():

  filename='proj.json'
  
  if os.path.exists(filename) is True:
    s = raw_input("proj.json exists. Do you want to overwrite it? Y/N: ")
    if 'Y' in s or 'y' in s:
      print "great, we'll overwrite."
    else:
      print "okay, closing program."
      exit()

  with open('proj.json', 'w') as outfile:
      json.dump(data, outfile, indent=4, sort_keys=True, separators=(',', ':'))

def select_template():

  template_list = []

  # update template list 
  for x in os.listdir(dirTemplates):
    if '.zip' not in x and '.md' not in x:
      template_list.append(x)

  temp_list = sorted(template_list)
  template_list = temp_list

  print '------ Template List ---------'
  for t in template_list: 
    print t

  # get user input

  dt = raw_input('\nWhich template to use? ' )

  # compare user input to existing template list

  if dt in template_list: 
    data['template'] = dt
  else: 
    print "That was not a valid template."
  

def create_KiCad_project():
  print "\ncreating KiCad Project from template", data['template']

  templatesrc = dirTemplates+data['template']+'/'+data['template']

  subprocess.call(['cp',templatesrc+'.kicad_pcb',data['projname']+'.kicad_pcb'])
  subprocess.call(['cp',templatesrc+'.pro',data['projname']+'.pro'])
  subprocess.call(['cp',templatesrc+'.sch',data['projname']+'.sch'])


  # replace entire title block of .kicad_pcb file 

  # replace entire title block of .sch file

  fixfile_list = [data['projname']+'.sch',data['projname']+'.kicad_pcb']

  for f in fixfile_list:

    fixfile_temp = [] 

  # need to fix handling of kicad title block logic

  with open(f,'r') as fixfile:
    for line in fixfile:
      if '  (title_block' in line:
        pcb_title_flag = True
      if pcb_title_flag is True:
        if '  )' in line:
          pcb_title_flag = False

      if 'Title ""' in line:
        fixfile_temp.append('Title "'+data['title']+'"\n')
      elif '(title ' in line:
        fixfile_temp.append('(title '+data['title']+')\n')
      elif 'Rev ""' in line:
        fixfile_temp.append('Rev "'+data['version']+'"\n')
      elif '(rev ' in line:
        fixfile_temp.append('(rev '+data['version']+')\n')
      elif 'Date ""' in line:
        fixfile_temp.append('Date "'+data['date_create']+'"\n')
      elif '(date ' in line:
        fixfile_temp.append('(date '+data['date_create']+')\n')
      elif 'Comp ""' in line:
        fixfile_temp.append('Comp "'+data['license']+'"\n')
      elif '(company ' in line:
        fixfile_temp.append('    (company '+data['company']+'")\n')
      elif 'Comment1 ""' in line:
        fixfile_temp.append('Comment1 "'+data['email']+' - '+data['website']+'"\n')
      elif '(comment 1 ' in line:
        fixfile_temp.append('    (comment 1 "'+data['email']+' - '+data['website']+'")\n')
      elif 'Comment2 ""' in line:
        fixfile_temp.append('Comment2 "Designed by '+data['author']+' for '+data['company']+'"\n')
      elif '(comment 2 ' in line:
        fixfile_temp.append('    (comment 2 "Designed by '+data['author']+' for '+data['company']+'")\n')
      else:
        fixfile_temp.append(line)

    with open(f,'w') as fixfile:
      for line in fixfile_temp:
        fixfile.write(line)

if __name__ == '__main__':

  select_template()

  create_proj_json()

  create_README()

  create_KiCad_project()
