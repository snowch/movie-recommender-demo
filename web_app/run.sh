#!/bin/bash

set -e

export FLASK_DEBUG=1
export USE_MSGHB=1
export USE_REDIS=0
export USE_BIGIN=1


[[ $USE_REDIS -eq 1 ]] && export VCAP_REDIS=",$(cat etc/redis_vcap.json)"
[[ $USE_MSGHB -eq 1 ]] && export VCAP_MSGHB=",$(cat etc/messagehub_vcap.json)"

# Usage: get_property FILE KEY
function get_property { 
    grep "^$2:" "$1" | cut -d':' -f2; 
}

if [[ $USE_BIGIN -eq 1 && -f ../hdp_app/etc/bi_connection.properties ]]
then
    export BI_HIVE_HOSTNAME="$(get_property ../hdp_app/etc/bi_connection.properties hostname)"
    export BI_HIVE_USERNAME="$(get_property ../hdp_app/etc/bi_connection.properties username)"
    export BI_HIVE_PASSWORD="$(get_property ../hdp_app/etc/bi_connection.properties password)"
fi 

export VCAP_SERVICES="{$(cat etc/cloudant_vcap.json) ${VCAP_REDIS} ${VCAP_MSGHB}}"

if [[ $# -eq 0 ]]
then
    python3.6 manage.py runserver -d
fi

python3.6 manage.py "$@"
