# ModSecurity & CRS with Nginx and REST API

This project provides a REST API that integrates **ModSecurity** with **Nginx** to inspect and block malicious HTTP requests. A **Flask** application serves as a proxy to forward requests and logs results based on **ModSecurity**'s findings.

## Project Overview

The project involves:
1. **Dockerized Environment**: The application runs within a Docker container that installs ModSecurity, Nginx, and other dependencies.
2. **ModSecurity**: Provides Web Application Firewall (WAF) functionalities and uses the Core Rule Set (CRS) to inspect incoming traffic.
3. **Flask API**: A Python-based proxy service that forwards HTTP requests to another service and checks if ModSecurity flags the requests as malicious.
4. **Logging**: Responses and logs are stored in `/var/log/modsecurity/audit.log`. Any issues flagged by ModSecurity are included in the response.

## Architecture

1. **API (Flask)**: Listens on port `5000`, forwarding requests to a server on port `8080` after modifying headers (using the `X-Request-Random` tag).
2. **Nginx with ModSecurity**: Processes traffic for potential security risks on port `80`, passing requests between the API and ModSecurity.
3. **ModSecurity Logs**: Tracks potential issues in `/var/log/modsecurity/audit.log`. If an issue occurs, the logs are included in the response.

## Installation

### Prerequisites
Make sure the following are installed:
- **Docker**: To build and run the project container.

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/modsecurity-nginx-flask.git
   cd modsecurity-nginx-flask
   ```

2. Build the Docker image:
   ```bash
   docker build -t modsecurity-nginx .
   ```

3. Run the container:
   ```bash
   docker run --name mod-sec -p 8010:80 modsecurity-nginx
   ```

   The API will be accessible at `http://localhost:8010`.

### File Structure

- `api.py`: Flask application that handles incoming POST requests, forwards them, and processes ModSecurity logs.
- `server.py`: Placeholder server handling forwarded requests and responding to the API.
- `Dockerfile`: Builds the Docker container, installing Nginx, ModSecurity, Flask, and other dependencies.
- `nginx.conf`: Configures Nginx to work with ModSecurity.
- `modsecurity.conf`: Configures the ModSecurity engine.

## Usage

1. Send a `POST` request to the API running at `http://localhost:8010`:
   ```bash
   curl -X POST http://localhost:8010 -H "Content-Type: application/json" -d '{"url":"/test", "method":"POST", "requestHeaders":{}, "requestBody":{}, "responseHeaders":{}, "responseBody":{}}'
   ```

2. The API will forward the request to the internal server on port `8080`.

3. If ModSecurity detects any issues with the request or response, the logs will be extracted from `/var/log/modsecurity/audit.log` and returned in the response.

## Example Request Flow

1. The client sends a `POST` request to the Flask API.
2. The API forwards the request to an internal server (`server.py`), adding the header `X-Request-Random` with a unique ID for tracking.
3. ModSecurity inspects the request when it passes through Nginx.
4. If ModSecurity flags the request or response, the Flask API checks the audit logs, extracts relevant logs, and returns them to the client.

## Logs
ModSecurity logs can be found at:
```bash
/var/log/modsecurity/audit.log
```

These logs include detailed information about any blocked requests.
