#!/usr/bin/env sh

set -eu

DB_SOCKET=/private/tmp/mysql.sock
DB_USER=ops
DB_NAME=ngts_ops

clear_database() {
    mysql -u ${DB_USER} -S ${DB_SOCKET} ${DB_NAME} -e 'drop table if exists transmission_sources'
}

initialise_schema() {
    echo Initialising schema
    mysql -u ${DB_USER} -S ${DB_SOCKET} ${DB_NAME} -e 'create table transmission_sources (
    id integer primary key auto_increment,
    image_id bigint not null,
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
    python ./bin/build_catalogue.py data/refimage.fits \
        --db-socket ${DB_SOCKET} \
        --db-user ${DB_USER} \
        --db-name ${DB_NAME} \
        --fits-out /tmp/catalogue.fits \
        --verbose
}

main() {
    clear_database
    initialise_schema
    extract_sources
}

main
