#!/bin/bash

docker run \
    -d \
    -v dataproducts_db:/var/lib/postgresql/data \
    -e POSTGRES_USER=dataproducts \
    -e POSTGRES_PASSWORD=password \
    -e POSTGRES_DB=dataproducts \
    -p 5432:5432 \
    --rm \
    --name dataproducts_db \
    postgres
