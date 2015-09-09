#!/usr/bin/env sh

set -eu

HOSTNAME="$(hostname -s)"
if [[ "${HOSTNAME}" == "mbp15" ]]; then
    DB_SOCKET=/private/tmp/mysql.sock
    DB_HOST=""
    DB_USER=ops
    DB_NAME=ngts_ops
elif [[ "${HOSTNAME}" == "ngtshead" ]]; then
    DB_SOCKET=""
    DB_HOST=ngtsdb
    DB_USER=sw
    DB_NAME=swdb
fi

run_mysql_command() {
    if [[ -z ${DB_SOCKET} ]]; then
        mysql -u ${DB_USER} -h ${DB_HOST} ${DB_NAME} -e "$@"
    else
        mysql -u ${DB_USER} -S ${DB_SOCKET} ${DB_NAME} -e "$@"
    fi
}

clear_database() {
    run_mysql_command 'drop table if exists transmission_sources'
}

initialise_schema() {
    echo Initialising schema
    run_mysql_command 'create table transmission_sources (
    id integer primary key auto_increment,
    image_id bigint not null,
    x_coordinate float not null,
    y_coordinate float not null,
    inc_prescan tinyint default 1,
    flux_adu float not null
    )
    '

    # Remove foreign key constraint for now
    # foreign key (image_id)
    #     references autoguider_refimage(ref_image_id)
    #     on delete restrict
}

extract_sources() {
    if [[ -z ${DB_SOCKET} ]]; then
        python ./bin/build_catalogue.py data/refimage.fits \
            --db-host ${DB_HOST} \
            --db-user ${DB_USER} \
            --db-name ${DB_NAME} \
            --fits-out /tmp/catalogue.fits \
            --verbose
    else
        python ./bin/build_catalogue.py data/refimage.fits \
            --db-socket ${DB_SOCKET} \
            --db-user ${DB_USER} \
            --db-name ${DB_NAME} \
            --fits-out /tmp/catalogue.fits \
            --verbose
    fi
}

main() {
    clear_database
    initialise_schema
    extract_sources
}

main
