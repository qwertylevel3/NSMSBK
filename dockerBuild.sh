#!/bin/bash -e

docker build -t name_server_mngr_site:debug .
docker run --name name_server_mngr_site -p 80:80 name_server_mngr_site:debug

