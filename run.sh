#!/bin/bash
# Run script for Open Kitchen application

export FLASK_APP=app
export FLASK_ENV=development
export FLASK_RUN_PORT=8080
export FLASK_RUN_HOST=0.0.0.0

echo "Starting Open Kitchen application..."
echo "Visit http://127.0.0.1:8080 in your browser"
echo "Press Ctrl+C to stop the server"
echo ""

flask run
