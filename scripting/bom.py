#!/usr/bin/python

import sys, os, argparse

# create a schematic class
class Sch():
  path = ''
  name = ''
  title = ''
  company = ''
  rev = ''
  date = ''
  comment1 = ''
  comment2 = ''
  comment3 = ''
  comment4 = ''

  def print_schematic(self):
    print '------------------------'
    print 'Project',self.name,self.rev
    print self.title
    print self.company 
    print self.date
    print self.comment1
    print self.comment2
    print self.comment3
    print self.comment4

# create a component class
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
  
# accept args
# script needs a name and version number
# it automatically takes the net file
# creates the outputs

parser = argparse.ArgumentParser()

parser.add_argument("-n","--name", nargs=1, help="name")
parser.add_argument("-v","--version", nargs=1, help="list all orders on a panel")

args = parser.parse_args()

components = []

# main

if __name__ == "__main__":

  print '------------------------'
  print "wickerbom.py"
  print '------------------------'
  print "Creating the bill of materials from the netlist:"
 
  sch = Sch()

  if args.name is None:
    sch.path = os.getcwd()
    sch.name = os.path.basename(sch.path)
  else:
    sch.name = args.name[0]

  if args.version is None:
    sch.rev = ''
  elif 'v' in args.version[0]:
    sch.rev = args.version[0]
  else: 
    sch.rev = 'v'+args.version[0]

  sch.path = sch.path+'/'+sch.name+'.net'

  comp_flag = False
  comp_count = 0
  fields_flag = False

  with open(sch.path,'r') as schfile:
    for line in schfile:
      if 'components' in line:
        comp_flag = True
      if 'libparts' in line:
        comp_flag = False

      if comp_flag is True:
        if 'comp' in line:
          if comp_count > 0:
            components.append(comp)
          comp = Comp()
          comp_count = comp_count + 1
          comp.ref = line.replace(')','').replace('\n','').strip('(comp (ref ')
        if 'value' in line: 
          comp.value = line
          comp.value = line.replace(')','').replace('\n','').strip('(value ') 
        if 'footprint' in line: 
          if ':' not in line:
            comp.footprint = line.replace('       (footprint ','').replace(')\n','')
            comp.fp_library = 'None'
          else:
            line = line.replace('      (footprint ','').replace(')\n','').split(':')
            comp.footprint = line[1]
            comp.fp_library = line[0]
        if 'datasheet' in line: 
          comp.datasheet = line.replace('(datasheet ','').lstrip(' ').replace(')\n','')
        if 'libsource' in line:
          line = line.replace('(libsource (lib ','').replace('))','').lstrip(' \n').split(') (')
          comp.sym_library = line[0]
          comp.symbol = line[1].lstrip('part ').replace('\n','')

        if 'fields' in line:
          fields_flag = True
          fields = []
        if '))' in line:
          fields_flag = False

        if fields_flag is True:
          if 'fields' not in line:
            if '\"' in line:
              line = line.replace('\"','')
            line = line.replace('(field (name ','').lstrip(' ').replace(')\n','').split(') ')
            comp.fields.append((line[0],line[1]))

# open and read the netlist

 

# collect a list of components in the netlist

# 
