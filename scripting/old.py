#!/usr/bin/python
# kingfisher creates the manufacturing files and documentation

import argparse, sys
from subprocess import call

class Client():
  company_name = ''
  client_name = ''
  contact = ''

###########################################################
#                    parse the arguments                  #
###########################################################

parser = argparse.ArgumentParser()
parser.add_argument('function',nargs=1,help='choose "co" (new company), "proj" (new project), or "out" (create manufacturing files)')
parser.add_argument('name',nargs=1,help='set the name')

parser.add_argument('--version','-v',nargs=1,metavar=('VERSION'),help='set version number, "1.1"')
parser.add_argument('--schonly','-s',action='store_true',default=False,help='use this flag if no board exists.')
parser.add_argument('--brdonly','-b',action='store_true',default=False,help='use this flag if no schematic exists.')
parser.add_argument('--pdfonly','-p',action='store_true',default=False,help='use this flag to rebuild PDF only')
parser.add_argument('--outline','-o',nargs=1,metavar=('LAYER'),help='move contents of this layer to outline.')

if len(sys.argv)==1:
    parser.print_help()
    sys.exit(1)

args = parser.parse_args()

def parse_arguments():

  if 'pr' in args.function[0]:
    print '- Create a new project in an existing company called',args.name[0]
  elif 'co' in args.function[0]:
    print '- Create a new company called',args.name[0]
  elif 'out' in args.function[0]:
    print '- Generate the output files for the project',args.name[0]
  else:
    parser.print_help()
  
  if args.version: 
    print 'Version:',args.version[0]

  if args.schonly:
    print 'Only the schematic exists.' 

  

###########################################################
#                      main                               #
###########################################################

if __name__ == "__main__":

  print "Kingfisher v1.0 - a Wickerbox tool for KiCad project management.\n" 

  parse_arguments()

  call(['pandoc','-fmarkdown-implicit_figures','-R','--toc','--template=projectoutput.tex','-V','geometry:margin=1in','README.md','-o',name+'-'+version+'.pdf'])
