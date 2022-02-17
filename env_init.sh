#!/bin/bash

# Script must be called as `source ./env_init.sh` in order to bring user shell into venv.

python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt
pip install --editable .
pre-commit install-hooks
