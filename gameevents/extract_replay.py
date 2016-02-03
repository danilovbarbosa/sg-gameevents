#!/usr/local/bin/python2.7
# encoding: utf-8
'''
extract_replay -- shortdesc

extract_replay is a description

It defines classes_and_methods

@author:     user_name

@copyright:  2015 organization_name. All rights reserved.

@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os

from argparse import ArgumentParser
#from argparse import RawDescriptionHelpFormatter

import re

__all__ = []
__version__ = 0.1
__date__ = '2015-12-08'
__updated__ = '2015-12-08'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    

    template = """$FILENAME putyourlix.txt
$BUILT_REQUIRED 2014-07-01 20:40:34
#VERSION_REQUIRED 2015080900

+PLAYER 0 Garden user

%HERE_COMES_THE_DATA%

$BUILT 2014-07-01 20:40:34
$AUTHOR Michael
$GERMAN 
$ENGLISH Put Your Lix on Ice

#SIZE_X 1280
#SIZE_Y 400
#TORUS_X 0
#TORUS_Y 0
#BACKGROUND_RED 0
#BACKGROUND_GREEN 0
#BACKGROUND_BLUE 0

#SECONDS 0
#INITIAL 20
#REQUIRED 20
#SPAWN_INTERVAL 30
#SPAWN_INTERVAL_FAST 4

#CLIMBER 5
#FLOATER 1
#EXPLODER 1
#BLOCKER 1
#PLATFORMER 5
#MINER 5
#JUMPER 5
#BATTER 5

:matt/winter/Hatch.H: 272 240

:matt/winter/Goal.G: 1040 208

:simon/crystal.W: 640 352
:simon/crystal.W: 688 352

:matt/winter/15: 81 188
:matt/winter/17: 64 80
:matt/winter/04: 64 176
:matt/winter/17: 32 160 frr
:matt/winter/05: 16 208
:matt/winter/16: 128 288 frr
:matt/winter/04: 48 272 frr
:matt/winter/10: 176 320
:matt/winter/10: 320 288
:matt/winter/10: 384 336 frr
:matt/winter/15: 192 224
:matt/winter/00: 304 176
:matt/winter/16: 464 224
:matt/winter/17: 528 96 frr
:geoo/steel/dark_64x64o.S: 608 208
:matt/winter/17: 560 192
:matt/winter/05: 512 144
:matt/winter/04: 544 272
:geoo/steel/dark_64x64o.S: 672 208
:matt/winter/01: 400 160
:matt/winter/01: 432 176 frr
:matt/winter/01: 432 144
:matt/winter/07: 176 16 rr
:matt/winter/07: 192 32 rr
:matt/winter/07: 208 16 rr
:matt/winter/07: 256 32 rr
:matt/winter/07: 272 48 rr
:matt/winter/07: 144 -16 rr
:matt/winter/10: 128 -48 rr
:matt/winter/07: 304 32 rr
:matt/winter/07: 320 16 rr
:matt/winter/07: 352 48 rr
:matt/winter/07: 368 32 rr
:matt/winter/07: 384 48 rr
:matt/winter/07: 448 32 rr
:matt/winter/07: 464 32 rr
:matt/winter/10: 272 -32 frr
:matt/winter/07: 496 0 rr
:matt/winter/07: 512 16 rr
:matt/winter/07: 528 0 rr
:matt/winter/07: 576 -32 rr
:matt/winter/10: 400 -64 f
:matt/winter/16: 720 160 frr
:matt/winter/10: 736 240
:matt/winter/05: 704 224
:matt/winter/10: 832 208 frr
:matt/winter/05: 944 96
:matt/winter/10: 944 256
:matt/winter/16: 1120 272 frr
:matt/winter/01: 1072 272
:matt/winter/01: 1104 256
:matt/winter/03: 1008 272
:matt/winter/10: 1024 336
:matt/winter/10: 752 304
:matt/winter/10: 944 336
:matt/winter/04: 864 272 frr
:matt/winter/07: 592 0 rr
:matt/winter/07: 640 0 rr
:matt/winter/07: 656 16 rr
:matt/winter/07: 672 0 rr
:matt/winter/07: 720 0 rr
:matt/winter/07: 736 -16 rr
:matt/winter/10: 576 -64 f

    """

    program_name = os.path.basename(sys.argv[0])
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2015 organization_name. All rights reserved.

  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0

  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))
    try:
        # Setup argument parser
        #parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser = ArgumentParser(prog='PROG', usage='%(prog)s path')
        #parser.add_argument("-r", "--recursive", dest="recurse", action="store_true", help="recurse into subfolders [default: %(default)s]")
        #parser.add_argument("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %(default)s]")
        #parser.add_argument("-i", "--include", dest="include", help="only include paths matching this regex pattern. Note: exclude is given preference over include. [default: %(default)s]", metavar="RE" )
        #parser.add_argument("-e", "--exclude", dest="exclude", help="exclude paths matching this regex pattern. [default: %(default)s]", metavar="RE" )
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        #parser.add_argument(dest="paths", help="paths to folder(s) with source file(s) [default: current]", metavar="path", nargs='+')
        #parser.add_argument('filename', type=str, help='The filename to extract the replays')
        parser.add_argument('mypath', type=str, help='The directory with the CSV files to convert. Output replay files will also be placed here.')
        # Process arguments
        args = parser.parse_args()

        mypath = args.mypath
       
        files = [f for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
        #print files
        
        for filename in files:
            print("-------"*4)
            print "Converting file: %s"% filename
            with open(os.path.join(mypath, filename)) as f:
                counter = 1
                content = f.read()
                #print(content)
                content = re.sub('timestamp,action,level,update,which_lix,lix_required,lix_saved,skills_used,seconds_required,seconds_used\s','',content)
                content = re.sub('[^,]+,(STARTGAME|ENDGAME)[,]+\s','',content)
                p = re.compile('[^,]+,ENDLEVEL,levels/putyourlix.txt,,,,,,,\s')
                splitcontent = p.split(content)
    #             print(len(splitcontent))
    #             print('--'*10)
    #             print(splitcontent[0])
    #             print('--'*10)
    #             print(splitcontent[12])
                for item in splitcontent:
                    newcontent = ""
                    lines = item.split("\n")
                    #print(lines)
                    for line in lines:
                        if "ASSIGN" in line:
                            fields = line.split(",")
                            newline = "! %s 0 %s %s \n" % (fields[3],fields[1],fields[4])
                            newcontent = newcontent + newline
                    newfilename = filename + ".%03d.txt" % counter
                    newfile = open(os.path.join(mypath, newfilename), 'w' )
                    newfilecontent = re.sub('%HERE_COMES_THE_DATA%', newcontent, template)
                    newfile.write(newfilecontent)
                    newfile.close()
                    counter = counter+1
                        
                print("-------"*4)
            
        print ""
        print "Done!"
        print ""
        return 0
    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception as e:
       
        if DEBUG or TESTRUN:
            raise(e)
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
#     if DEBUG:
#         sys.argv.append("-h")
#         sys.argv.append("-v")
#         sys.argv.append("-r")
#     if TESTRUN:
#         import doctest
#         doctest.testmod()
#     if PROFILE:
#         import cProfile
#         import pstats
#         profile_filename = 'extract_replay_profile.txt'
#         cProfile.run('main()', profile_filename)
#         statsfile = open("profile_stats.txt", "wb")
#         p = pstats.Stats(profile_filename, stream=statsfile)
#         stats = p.strip_dirs().sort_stats('cumulative')
#         stats.print_stats()
#         statsfile.close()
#         sys.exit(0)
    sys.exit(main())