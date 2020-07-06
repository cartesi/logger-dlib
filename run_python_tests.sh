#!/bin/bash
SCRIPTPATH="$( pwd -P )"
export PYTHONPATH=${SCRIPTPATH}

cd ./test
python3 test_logger.py
