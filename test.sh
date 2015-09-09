#!/usr/bin/env sh

set -eu

clear_database() {
    mysql -u sw -h localhost ngts_ops -e 'drop table if exists transmission_sources'
}

initialise_schema() {
    echo Initialising schema
    mysql -u sw -h localhost ngts_ops -e 'create table transmission_sources (
    image_id bigint primary key,
    x_coordinate float not null,
    y_coordinate float not null,
    inc_prescan tinyint default 1,
    flux_adu float not null,
    foreign key (image_id)
        references autoguider_refimage(ref_image_id)
        on delete restrict
    )
    '
}

extract_sources() {
    python ./bin/build_catalogue.py data/refimage.fits
}

main() {
    clear_database
    initialise_schema
    extract_sources
}

main
