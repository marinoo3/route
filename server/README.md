# Route Server

FastAPI server that receives and processes data from an ESP32 sensor. It provides endpoints for creating route sessions and handling IMU (Inertial Measurement Unit) sensor data.

## Quick Start

```bash
# Activate virtual environment
source server-env/bin/activate

# Run the development server
uvicorn app.main:app --reload

# Or specify host and port
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The server will start at `http://localhost:8000`. Interactive API docs are available at `/docs`.

## Setup

Create a `.env` file with the following variables:

```
db_url=<database_url>
db_username=<username>
db_password=<password>
```

## Project Structure

- `app/main.py` - FastAPI application setup
- `app/routers/api.py` - Sensor data and session endpoints
- `app/routers/route.py` - Route management endpoints
- `app/services/` - Database and business logic services
- `app/models/` - Data models and exceptions

## Features

- **Session Management**: Create and manage route sessions
- **IMU Data Processing**: Receive and store sensor data from ESP32 devices
- **Database Integration**: Persistent storage of route and sensor data
