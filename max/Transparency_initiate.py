# -*- coding: utf-8 -*-
"""
Created on Wed Sep  9 11:11:14 2015

@author: mx
"""


import sys
import os
import datetime
        

outdir = str(sys.argv[1])      
outfile = str(sys.argv[2])      
sanityfile = str(sys.argv[3])



######################################################################### 
### Create outdir
#########################################################################  
def initiate_outdir(outdir):
    if not os.path.exists(outdir): os.mkdir(outdir)
        


######################################################################### 
### Write output file
#########################################################################     
def initiate_outfile(outfile): 
    
    if not os.path.exists(outfile):
        with open(outfile, 'w') as myfile:
            myfile.write('#MJD IMAGE_ID MEDIAN MAD LOWER_QUARTER UPPER_QUARTER MEAN SEM STD\n')    
    else:
        print '!!! WARNING: OUTPUT FILE ALREADY EXISTS, DATA WILL BE APPENDED TO EXISTING FILE !!!'
        timestamp = datetime.datetime.utcnow().isoformat()
        with open(outfile, 'a') as myfile:
            myfile.write('# APPENDIX ON '+str(timestamp)+' (UTC)\n')
            


######################################################################### 
### Write sanity file
######################################################################### 
def initiate_sanity(sanityfile):
    if not os.path.exists(sanityfile):
        with open(sanityfile, 'w') as myfile:
            myfile.write('Outlying flux ratios at:\n')
            myfile.write('IMAGE_ID    x    y    flux    ref_flux\n')    
    else:
        print '!!! WARNING: SANITY FILE ALREADY EXISTS, DATA WILL BE APPENDED TO EXISTING FILE !!!'
        timestamp = datetime.datetime.utcnow().isoformat()
        with open(outfile, 'a') as myfile:
            myfile.write('# APPENDIX ON '+str(timestamp)+' (UTC)\n')       
       
       
######################################################################### 
### MAIN
#########################################################################  
if __name__ == '__main__':
    initiate_outdir(outdir)
    initiate_outfile(outfile)
    initiate_sanity(sanityfile)
     