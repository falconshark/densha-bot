#!/bin/bash
# Build the database and start the application
alembic upgrade head
python3 main.py
