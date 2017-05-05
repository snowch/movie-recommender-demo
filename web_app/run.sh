#!/bin/bash

set -e

export FLASK_DEBUG=1
export USE_MSGHB=1
export USE_REDIS=0


[[ $USE_REDIS -eq 1 ]] && export VCAP_REDIS=",$(cat etc/redis_vcap.json)"
[[ $USE_MSGHB -eq 1 ]] && export VCAP_MSGHB=",$(cat etc/messagehub_vcap.json)"

export VCAP_SERVICES="{$(cat etc/cloudant_vcap.json) ${VCAP_REDIS} ${VCAP_MSGHB}}"

if [[ $# -eq 0 ]]
then
    python3.6 manage.py runserver -d
fi

python3.6 manage.py "$@"
