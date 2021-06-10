#!/usr/bin/env bash
docker context use $1
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
docker context use default
