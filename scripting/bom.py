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


