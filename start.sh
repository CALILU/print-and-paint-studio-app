#!/bin/bash
# start.sh
python migration.py
gunicorn --bind 0.0.0.0:5000 app:app