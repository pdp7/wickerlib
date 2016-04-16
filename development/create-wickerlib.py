#!/usr/bin/python
# Create Wickerlib

import time
import sys
import fnmatch
import os
import glob
from collections import namedtuple
import re
import subprocess

## Initial Creation of Wickerlib

script, filename = sys.argv

class LibraryPart(object):

  WBoxSKU = None
  Reference = None
  Description = None
  Value = None
  KiCadFootprint = None
  Datasheet = None
  Package = None
  MF_Name = None
  MF_PN = None
  S1_Name = None
  S1_PN = None
  Verified = None

# globals

PartsList = []

if __name__ == "__main__":

## create the parts list

  print filename
  for line in open(filename, 'r'):
    aPart = LibraryPart()
    line = line.replace('Reference','-').split(',')
    if line[1] != '-':#or if line[1] != 'Reference':
      aPart.WBoxSKU = line[0]
      aPart.Reference = line[1]
      aPart.Description = line[2]
      aPart.Value = line[3]
      aPart.KiCadFootprint = line[4]
      aPart.Datasheet = line[5]
      aPart.Package = line[6]
      aPart.MF_Name = line[7]
      aPart.MF_PN = line[8]
      aPart.S1_Name = line[9]
      aPart.S1_PN = line[10]
      aPart.Verified = line[11]
      PartsList.append(aPart)
    else: 
      print line[0], 'is not a valid package part for KiCad.'

  PartsList.sort()
  for part in PartsList: 
#    print part.Reference  
    print part.WBoxSKU, part.Reference, part.Description, part.Value, part.KiCadFootprint, part.Datasheet, part.Package, part.MF_Name, part.MF_PN, part.S1_Name, part.S1_PN, part.Verified


# capture command line arguments
#script, filename, wickerlibname = sys.argv
#
## main
#if __name__ == "__main__":
#
#  print wickerlibname, filename
#  for line in open(wickerlibname, 'r'):
#    if 'Wbox_SKU' in line:
#      print line.split(',')
    

#  for line in open(filename, 'r'):
#    print line.split(',')
    

# I have an inventory of actual parts
# I have an existing wickerlib library 
# that contains symbols for each of those parts
# but might contain multiple symbols for each of those parts

# The information appears to get stored in alphabetical order, 
# so we'll have to use the right-hand split section for the 
# category name to identify.

# NAME 
# F0   Reference
# F1   Value
# F2   Footprint
# F3   Datasheet
# F4   Description
# F5   Wbox_SKU
# F6   Source1_PN
# F7   MF_Name
# F8   Source1
# F9   Package
# F10  MF_PN

# Read in the list of SKUs that currently exist in wickerlib

