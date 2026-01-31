#!/bin/bash
cd /home/dy/CampusFlow
source .venv/bin/activate
export PYTHONPATH=/home/dy/CampusFlow:$PYTHONPATH
python app.py
