#!/bin/bash

export PGPASSWORD=password
pgcli -h localhost -p 5432 -u dataproducts -d dataproducts
