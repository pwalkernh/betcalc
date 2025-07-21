#!/bin/bash

# =============================================================================
# PostgreSQL Setup Convenience Script
# =============================================================================
# 
# This script allows you to run the PostgreSQL setup from within the postgres/
# directory. It automatically navigates to the project root and runs the
# appropriate setup script.
# 
# USAGE:
#   ./run.sh [setup_type] [OPTIONS]
# 
# SETUP TYPES:
#   start     - Start PostgreSQL using individual Docker container
#   stop      - Stop PostgreSQL container
#   help      - Show this help message
#
# EXAMPLES:
#   ./run.sh start
#   ./run.sh start --port 5433
#   ./run.sh stop --remove
# 
# =============================================================================

# Get the directory where this script is located
POSTGRES_SCRIPTS_FOLDER="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Default values can be overridden by passing arguments to the individual scripts

# Function to show help
show_help() {
    echo "Usage: $0 [setup_type] [OPTIONS]"
    echo ""
    echo "SETUP TYPES:"
    echo "  start     - Start PostgreSQL using individual Docker container"
    echo "  stop      - Stop PostgreSQL container"
    echo "  help      - Show this help message"
    echo ""
    echo "DEFAULT VALUES:"
    echo "  Container name: betcalc-postgres"
    echo "  Port: 5432"
    echo "  Data directory: /opt/postgres/data"
    echo ""
    echo "EXAMPLES:"
    echo "  $0 start"
    echo "  $0 start --port 5433"
    echo "  $0 stop --remove"
}

# Check if setup type is provided
if [[ $# -eq 0 ]]; then
    echo "Error: Setup type is required" >&2
    show_help
    exit 1
fi

SETUP_TYPE="$1"
shift

# Navigate to project root and run the appropriate script
cd "$POSTGRES_SCRIPTS_FOLDER"

case "$SETUP_TYPE" in
    start)
        echo "Starting PostgreSQL container..."
        ./start_postgres.sh "$@"
        ;;
    stop)
        echo "Stopping PostgreSQL container..."
        ./stop_postgres.sh "$@"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "Error: Unknown setup type '$SETUP_TYPE'" >&2
        show_help
        exit 1
        ;;
esac 