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

  ## create the lists of parts, values, and header symbols

  print filename
  for line in open(filename, 'r'):
    aPart = LibraryPart()
    line = line.replace('Reference','-').replace('\'','').split(',')
    if line[1] != '-': #or if line[1] != 'Reference':
      aPart.WBoxSKU = line[0]
      aPart.Reference = line[1]
      aPart.Value = line[2]
      aPart.Description = line[3]
      aPart.HeaderSymbol = line[4]
      aPart.KiCadFootprint = line[5]
      aPart.Datasheet = line[6]
      aPart.Package = line[7]
      aPart.MF_Name = line[8]
      aPart.MF_PN = line[9]
      aPart.S1_Name = line[10]
      aPart.S1_PN = line[11]
      aPart.Verified = line[13]
      PartsList.append(aPart)
    else: 
      print line[0], 'is not a valid package part for KiCad.'

  PartsList.sort()

  ValueList = []
  for part in PartsList:
    ValueList.append(part.Value)

  SortedSetValueList = sorted(set(ValueList))

  HeaderSymbolList = []
  for part in PartsList: 
    HeaderSymbolList.append(part.HeaderSymbol)

  SortedSetHeaderSymbolList = sorted(set(HeaderSymbolList))

  ## create the DCM file

  dcmfile = open('wickerlib.dcm','w')
  dcmfile.write('EESchema-DOCLIB  Version 2.0\n')
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
        libfile.write('F4 \"'+part.Package+'\" 0 -350 50 H I C CIN "Package"\n')
        libfile.write('F5 \"'+part.MF_Name+'\" 0 -350 50 H I C CIN "MF_Name"\n')
        libfile.write('F6 \"'+part.MF_PN+'\" 0 -350 50 H I C CIN "MF_PN"\n')
        libfile.write('F7 \"'+part.S1_Name+'\" 0 -350 50 H I C CIN "S1_Name"\n')
        libfile.write('F8 \"'+part.S1_PN+'\" 0 -350 50 H I C CIN "S1_PN"\n')
        libfile.write('F9 \"'+part.Description+'\" 0 -350 50 H I C CIN "Description"\n')
        libfile.write('F10 \"Not Verified\" 0 -350 50 H I C CIN "Verified"\n')
        print part.S1_Name
        libfile.write('DRAW\n')
        symbol_dict = ''
        libfile.write('S -100 100 100 -100 0 1 5 f\n')
        libfile.write('ENDDRAW\n')
        libfile.write('ENDDEF\n')
        break
  libfile.write('#\n')
  libfile.write('#End Library\n')
  libfile.close()

  ## create the skeleton of the header module for the symbol picture library
  ## uncomment and use only once, if none exists. 

  ## headerfile = open('headersymbols.py','w')
  ## headerfile.write('#!/usr/bin/python\n')
  ## headerfile.write('# Create Wickerlib\n')
  ## for value in SortedSetHeaderSymbolList:
  ##   print value
  ##   headerfile.write('# '+value+'\n\n')
  ## headerfile.close()

