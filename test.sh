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

initialise_schema() {
    echo Initialising schema
    if [[ -z ${DB_SOCKET} ]]; then
        python bin/initialise_database.py \
                --db-host ${DB_HOST} \
                --db-user ${DB_USER} \
                --db-name ${DB_NAME} \
                -v
    else
        python bin/initialise_database.py \
                --db-socket ${DB_SOCKET} \
                --db-user ${DB_USER} \
                --db-name ${DB_NAME} \
                -v
    fi

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
    initialise_schema
    extract_sources
}

main
