# Voice Notes System - Deployment Guide

Comprehensive guide for deploying Voice Notes System in different environments.

## Table of Contents

1. [Deployment Overview](#deployment-overview)
2. [Local Development Deployment](#local-development-deployment)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [System Service Setup](#system-service-setup)
7. [Security Configuration](#security-configuration)
8. [Monitoring and Logging](#monitoring-and-logging)
9. [Backup and Recovery](#backup-and-recovery)
10. [Troubleshooting](#troubleshooting)

## Deployment Overview

### Architecture Options

Voice Notes System can be deployed in several configurations:

1. **Desktop Application**: Local installation with system tray interface
2. **MCP Server**: Background service for Claude Desktop integration
3. **Containerized**: Docker-based deployment for consistency
4. **Cloud Service**: Remote deployment with API access

### Requirements

#### Minimum System Requirements
- **CPU**: 2 cores, 2.0 GHz
- **RAM**: 4 GB
- **Storage**: 2 GB free space
- **OS**: macOS 10.15+, Windows 10+, Ubuntu 18.04+
- **Python**: 3.9 or higher
- **Network**: Internet access for API calls

#### Recommended System Requirements
- **CPU**: 4 cores, 2.5 GHz
- **RAM**: 8 GB
- **Storage**: 10 GB free space (for audio cache and logs)
- **Audio**: Microphone (built-in or external)

## Local Development Deployment

### Quick Setup

```bash
# Clone repository
git clone https://github.com/your-org/voice-notes-system.git
cd voice-notes-system

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.template .env
# Edit .env with your API keys

# Run initial setup
python setup_config.py

# Validate installation
python validate_config.py

# Start application
python -m src.voice_notes_app
```

### Development Configuration

Create `.env` file for development:

```bash
# API Configuration
OPENAI_API_KEY=your_openai_api_key_here

# MCP Configuration
VOICE_NOTES_MCP_MODE=development
VOICE_NOTES_MCP_HOST=localhost
VOICE_NOTES_MCP_PORT=8000

# Development Settings
LOG_LEVEL=DEBUG
VOICE_NOTES_OUTPUT_DIR=./dev_notes
VOICE_NOTES_CONFIG_DIR=./config

# Audio Settings
AUDIO_SAMPLE_RATE=44100
AUDIO_CHANNELS=1

# Development Features
ENABLE_MOCK_SERVICES=false
ENABLE_DEBUG_LOGGING=true
```

### IDE Configuration

#### VS Code Settings

Create `.vscode/settings.json`:

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".pytest_cache": true,
        "venv/": true
    }
}
```

## Production Deployment

### Pre-deployment Checklist

- [ ] All tests passing (`pytest`)
- [ ] Code formatted (`black src/ tests/`)
- [ ] Linting clean (`flake8 src/ tests/`)
- [ ] Type checking clean (`mypy src/`)
- [ ] Security scan completed
- [ ] Configuration validated
- [ ] Backup procedures tested

### Production Environment Setup

```bash
# Create production directory
sudo mkdir -p /opt/voice-notes-system
cd /opt/voice-notes-system

# Create production user
sudo useradd -r -s /bin/false voicenotes
sudo chown voicenotes:voicenotes /opt/voice-notes-system

# Switch to production user context
sudo -u voicenotes bash

# Install application
git clone https://github.com/your-org/voice-notes-system.git .
python3 -m venv venv-prod
source venv-prod/bin/activate
pip install --no-cache-dir -r requirements.txt

# Create production configuration
cp config/config.yaml.template config/config.yaml
# Edit configuration for production settings

# Set up environment variables
cat > .env.prod << 'EOF'
OPENAI_API_KEY=your_production_api_key
VOICE_NOTES_MCP_MODE=production
LOG_LEVEL=INFO
VOICE_NOTES_OUTPUT_DIR=/var/lib/voice-notes/notes
VOICE_NOTES_CONFIG_DIR=/etc/voice-notes
EOF

# Set secure permissions
chmod 600 .env.prod
chmod 755 /opt/voice-notes-system
chmod -R 644 config/
```

### Production Configuration

Create `/etc/voice-notes/config.yaml`:

```yaml
# Production Configuration
environment: production

logging:
  level: INFO
  file: /var/log/voice-notes/app.log
  max_size: 100MB
  backup_count: 5

audio:
  sample_rate: 44100
  channels: 1
  silence_threshold: 0.01
  silence_duration: 2.0
  temp_directory: /tmp/voice-notes-audio

processing:
  default_mode: standard
  timeout: 300
  max_concurrent: 3

file_management:
  output_directory: /var/lib/voice-notes/notes
  backup_directory: /var/lib/voice-notes/backups
  cleanup_temp_files: true
  auto_backup: true

security:
  encrypt_temp_files: true
  secure_delete: true
  api_rate_limiting: true

monitoring:
  metrics_enabled: true
  health_check_port: 8001
  prometheus_metrics: true
```

## Docker Deployment

### Dockerfile

```dockerfile
# Production Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libasound2-dev \
    pulseaudio \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN useradd -r -s /bin/false voicenotes

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY scripts/ ./scripts/

# Create necessary directories
RUN mkdir -p /var/lib/voice-notes/notes \
             /var/log/voice-notes \
             /tmp/voice-notes-audio

# Set ownership
RUN chown -R voicenotes:voicenotes /app /var/lib/voice-notes /var/log/voice-notes /tmp/voice-notes-audio

# Switch to application user
USER voicenotes

# Environment variables
ENV PYTHONPATH=/app
ENV LOG_LEVEL=INFO
ENV VOICE_NOTES_MCP_MODE=server

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python scripts/health_check.py || exit 1

# Expose MCP server port
EXPOSE 8000

# Start application
CMD ["python", "-m", "src.mcp_server"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  voice-notes:
    build: .
    container_name: voice-notes-system
    restart: unless-stopped

    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - VOICE_NOTES_MCP_MODE=server
      - LOG_LEVEL=INFO

    volumes:
      - voice_notes_data:/var/lib/voice-notes
      - voice_notes_logs:/var/log/voice-notes
      - ./config/production.yaml:/app/config/config.yaml:ro

    ports:
      - "8000:8000"  # MCP server
      - "8001:8001"  # Health check

    networks:
      - voice_notes_network

    depends_on:
      - redis

    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '1.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  redis:
    image: redis:7-alpine
    container_name: voice-notes-redis
    restart: unless-stopped
    volumes:
      - redis_data:/data
    networks:
      - voice_notes_network

volumes:
  voice_notes_data:
  voice_notes_logs:
  redis_data:

networks:
  voice_notes_network:
    driver: bridge
```

### Build and Deploy

```bash
# Build Docker image
docker build -t voice-notes-system:latest .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f voice-notes

# Scale service
docker-compose up -d --scale voice-notes=2

# Update deployment
docker-compose pull
docker-compose up -d --force-recreate
```

## Cloud Deployment

### AWS Deployment

#### ECS Deployment

```yaml
# ecs-task-definition.json
{
  "family": "voice-notes-system",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/voiceNotesTaskRole",
  "containerDefinitions": [
    {
      "name": "voice-notes",
      "image": "your-account.dkr.ecr.region.amazonaws.com/voice-notes:latest",
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "VOICE_NOTES_MCP_MODE",
          "value": "server"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ],
      "secrets": [
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:voice-notes/openai-key"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/voice-notes-system",
          "awslogs-region": "us-west-2",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "mountPoints": [
        {
          "sourceVolume": "voice-notes-data",
          "containerPath": "/var/lib/voice-notes"
        }
      ]
    }
  ],
  "volumes": [
    {
      "name": "voice-notes-data",
      "efsVolumeConfiguration": {
        "fileSystemId": "fs-12345678",
        "transitEncryption": "ENABLED"
      }
    }
  ]
}
```

#### Terraform Configuration

```hcl
# main.tf
provider "aws" {
  region = var.aws_region
}

# ECS Cluster
resource "aws_ecs_cluster" "voice_notes" {
  name = "voice-notes-cluster"

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

# Load Balancer
resource "aws_lb" "voice_notes" {
  name               = "voice-notes-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets           = var.public_subnet_ids
}

# ECS Service
resource "aws_ecs_service" "voice_notes" {
  name            = "voice-notes-service"
  cluster         = aws_ecs_cluster.voice_notes.id
  task_definition = aws_ecs_task_definition.voice_notes.arn
  desired_count   = 2
  launch_type     = "FARGATE"

  network_configuration {
    security_groups = [aws_security_group.ecs_tasks.id]
    subnets         = var.private_subnet_ids
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.voice_notes.arn
    container_name   = "voice-notes"
    container_port   = 8000
  }
}
```

### Google Cloud Platform

#### Cloud Run Deployment

```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: voice-notes-system
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 100
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/voice-notes:latest
        ports:
        - containerPort: 8000
        env:
        - name: VOICE_NOTES_MCP_MODE
          value: "server"
        - name: LOG_LEVEL
          value: "INFO"
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: openai-api-key
              key: key
        resources:
          limits:
            cpu: "2"
            memory: "2Gi"
        volumeMounts:
        - name: voice-notes-data
          mountPath: /var/lib/voice-notes
      volumes:
      - name: voice-notes-data
        nfs:
          server: your-filestore-ip
          path: /voice_notes
```

## System Service Setup

### Linux systemd Service

```ini
# /etc/systemd/system/voice-notes.service
[Unit]
Description=Voice Notes System
After=network.target
Wants=network.target

[Service]
Type=simple
User=voicenotes
Group=voicenotes
WorkingDirectory=/opt/voice-notes-system
Environment=PATH=/opt/voice-notes-system/venv-prod/bin
EnvironmentFile=/opt/voice-notes-system/.env.prod
ExecStart=/opt/voice-notes-system/venv-prod/bin/python -m src.voice_notes_app
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=voice-notes

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/voice-notes /var/log/voice-notes /tmp/voice-notes-audio

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Enable service
sudo systemctl enable voice-notes.service

# Start service
sudo systemctl start voice-notes.service

# Check status
sudo systemctl status voice-notes.service

# View logs
sudo journalctl -u voice-notes.service -f
```

### macOS LaunchDaemon

```xml
<!-- /Library/LaunchDaemons/com.voicenotes.app.plist -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.voicenotes.app</string>

    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Voice Notes System/venv/bin/python</string>
        <string>-m</string>
        <string>src.voice_notes_app</string>
    </array>

    <key>WorkingDirectory</key>
    <string>/Applications/Voice Notes System</string>

    <key>RunAtLoad</key>
    <true/>

    <key>KeepAlive</key>
    <dict>
        <key>SuccessfulExit</key>
        <false/>
    </dict>

    <key>StandardOutPath</key>
    <string>/var/log/voice-notes/stdout.log</string>

    <key>StandardErrorPath</key>
    <string>/var/log/voice-notes/stderr.log</string>

    <key>UserName</key>
    <string>voicenotes</string>
</dict>
</plist>
```

Load the service:

```bash
# Load service
sudo launchctl load /Library/LaunchDaemons/com.voicenotes.app.plist

# Start service
sudo launchctl start com.voicenotes.app

# Check status
sudo launchctl list | grep voicenotes
```

### Windows Service

Use NSSM (Non-Sucking Service Manager):

```batch
REM Install NSSM
choco install nssm

REM Create service
nssm install "Voice Notes System" "C:\Voice Notes System\venv\Scripts\python.exe"
nssm set "Voice Notes System" Arguments "-m src.voice_notes_app"
nssm set "Voice Notes System" AppDirectory "C:\Voice Notes System"
nssm set "Voice Notes System" DisplayName "Voice Notes System"
nssm set "Voice Notes System" Description "AI-powered voice note capture and processing"
nssm set "Voice Notes System" Start SERVICE_AUTO_START

REM Start service
nssm start "Voice Notes System"
```

## Security Configuration

### SSL/TLS Configuration

For production deployments with external access:

```yaml
# config/security.yaml
ssl:
  enabled: true
  cert_file: /etc/ssl/certs/voice-notes.crt
  key_file: /etc/ssl/private/voice-notes.key
  protocols: ["TLSv1.2", "TLSv1.3"]
  ciphers: "ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS"

authentication:
  enabled: true
  method: "api_key"  # or "jwt", "oauth"
  api_key_header: "X-API-Key"
  rate_limiting:
    enabled: true
    requests_per_minute: 60

authorization:
  enabled: true
  default_role: "user"
  admin_users: ["admin@example.com"]
```

### Firewall Configuration

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow 8000/tcp  # MCP server
sudo ufw allow 8001/tcp  # Health check
sudo ufw enable

# iptables
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8000 -j ACCEPT
sudo iptables -A INPUT -p tcp --dport 8001 -j ACCEPT
sudo iptables -A INPUT -j DROP
```

### Environment Security

```bash
# Secure environment file
touch .env.prod
chmod 600 .env.prod
chown voicenotes:voicenotes .env.prod

# Secure configuration directory
chmod -R 755 /etc/voice-notes
chmod 644 /etc/voice-notes/*.yaml
chown -R root:voicenotes /etc/voice-notes

# Secure data directory
chmod -R 755 /var/lib/voice-notes
chown -R voicenotes:voicenotes /var/lib/voice-notes

# Secure log directory
chmod -R 755 /var/log/voice-notes
chown -R voicenotes:voicenotes /var/log/voice-notes
```

## Monitoring and Logging

### Logging Configuration

```python
# config/logging.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
        'json': {
            'format': '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}'
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'INFO',
            'formatter': 'detailed',
            'stream': 'ext://sys.stdout'
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'formatter': 'json',
            'filename': '/var/log/voice-notes/app.log',
            'maxBytes': 100000000,  # 100MB
            'backupCount': 5
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'ERROR',
            'formatter': 'detailed',
            'filename': '/var/log/voice-notes/error.log',
            'maxBytes': 50000000,  # 50MB
            'backupCount': 3
        }
    },
    'loggers': {
        'voice_notes': {
            'level': 'DEBUG',
            'handlers': ['console', 'file', 'error_file'],
            'propagate': False
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console']
    }
}
```

### Health Check Endpoint

```python
# scripts/health_check.py
import aiohttp
import asyncio
import sys
import os

async def health_check():
    """Check application health."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8001/health') as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get('status') == 'healthy':
                        print("Health check passed")
                        return 0
                    else:
                        print(f"Health check failed: {data}")
                        return 1
                else:
                    print(f"Health check failed with status: {response.status}")
                    return 1
    except Exception as e:
        print(f"Health check error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(health_check()))
```

### Prometheus Metrics

```python
# src/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
RECORDINGS_TOTAL = Counter('voice_notes_recordings_total',
                          'Total number of recordings')
TRANSCRIPTION_DURATION = Histogram('voice_notes_transcription_duration_seconds',
                                 'Time spent on transcription')
ACTIVE_SESSIONS = Gauge('voice_notes_active_sessions',
                       'Number of active recording sessions')
API_COSTS = Counter('voice_notes_api_costs_total',
                   'Total API costs', ['service'])

def start_metrics_server(port=8002):
    """Start Prometheus metrics server."""
    start_http_server(port)
```

## Backup and Recovery

### Automated Backup Script

```bash
#!/bin/bash
# scripts/backup.sh

BACKUP_DIR="/var/backups/voice-notes"
DATA_DIR="/var/lib/voice-notes"
CONFIG_DIR="/etc/voice-notes"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Backup data
tar -czf "$BACKUP_DIR/voice-notes-data-$DATE.tar.gz" -C "$DATA_DIR" .

# Backup configuration
tar -czf "$BACKUP_DIR/voice-notes-config-$DATE.tar.gz" -C "$CONFIG_DIR" .

# Remove old backups (keep 30 days)
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete

# Log backup completion
echo "$(date): Backup completed - $BACKUP_DIR/voice-notes-*-$DATE.tar.gz" >> /var/log/voice-notes/backup.log
```

### Database Backup (if using database)

```bash
#!/bin/bash
# scripts/db_backup.sh

DB_NAME="voice_notes"
BACKUP_DIR="/var/backups/voice-notes/db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# PostgreSQL backup
pg_dump "$DB_NAME" | gzip > "$BACKUP_DIR/voice-notes-db-$DATE.sql.gz"

# MySQL backup
# mysqldump "$DB_NAME" | gzip > "$BACKUP_DIR/voice-notes-db-$DATE.sql.gz"
```

### Restore Procedures

```bash
#!/bin/bash
# scripts/restore.sh

BACKUP_FILE="$1"
RESTORE_TYPE="$2"  # data, config, or db

if [ -z "$BACKUP_FILE" ] || [ -z "$RESTORE_TYPE" ]; then
    echo "Usage: $0 <backup_file> <restore_type>"
    exit 1
fi

case "$RESTORE_TYPE" in
    "data")
        systemctl stop voice-notes
        tar -xzf "$BACKUP_FILE" -C /var/lib/voice-notes/
        chown -R voicenotes:voicenotes /var/lib/voice-notes/
        systemctl start voice-notes
        ;;
    "config")
        systemctl stop voice-notes
        tar -xzf "$BACKUP_FILE" -C /etc/voice-notes/
        chown -R root:voicenotes /etc/voice-notes/
        systemctl start voice-notes
        ;;
    "db")
        # PostgreSQL restore
        gunzip -c "$BACKUP_FILE" | psql voice_notes
        ;;
    *)
        echo "Invalid restore type. Use: data, config, or db"
        exit 1
        ;;
esac
```

## Troubleshooting

### Common Deployment Issues

#### Permission Errors

```bash
# Fix ownership
sudo chown -R voicenotes:voicenotes /opt/voice-notes-system
sudo chown -R voicenotes:voicenotes /var/lib/voice-notes
sudo chown -R voicenotes:voicenotes /var/log/voice-notes

# Fix permissions
sudo chmod -R 755 /opt/voice-notes-system
sudo chmod 600 /opt/voice-notes-system/.env.prod
```

#### Port Conflicts

```bash
# Check port usage
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# Kill conflicting process
sudo kill -9 <PID>
```

#### Service Won't Start

```bash
# Check service status
sudo systemctl status voice-notes.service

# View detailed logs
sudo journalctl -u voice-notes.service -n 50

# Check configuration
python validate_config.py --config /etc/voice-notes/config.yaml
```

#### Docker Issues

```bash
# Check container logs
docker logs voice-notes-system

# Debug container
docker exec -it voice-notes-system bash

# Check resource usage
docker stats voice-notes-system

# Restart service
docker-compose restart voice-notes
```

### Performance Troubleshooting

#### Memory Issues

```bash
# Monitor memory usage
sudo ps aux | grep voice-notes
sudo systemctl status voice-notes.service

# Check for memory leaks
python -m memory_profiler src/voice_notes_app.py
```

#### CPU Issues

```bash
# Monitor CPU usage
top -p $(pgrep -f voice-notes)
htop

# Profile CPU usage
python -m cProfile -o profile.stats src/voice_notes_app.py
```

### Network Troubleshooting

```bash
# Test API connectivity
curl -v https://api.openai.com/v1/models
python scripts/test_api_connectivity.py

# Check MCP server
curl -v http://localhost:8000/health
nc -zv localhost 8000
```

### Log Analysis

```bash
# Real-time log monitoring
tail -f /var/log/voice-notes/app.log

# Search for errors
grep -i error /var/log/voice-notes/app.log

# Count log levels
awk '{print $3}' /var/log/voice-notes/app.log | sort | uniq -c

# Extract specific timeframe
sed -n '/2024-01-15 10:00/,/2024-01-15 11:00/p' /var/log/voice-notes/app.log
```

---

This deployment guide covers all aspects of deploying Voice Notes System from development to production environments. Choose the deployment method that best fits your infrastructure and requirements.