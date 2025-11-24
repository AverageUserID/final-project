#!/bin/bash
docker build -t final-project .
docker run --env-file .env -p 8000:8000 final-project
