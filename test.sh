#!/usr/bin/env sh

set -eu

clear_database() {
    mysql -u sw -h ngtsdb ngts_ops -e 'drop table if exists transmission_sources'
}

extract_sources() {
    python ./bin/build_catalogue.py data/refimage.fits
}

main() {
    clear_database
    extract_sources
}
