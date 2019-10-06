#!/bin/sh
echo Starting LITHOSYS
export PYTHONPATH=:$(dirname $0)/src/
cd $(dirname $0)/src
python3 -W ignore ./lithosys.py en fr
echo Done