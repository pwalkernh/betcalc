#!/bin/bash

# =============================================================================
# PostgreSQL Docker Container Startup Script
# =============================================================================
# 
# This script starts a PostgreSQL database using Docker with configurable
# volume mounting and password prompting. For more details about the Postgres Docker
# image, see https://hub.docker.com/_/postgres.
# 
# USAGE:
#   ./start_postgres.sh [OPTIONS]
# 
# OPTIONAL ARGUMENTS:
#   --postgres-root <path>    Custom volume mount point (default: /opt/postgres/data)
#   --container-name <name>   Custom container name (default: betcalc-postgres)
#   --port <port>            Custom port mapping (default: 5432)
#   --postgres-user <user>   Custom PostgreSQL user (default: postgres)
#   --postgres-db <db>       Custom PostgreSQL database (default: betcalc)
#   --network <network>      Custom Docker network (default: none)
#   --help, -h               Show this help message
#
# EXAMPLES:
#   ./start_postgres.sh
#   ./start_postgres.sh --postgres-root /custom/path
#   ./start_postgres.sh --container-name my-postgres --port 5433
#   ./start_postgres.sh --postgres-user myuser --postgres-db mydb
#   ./start_postgres.sh --network my-network
# 
# EXIT CODES:
#   0 - Success
#   1 - Invalid arguments or missing required parameters
#   2 - Docker command failed
#   3 - Container already exists
# 
# =============================================================================

# Initialize variables with defaults
POSTGRES_ROOT="/opt/postgres/data"
POSTGRES_USER="postgres"
POSTGRES_DB="betcalc"
CONTAINER_NAME="betcalc-postgres"
PORT="5432"
NETWORK="betcalc-network"

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONAL ARGUMENTS:"
    echo "  --postgres-root <path>    Custom volume mount point (default: ${POSTGRES_ROOT})"
    echo "  --container-name <name>   Custom container name (default: ${CONTAINER_NAME})"
    echo "  --port <port>            Custom port mapping (default: ${PORT})"
    echo "  --postgres-user <user>   Custom PostgreSQL user (default: ${POSTGRES_USER})"
    echo "  --postgres-db <db>       Custom PostgreSQL database (default: ${POSTGRES_DB})"
    echo "  --network <network>      Custom Docker network (default: ${NETWORK})"
    echo "  --help, -h               Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0"
    echo "  $0 --postgres-root /custom/path"
    echo "  $0 --container-name my-postgres --port 5433"
    echo "  $0 --postgres-user myuser --postgres-db mydb"
    echo "  $0 --network my-network"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --postgres-root)
            POSTGRES_ROOT="$2"
            shift 2
            ;;
        --container-name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --port)
            PORT="$2"
            shift 2
            ;;
        --postgres-user)
            POSTGRES_USER="$2"
            shift 2
            ;;
        --postgres-db)
            POSTGRES_DB="$2"
            shift 2
            ;;
        --network)
            NETWORK="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Error: Unknown argument $1" >&2
            show_help
            exit 1
            ;;
    esac
done

# Validate port parameter
if [[ ! "$PORT" =~ ^[0-9]+$ ]] || [[ "$PORT" -lt 1 ]] || [[ "$PORT" -gt 65535 ]]; then
    echo "Error: --port must be a number between 1 and 65535" >&2
    exit 1
fi

# Check if container already exists
if docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: Container '$CONTAINER_NAME' already exists" >&2
    echo "To remove the existing container, run: docker rm -f $CONTAINER_NAME" >&2
    exit 3
fi

# Check if network exists and create it if it doesn't
if [[ -n "$NETWORK" ]]; then
    if ! docker network ls --format "{{.Name}}" | grep -q "^${NETWORK}$"; then
        echo "Creating Docker network: $NETWORK"
        docker network create --attachable --scope=local --label="betcalc-network" "$NETWORK"
        if [[ $? -ne 0 ]]; then
            echo "Error: Failed to create Docker network '$NETWORK'" >&2
            exit 1
        fi
    else
        echo "Using existing Docker network: $NETWORK"
    fi
fi

# Create the data directory if it doesn't exist
if [[ ! -d "$POSTGRES_ROOT" ]]; then
    echo "Creating data directory: $POSTGRES_ROOT"
    mkdir -p "$POSTGRES_ROOT"
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to create data directory $POSTGRES_ROOT" >&2
        exit 1
    fi
fi

# Prompt for password with hidden input
echo -n "Enter PostgreSQL password: "
read -s POSTGRES_PASSWORD
echo ""

# Prompt for password confirmation and check match
echo -n "Confirm PostgreSQL password: "
read -s POSTGRES_PASSWORD_CONFIRM
echo ""

if [[ "$POSTGRES_PASSWORD" != "$POSTGRES_PASSWORD_CONFIRM" ]]; then
    echo "Error: Passwords do not match" >&2
    exit 1
fi

# Validate password is not empty
if [[ -z "$POSTGRES_PASSWORD" ]]; then
    echo "Error: Password cannot be empty" >&2
    exit 1
fi

echo "Starting PostgreSQL container..."
echo "Container name: $CONTAINER_NAME"
echo "Port mapping: $PORT:5432"
echo "Data directory: $POSTGRES_ROOT"

# Start the PostgreSQL container
docker run -d \
    --name "$CONTAINER_NAME" \
    ${NETWORK:+--network "$NETWORK"} \
    -e POSTGRES_PASSWORD="$POSTGRES_PASSWORD" \
    -e POSTGRES_USER="$POSTGRES_USER" \
    -e POSTGRES_DB="$POSTGRES_DB" \
    -e PGDATA=/var/lib/postgresql/data/pgdata \
    -v "$POSTGRES_ROOT:/var/lib/postgresql/data" \
    -p "$PORT:5432" \
    postgres

# Check if the container started successfully
if [[ $? -eq 0 ]]; then
    echo ""
    echo "PostgreSQL container started successfully!"
    echo ""
    echo "Connection details:"
    echo "  Host: localhost"
    echo "  Port: $PORT"
    echo "  Database: $POSTGRES_DB"
    echo "  Username: $POSTGRES_USER"
    echo "  Password: [hidden]"
    echo ""
    echo "To connect using psql:"
    echo "  psql -h localhost -p $PORT -U $POSTGRES_USER -d $POSTGRES_DB"
    echo ""
    echo "To stop the container:"
    echo "  docker stop $CONTAINER_NAME"
    echo ""
    echo "To remove the container:"
    echo "  docker rm -f $CONTAINER_NAME"
else
    echo "Error: Failed to start PostgreSQL container" >&2
    exit 2
fi 