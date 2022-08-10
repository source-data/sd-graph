#!/bin/bash
# Create a systemd service that autostarts & manages a docker-compose instance in the current directory
# by Uli Köhler - https://techoverflow.net
# Licensed as CC0 1.0 Universal

# exit when any command fails
set -e

if [[ -z "$IMAGE_TAG" ]]; then
    echo "Error: must provide IMAGE_TAG variable in environment" 1>&2
    exit 1
fi

PWD="$(pwd)"
SERVICENAME="$(basename "${PWD}")"
PATH="/usr/local/bin:$PATH"
DOCKER_COMPOSE="$(which docker-compose)"
SD_GRAPH_CMD="${DOCKER_COMPOSE} -f production.yml"

SERVICE_FILE=$(cat <<EOF
[Unit]
Description=$SERVICENAME
Requires=docker.service
After=docker.service
[Service]
Restart=always
User=ec2-user
Group=docker
WorkingDirectory=${PWD}
Environment="IMAGE_TAG=${IMAGE_TAG}"
# Shutdown container (if running) when unit is started
ExecStartPre=${SD_GRAPH_CMD} down
# Start container when unit is started
ExecStart=${SD_GRAPH_CMD} up
# Stop container when unit is stopped
ExecStop=${SD_GRAPH_CMD} down
[Install]
WantedBy=multi-user.target
EOF
)

SERVICE_FILE_NAME="/etc/systemd/system/${SERVICENAME}.service"

echo "Creating systemd service... $SERVICE_FILE_NAME"
echo "${SERVICE_FILE}" > "${SERVICE_FILE_NAME}"

echo "Enabling & starting $SERVICENAME"
systemctl enable $SERVICENAME.service
systemctl start $SERVICENAME.service
