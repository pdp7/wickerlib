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
    line = line.replace('Reference','-').replace('\'','').split(',')
    if line[1] != '-': #or if line[1] != 'Reference':
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

  ## create a list of just the Value field without duplicates
  ## so we know which symbols we need to create

  ValueList = []
  for part in PartsList:
    ValueList.append(part.Value)

  ## create the DCM file

  dcmfile = open('wickerlib.dcm','w')
  dcmfile.write('EESchema-DOCLIB  Version 2.0\n')
  SortedSetValueList = sorted(set(ValueList))
  for value in SortedSetValueList:
    for part in PartsList:
      if part.Value == value:
        dcmfile.write('#\n')
        dcmfile.write('$CMP '+part.Value+'\n')
        dcmfile.write('D '+part.Description+'\n')
        dcmfile.write('F '+part.Datasheet+'\n')
        dcmfile.write('$ENDCMP\n')
        break
  dcmfile.write('#End Doc Library\n')
  dcmfile.close()

  ## create the LIB file
  libfile = open('wickerlib.lib','w')
  libfile.write('EESchema-LIBRARY Version 2.3\n')
  libfile.write('#encoding utf-8\n')
  for value in SortedSetValueList:
    print value
    for part in PartsList:
      if part.Value == value:
        libfile.write('#\n')
        libfile.write('# '+part.Value+'\n')
        libfile.write('#\n')
        libfile.write('DEF '+part.Value+' '+part.Reference+' 0 40 Y Y 1 F N\n')
        libfile.write('F0 \"'+part.Reference+'\" 0 450 50 H V L CNN\n')
        libfile.write('F1 \"'+part.Value+'\" 0 350 50 H V L CNN\n')
        libfile.write('F2 \"'+part.Package+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F3 \"'+part.Datasheet+'\" 0 0 5 H I C CNN\n')
        libfile.write('F4 \"'+part.Package+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F5 \"'+part.MF_Name+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F6 \"'+part.MF_PN+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F7 \"'+part.S1_Name+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F8 \"'+part.S1_PN+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F6 \"'+part.Description+'\" 0 -350 50 H I C CIN\n')
        libfile.write('F6 \"Not Verified\" 0 -350 50 H I C CIN\n')
        print part.S1_Name
        libfile.write('DRAW\n')
        libfile.write('S -10 10 10 -10 0 1 10 f\n')
        libfile.write('ENDDRAW\n')
        libfile.write('ENDDEF\n')
        break
  libfile.write('#\n')
  libfile.write('#End Library\n')
  libfile.close()

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

