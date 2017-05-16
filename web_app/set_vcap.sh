#!/bin/bash

export VCAP_SERVICES="{$(cat etc/cloudant_vcap.json),$(cat etc/redis_vcap.json)}"
