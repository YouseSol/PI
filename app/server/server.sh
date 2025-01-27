#!/bin/bash

PORT=36651

cd /app/build/web/

echo "Starting the server on port $PORT..."
# python3 -m http.server $PORT
python3 ../../server/cors_server.py $PORT
