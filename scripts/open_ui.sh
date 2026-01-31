#!/bin/bash

# Open Airflow UI
if which xdg-open > /dev/null; then
    xdg-open http://localhost:8080
    xdg-open http://localhost:8000/docs
elif which open > /dev/null; then
    open http://localhost:8080
    open http://localhost:8000/docs
else
    echo "Could not detect a browser opener. Please open manually:"
    echo "Airflow UI: http://localhost:8080"
    echo "API Docs: http://localhost:8000/docs"
fi
