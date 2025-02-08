#!/bin/bash

if [ "$DEV_MODE" == "True" ]; then
    exec python3.11 -m uvicorn api:api --reload --port 80 --host 0.0.0.0 --reload-exclude '*.log' --log-level debug --access-log
else
    exec uvicorn api:api --port 80 --host 0.0.0.0 --workers 4
fi
