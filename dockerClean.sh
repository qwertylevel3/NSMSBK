#!/bin/bash -e

docker stop name_server_mngr_site
docker container prune
docker image rm name_server_mngr_site:debug

