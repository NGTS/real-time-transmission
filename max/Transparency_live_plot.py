"""
Maximilian N. Guenther
Cavendish Astrophysics
University of Cambridge

Created: 15 April 2015
Last update: 12 June 2015
"""



import sys
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import timeit



outdir = str(sys.argv[1])
outfile = str(sys.argv[2])


def fct(outdir,outfile):
    
    
    #########################################################################
    # Python settings
    #########################################################################      
    font = {#'family' : 'normal',
            'weight' : 'normal',
            'size'   : 18}
    matplotlib.rc('font', **font)   
    matplotlib.rc('legend',**{'fontsize':18})
        
        
    
    ######################################################################### 
    ### Read in data from file
    #########################################################################  
    data = np.genfromtxt(outfile, delimiter=' ', comments='#').T
    (mjd,image_id,median,mad,lower_quarter,upper_quarter,mean,sem,std) = data
    
    
    ######################################################################### 
    ### Plot
    #########################################################################   
    if len(mjd)>1:
        #::: Mag Zeropoint overview
        fig = plt.figure()
        #:::
        ax1 = fig.add_subplot(111)
        ax1.errorbar(mjd-mjd[0], mean, yerr=sem, color='blue',fmt='o',markersize=8)
        ax1.errorbar(mjd-mjd[0], median, yerr=mad, color='red',fmt='o',markersize=8)
        #ax1.plot(mjd-mjd[0],median_K,'ro',markersize=8)
        ax1.set_xlabel('MJD ' + str(mjd[0]) + '+')
        ax1.set_ylabel('Flux/Flux_0')
	ax1.set_ylim(0.,1.2)
        ax1.grid('on')
        #:::    
        timestamp = str(int(timeit.default_timer()))
        fig.savefig(outdir+'/MagZero_MJD_'+timestamp+'.png', bbox_inches='tight', dpi=100)
        print 'Saved plot.'
    
    
    
if __name__ == '__main__':    
    fct(outdir,outfile)

