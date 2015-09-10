#!/usr/bin/env bash


#TODO:
#- change directories and mkdir if needed



abspath() {
    python -c "import os; print os.path.realpath('${1}')"
}



#########################################################################
### User settings
#########################################################################

readonly DATADIR=${1} #where the images lie
readonly REFDIR='/home/maxg/data/' #where the reference file lies
readonly BASEDIR=$(abspath $(dirname $0)) #where this .sh file lies
readonly OUTDIR="${DATADIR}_output" #where the output shall go

readonly REFERENCE=$REFDIR/'catalogue2.fits' #reference file with fluxes and magnitudes
readonly OUTFILE=$OUTDIR/'output.txt' #output file with flux ratios and/or magnitude zero-points
readonly SANITYFILE=$OUTDIR/'sanity.txt' #sanity file that contains info if flux > 2*ref_flux

readonly R_APERT=3. #aperture circle
readonly R_IN=6. #inner background annulus
readonly R_OUT=8. #outer backgroudn annulus



#########################################################################
### Define functions
#########################################################################

initiate() {
    echo "Initiate directories and output files"
    mkdir -p $OUTDIR
    CMD="python ${BASEDIR}/Transparency_initiate.py $OUTDIR $OUTFILE $SANITYFILE"
    echo $CMD
    ${CMD}
}


photometry() {
    echo "Do photometry and calculate flux ratio"
    CMD="python ${BASEDIR}/Transparency_photometry.py $IMAGE $REFERENCE $OUTDIR $OUTFILE $SANITYFILE $R_APERT $R_IN $R_OUT"
    echo $CMD
    ${CMD}
}


plot() {
echo "Create/Update Transparency Plot"
CMD="python ${BASEDIR}/Transparency_live_plot.py $OUTDIR $OUTFILE"
echo $CMD
${CMD}
}



#########################################################################
### MAIN
#########################################################################

main() {
    echo "#########################################################################"
    echo "### Initiating..."
    initiate

    for IMAGE in $DATADIR/IMAGE*.fits; do
        echo "#########################################################################"
        echo "### Working on $IMAGE"
        photometry
        echo "#########################################################################"
    done

    plot
}

main
