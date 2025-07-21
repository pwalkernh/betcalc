#!/bin/bash

# =============================================================================
# PostgreSQL Docker Container Management Script
# =============================================================================
# 
# This script stops and optionally removes a PostgreSQL database container.
# 
# USAGE:
#   ./stop_postgres.sh [OPTIONS]
# 
# OPTIONAL ARGUMENTS:
#   --container-name <name>   Custom container name (default: betcalc-postgres)
#   --remove                  Remove the container after stopping
#   --help, -h               Show this help message
# 
# EXAMPLES:
#   ./stop_postgres.sh
#   ./stop_postgres.sh --remove
#   ./stop_postgres.sh --container-name my-postgres --remove
# 
# EXIT CODES:
#   0 - Success
#   1 - Invalid arguments
#   2 - Container not found
#   3 - Docker command failed
# 
# =============================================================================

# Initialize variables with defaults
CONTAINER_NAME="betcalc-postgres"
REMOVE_CONTAINER=false

# Function to show help
show_help() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "OPTIONAL ARGUMENTS:"
    echo "  --container-name <name>   Custom container name (default: ${CONTAINER_NAME})"
    echo "  --remove                  Remove the container after stopping"
    echo "  --help, -h               Show this help message"
    echo ""
    echo "EXAMPLES:"
    echo "  $0"
    echo "  $0 --remove"
    echo "  $0 --container-name my-postgres --remove"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --container-name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --remove)
            REMOVE_CONTAINER=true
            shift
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

# Check if container exists
if ! docker ps -a --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "Error: Container '$CONTAINER_NAME' not found" >&2
    exit 2
fi

# Check if container is running
if docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping container '$CONTAINER_NAME'..."
    docker stop "$CONTAINER_NAME"
    
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to stop container '$CONTAINER_NAME'" >&2
        exit 3
    fi
    
    echo "Container '$CONTAINER_NAME' stopped successfully."
else
    echo "Container '$CONTAINER_NAME' is not running."
fi

# Remove container if requested
if [[ "$REMOVE_CONTAINER" == true ]]; then
    echo "Removing container '$CONTAINER_NAME'..."
    docker rm "$CONTAINER_NAME"
    
    if [[ $? -ne 0 ]]; then
        echo "Error: Failed to remove container '$CONTAINER_NAME'" >&2
        exit 3
    fi
    
    echo "Container '$CONTAINER_NAME' removed successfully."
    echo ""
    echo "Note: Data volume remains intact. To completely remove data, manually delete the volume mount directory."
else
    echo ""
    echo "Container '$CONTAINER_NAME' stopped but not removed."
    echo "To remove the container, run: $0 --remove"
    echo "To start the container again, run: ./start_postgres.sh"
fi 