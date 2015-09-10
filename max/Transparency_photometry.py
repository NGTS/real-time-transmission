# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 16:45:12 2015

@author: mx
"""

import numpy as np
import photutils as ph
import astropy.io.fits as pf
import matplotlib.pyplot as plt
import matplotlib
import sys

######################################################################### 
### Settings
#########################################################################

fname = str(sys.argv[1])
ref_fname = str(sys.argv[2])
outdir = str(sys.argv[3])
outfile = str(sys.argv[4])
sanityfile = str(sys.argv[5])
R_apert = float(str(sys.argv[6]))
R_in = float(str(sys.argv[7]))
R_out = float(str(sys.argv[8]))


######################################################################### 
### Read Image
#########################################################################
def read_image(fname):
    with pf.open(fname) as hdulist:
        data, mjd, image_id = hdulist[0].data, hdulist[0].header[
            'mjd'
        ], hdulist[0].header['image_id']
    return data, mjd, image_id


######################################################################### 
### Read Reference
#########################################################################
def read_reference(ref_fname):
    with pf.open(fname) as hdulist:
        x, y, ref_flux = hdulist[1].data['x_coordinate'], hdulist[1].data[
            'y_coordinate'
        ], hdulist[1].data['flux_adu']
    return x, y, ref_flux


    ######################################################################### 
    ### (Optional) Show Image
    #########################################################################
def show_image(data, x, y, R_apert):
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cmap = matplotlib.cm.get_cmap('Greys')
    ax.imshow(np.log(data), cmap=cmap)
    ax.set_xlim()
    for i in range(len(x)):
        circle = plt.Circle((x[i], y[i]), R_apert, color='g')
        circle = plt.Circle((x[i], y[i]), R_apert * 10., facecolor='none')
        ax.add_artist(circle)
    ax.set_xlim(0, 600)
    ax.set_ylim(300, 700)


    ######################################################################### 
    ### Do Photometry with local background subtraction
    #########################################################################
def photometry_local(data, x, y, R_apert, R_in, R_out):
    apertures = ph.CircularAperture((x, y), r=R_apert)
    annulus_apertures = ph.CircularAnnulus((x, y), r_in=R_in, r_out=R_out)
    rawflux_table = ph.aperture_photometry(data, apertures)
    bkgflux_table = ph.aperture_photometry(data, annulus_apertures)
    bkg_mean = bkgflux_table['aperture_sum'] / annulus_apertures.area()
    bkg_sum = bkg_mean * apertures.area()
    final_sum = rawflux_table['aperture_sum'] - bkg_sum
    return np.array(final_sum)


    ######################################################################### 
    ### Calculate FLux Ratio
    #########################################################################
def calc_flux_ratio(flux, ref_flux):
    return 1. * flux / ref_flux


    #median absolute deviation
def mad(arr):
    return np.median(np.abs(arr - np.median(arr)))


######################################################################### 
### Write output files
#########################################################################
def do_statistics(flux_ratio):
    return np.median(flux_ratio), mad(flux_ratio), np.percentile(
        flux_ratio, .25), np.percentile(
            flux_ratio,
            .75), np.mean(flux_ratio), 1. * np.std(flux_ratio) / np.sqrt(
                len(flux_ratio)), np.std(flux_ratio)


######################################################################### 
### Write output files
#########################################################################
def write_file(outfile, mjd, image_id, median, mad, lower_quart, upper_quart,
               mean, std, sem):
    with open(outfile, "a") as myfile:
        line = str(mjd) + ' ' + str(image_id) + ' ' + str(median) + ' ' + str(
            mad) + ' ' + str(lower_quart) + ' ' + str(upper_quart) + ' ' + str(
                mean) + ' ' + str(std) + ' ' + str(sem) + '\n'
        myfile.write(line)


        ######################################################################### 
        ### SANITY CHECKS (TO MARK OUTLIES E.G. AFTER VOLTAGE CHANGES)
        #########################################################################
def sanity_check(sanityfile, image_id, x, y, flux, ref_flux, flux_ratio):
    ind = np.where(flux_ratio > 2.)[0]
    with open(sanityfile, "a") as myfile:
        myfile.write(
            '#########################################################################\n')
        myfile.write(
            str(image_id) + '    ' + str(x[ind]) + '    ' + str(y[ind]) +
            '    ' + str(flux[ind]) + '    ' + str(ref_flux[ind]) + '\n')

    ######################################################################### 
    ### MAIN
    #########################################################################


if __name__ == '__main__':
    data, mjd, image_id = read_image(fname)
    x, y, ref_flux = read_reference(ref_fname)
    flux = photometry_local(data, x, y, R_apert, R_in, R_out)
    flux_ratio = calc_flux_ratio(flux, ref_flux)
    median, mad, lower_quarter, upper_quarter, mean, sem, std = do_statistics(
        flux_ratio)
    write_file(outfile, mjd, image_id, median, mad, lower_quarter,
               upper_quarter, mean, sem, std)
    sanity_check(sanityfile, image_id, x, y, flux, ref_flux, flux_ratio)
