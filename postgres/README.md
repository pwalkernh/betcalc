# PostgreSQL Database Setup

This directory contains scripts to set up and manage a PostgreSQL database using Docker for the betcalc-flask application.

## Setup Options

### Option 1: Convenience Script (Easiest)

If you're working from within the `app/postgres/` directory, you can use the convenience script:

```bash
# From within postgres/ directory
./run.sh start
./run.sh stop --remove
```

### Option 2: Individual Docker Scripts (Direct control)

Use the individual scripts for direct Docker container management:

#### `start_postgres.sh`
Starts a PostgreSQL container with configurable options.

```bash
# Basic usage
./app/postgres/start_postgres.sh

# With custom options
./app/postgres/start_postgres.sh --postgres-root /custom/path --port 5433 --container-name my-postgres --postgres-user myuser --postgres-db mydb
```

**Options:**
- `--postgres-root <path>`: Custom volume mount point (default: `/opt/postgres/data`)
- `--container-name <name>`: Custom container name (default: `betcalc-postgres`)
- `--port <port>`: Custom port mapping (default: `5432`)
- `--postgres-user <user>`: Custom PostgreSQL user (default: `postgres`)
- `--postgres-db <db>`: Custom PostgreSQL database (default: `betcalc`)

#### `stop_postgres.sh`
Stops and optionally removes the PostgreSQL container.

```bash
# Stop container
./app/postgres/stop_postgres.sh

# Stop and remove container
./app/postgres/stop_postgres.sh --remove

# With custom container name
./app/postgres/stop_postgres.sh --container-name my-postgres --remove
```

**Options:**
- `--container-name <name>`: Custom container name (default: `betcalc-postgres`)
- `--remove`: Remove the container after stopping

## Connection Details

### Default Connection Information
- **Host**: `localhost`
- **Port**: `5432`
- **Database**: `betcalc`
- **Username**: `postgres`
- **Password**: Set during script execution

### Connecting with psql
```bash
psql -h localhost -p 5432 -U postgres -d betcalc
```

## Data Persistence

Data is persisted in the volume mount point (default: `/opt/postgres/data`). This directory is created automatically if it doesn't exist.

## Security Notes

1. **Password Handling**: Scripts prompt for passwords with hidden input (no echo)
2. **Container Isolation**: Uses isolated containers with proper networking

## Troubleshooting

### Container Already Exists
```bash
# Remove existing container
docker rm -f betcalc-postgres

# Then run the start script again
./app/postgres/start_postgres.sh
```

### Port Already in Use
```bash
# Use a different port
./app/postgres/start_postgres.sh --port 5433
```

### Permission Issues
```bash
# Make scripts executable
chmod +x *.sh
```



## Integration with Flask App

To integrate with your Flask application, you'll need to:

1. Install PostgreSQL Python driver:
   ```bash
   pip install psycopg2-binary
   ```

2. Set up database connection in your Flask app:
   ```python
   import os
   from flask_sqlalchemy import SQLAlchemy
   
   app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
       'DATABASE_URL', 
       'postgresql://postgres:password@localhost:5432/betcalc'
   )
   ```

## File Organization

```
app/postgres/
├── start_postgres.sh              # Individual Docker container startup
├── stop_postgres.sh               # Individual Docker container management
├── run.sh                         # Convenience script for running from postgres/ directory
└── README.md                      # This documentation
```

## Recommendations

- **Development**: Use the convenience script for quick setup and teardown
- **Data Safety**: Always backup your data directory before major changes
- **Security**: Use strong passwords and consider using Docker secrets for production 