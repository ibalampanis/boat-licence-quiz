#!/bin/bash
# Script to flush and reload questions from the database in the Docker container

# Name of the container running the web service
CONTAINER_NAME=$(docker-compose ps -q web)

if [ -z "$CONTAINER_NAME" ]; then
    echo "Error: Web container is not running. Start it with 'docker-compose up -d'."
    exit 1
fi

echo "Copying reload_questions.py to the container..."
docker cp reload_questions.py $CONTAINER_NAME:/app/

echo "Executing the script in the container..."
docker exec $CONTAINER_NAME python /app/reload_questions.py

echo "Done!"
