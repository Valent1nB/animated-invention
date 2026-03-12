# Project X - Backend

FastAPI backend application following Clean Architecture principles.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Variables](#environment-variables)
- [Local Development Setup](#local-development-setup)
- [Google OAuth Setup](#google-oauth-setup)
- [AWS Setup](#aws-setup)
  - [Creating AWS Account](#creating-aws-account)
  - [Creating S3 Bucket](#creating-s3-bucket)
  - [Creating EC2 Instance](#creating-ec2-instance)
- [Deployment](#deployment)
  - [Deploying to EC2](#deploying-to-ec2)
- [Database Migrations](#database-migrations)
- [Testing](#testing)
- [Project Structure](#project-structure)

## Prerequisites

- Python 3.12+
- Docker and Docker Compose
- [uv](https://github.com/astral-sh/uv) package manager
- PostgreSQL 17.4+ (or use Docker)
- AWS Account (for production deployment)
- Google Cloud Platform Account (for OAuth)

## Environment Variables

Create a `.env` file in the project root directory with the following variables:

```env
# Environment
ENV=local  # Options: test, local, dev, prod

# Database Configuration
PGHOST=postgres
PGPORT=5432
PGPASSWORD=your_postgres_password
POSTGRES_DB=px
POSTGRES_USER=postgres

# Authentication
AUTH_SIGNATURE_SECRET=your_secret_key_for_jwt_signing
JWT_ACCESS_LIFETIME=3600  # Access token lifetime in seconds
JWT_REFRESH_LIFETIME=604800  # Refresh token lifetime in seconds

# Google OAuth Configuration
GOOGLE_OAUTH_CLIENT_ID=your_google_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_google_client_secret
FRONTEND_REDIRECT_URI=http://localhost:3000/example
GOOGLE_REDIRECT_URI=http://localhost:8000/example
STATE_TOKEN_AUDIENCE=fastapi-users:oauth-state

# AWS S3 Configuration
AWS_DEFAULT_REGION=eu-central-1
AWS_S3_MEDIA_BUCKET=your-s3-bucket-name
AWS_S3_MEDIA_ROOT_FOLDER=media

# AWS Credentials (optional - can also use IAM roles or ~/.aws/credentials)
# If not using IAM roles, uncomment and set these:
# AWS_ACCESS_KEY_ID=your_access_key_id
# AWS_SECRET_ACCESS_KEY=your_secret_access_key

# Media Upload Configuration (optional, defaults shown)
SUPPORTED_MEDIA_FORMATS=jpg,jpeg,png,gif,webp,pdf,doc,docx
MAX_UPLOAD_MEDIA_FILE_SIZE=10485760  # 10MB in bytes
```

### Environment Variable Descriptions

- **ENV**: Application environment (`test`, `local`, `dev`, `prod`)
- **PGHOST**: PostgreSQL hostname (use `postgres` for Docker, `localhost` for local)
- **PGPORT**: PostgreSQL port (default: 5432)
- **PGPASSWORD**: PostgreSQL password
- **POSTGRES_DB**: Database name
- **POSTGRES_USER**: PostgreSQL username
- **AUTH_SIGNATURE_SECRET**: Secret key for JWT token signing (generate a strong random string)
- **JWT_ACCESS_LIFETIME**: Access token expiration time in seconds
- **JWT_REFRESH_LIFETIME**: Refresh token expiration time in seconds
- **GOOGLE_OAUTH_CLIENT_ID**: Google OAuth 2.0 Client ID
- **GOOGLE_OAUTH_CLIENT_SECRET**: Google OAuth 2.0 Client Secret
- **FRONTEND_REDIRECT_URI**: Frontend redirect URI after OAuth callback
- **GOOGLE_REDIRECT_URI**: Backend redirect URI for OAuth callback
- **AWS_DEFAULT_REGION**: AWS region for S3 bucket
- **AWS_S3_MEDIA_BUCKET**: S3 bucket name for media storage
- **AWS_S3_MEDIA_ROOT_FOLDER**: Root folder in S3 bucket for media files
- **AWS_ACCESS_KEY_ID**: AWS access key ID (optional, can use IAM roles or ~/.aws/credentials)
- **AWS_SECRET_ACCESS_KEY**: AWS secret access key (optional, can use IAM roles or ~/.aws/credentials)

**Note**: AWS credentials can be provided via:
1. Environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`)
2. AWS credentials file (`~/.aws/credentials`)
3. IAM role (when running on EC2)

## Local Development Setup

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd project-x
   ```

2. **Create `.env` file**:
   ```bash
   cp .env.example .env  # If you have an example file
   # Or create manually with the variables listed above
   ```

3. **Start services with Docker Compose**:
   ```bash
   make up
   # Or manually:
   docker compose up postgres backend
   ```

4. **Run database migrations**:
   ```bash
   make migrate
   # Or manually:
   docker compose exec backend alembic upgrade head
   ```

5. **Access the API**:
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Health Check: http://localhost:8000/api/v1/health

### Alternative: Local Development Without Docker

1. **Install dependencies**:
   ```bash
   uv sync
   ```

2. **Set up PostgreSQL** locally or use a remote instance

3. **Update `.env`** to point to your local PostgreSQL:
   ```env
   PGHOST=localhost
   PGPORT=5432
   ```

4. **Run migrations**:
   ```bash
   uv run alembic upgrade head
   ```

5. **Start the server**:
   ```bash
   uv run uvicorn app.app:app --host 0.0.0.0 --port 8000 --reload
   ```

## Google OAuth Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google+ API**:
   - Navigate to "APIs & Services" > "Library"
   - Search for "Google+ API" and enable it

3. **Create OAuth 2.0 Credentials**:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Choose "Web application"
   - Add authorized redirect URIs:
     - `http://localhost:8000/example` (for local development)
     - `https://your-domain.com/example` (for production)
   - Copy the Client ID and Client Secret

4. **Update `.env` file**:
   ```env
   GOOGLE_OAUTH_CLIENT_ID=your_client_id_here
   GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret_here
   ```

## AWS Setup

### Creating AWS Account

1. **Sign up for AWS**:
   - Go to [AWS Sign Up](https://aws.amazon.com/)
   - Create a new account (requires credit card, but free tier available)
   - Complete email verification

2. **Access AWS Console**:
   - Log in to [AWS Console](https://console.aws.amazon.com/)
   - Select your preferred region (e.g., `eu-central-1`)

### Creating S3 Bucket

1. **Navigate to S3**:
   - In AWS Console, search for "S3" and open it

2. **Create a new bucket**:
   - Click "Create bucket"
   - Enter bucket name (must be globally unique, e.g., `project-x-media-2024`)
   - Select region (e.g., `eu-central-1`)
   - Click "Create bucket"

3. **Configure bucket permissions** (if needed):
   - Go to bucket > "Permissions" tab
   - Edit "Bucket policy" to allow your application access
   - Example policy (adjust bucket name and principal):
     ```json
     {
       "Version": "2012-10-17",
       "Statement": [
         {
           "Sid": "AllowAppAccess",
           "Effect": "Allow",
           "Principal": {
             "AWS": "arn:aws:iam::YOUR_ACCOUNT_ID:user/YOUR_IAM_USER"
           },
           "Action": ["s3:PutObject", "s3:GetObject", "s3:DeleteObject"],
           "Resource": "arn:aws:s3:::your-bucket-name/*"
         }
       ]
     }
     ```

4. **Create IAM User for S3 Access**:
   - Go to IAM > Users > "Create user"
   - Name: `project-x-s3-user`
   - Attach policy: `AmazonS3FullAccess` (or create custom policy for specific bucket)
   - Create access key:
     - Go to user > "Security credentials" tab
     - Click "Create access key"
     - Choose "Application running outside AWS"
     - Save Access Key ID and Secret Access Key securely

5. **Configure AWS credentials** (choose one method):

   **Method 1: Environment variables** (add to `.env`):
   ```env
   AWS_DEFAULT_REGION=eu-central-1
   AWS_S3_MEDIA_BUCKET=your-bucket-name
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   ```

   **Method 2: AWS credentials file** (recommended for local development):
   ```bash
   mkdir -p ~/.aws
   nano ~/.aws/credentials
   ```
   Add:
   ```ini
   [default]
   aws_access_key_id = your_access_key_id
   aws_secret_access_key = your_secret_access_key
   ```

   **Method 3: IAM role** (recommended for EC2):
   - Attach IAM role with S3 permissions to your EC2 instance
   - No credentials needed in `.env` file

### Creating EC2 Instance

1. **Launch EC2 Instance**:
   - In AWS Console, search for "EC2" and open it
   - Click "Launch Instance"

2. **Configure Instance**:
   - **Name**: `project-x-backend`
   - **AMI**: Choose "Ubuntu Server 22.04 LTS" (free tier eligible)
   - **Instance Type**: `t2.micro` (free tier) or `t3.small` for production
   - **Key Pair**: Create new or select existing (download `.pem` file)
   - **Network Settings**:
     - Allow HTTP (port 80)
     - Allow HTTPS (port 443)
     - Allow Custom TCP (port 8000) from your IP
   - **Storage**: 20 GB (free tier: 30 GB)
   - Click "Launch Instance"

3. **Configure Security Group** (if needed):
   - Go to EC2 > Security Groups
   - Edit inbound rules:
     - SSH (22) from your IP
     - HTTP (80) from anywhere (0.0.0.0/0)
     - HTTPS (443) from anywhere (0.0.0.0/0)
     - Custom TCP (8000) from your IP or load balancer

4. **Allocate Elastic IP** (optional, recommended):
   - Go to EC2 > Elastic IPs
   - Click "Allocate Elastic IP address"
   - Select your instance and click "Associate"

5. **Connect to Instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

## Deployment

### Deploying to EC2

1. **Connect to EC2 instance**:
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

2. **Install prerequisites**:
   ```bash
   sudo apt update
   sudo apt install -y python3.12 python3.12-venv python3-pip docker.io docker-compose git
   sudo usermod -aG docker $USER
   newgrp docker
   ```

3. **Install uv**:
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   source $HOME/.cargo/env
   ```

4. **Clone repository**:
   ```bash
   cd /home/ubuntu
   git clone <repository-url> project-x
   cd project-x
   ```

5. **Create `.env` file**:
   ```bash
   nano .env
   # Add all production environment variables
   ```

6. **Update environment variables for production**:
   ```env
   ENV=prod
   PGHOST=localhost  # Or RDS endpoint if using RDS
   PGPASSWORD=strong_production_password
   FRONTEND_REDIRECT_URI=https://your-frontend-domain.com/example
   GOOGLE_REDIRECT_URI=https://your-backend-domain.com/example
   AWS_DEFAULT_REGION=eu-central-1
   AWS_S3_MEDIA_BUCKET=your-production-bucket-name
   # AWS credentials via IAM role (recommended) or add AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY
   ```

7. **Attach IAM role to EC2 instance** (recommended for production):
   - Go to EC2 > Instances > Select your instance
   - Actions > Security > Modify IAM role
   - Select or create IAM role with S3 permissions
   - This eliminates the need for hardcoded credentials

8. **Set up PostgreSQL** (if not using RDS):
   ```bash
   sudo apt install -y postgresql postgresql-contrib
   sudo -u postgres psql
   ```
   ```sql
   CREATE DATABASE px;
   CREATE USER postgres WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE px TO postgres;
   \q
   ```

9. **Build and start services**:
   ```bash
   docker compose build
   docker compose up -d
   ```

10. **Run migrations**:
   ```bash
   docker compose exec backend alembic upgrade head
   ```

10. **Set up reverse proxy with Nginx** (recommended):
    ```bash
    sudo apt install -y nginx
    sudo nano /etc/nginx/sites-available/project-x
    ```

    Add configuration:
    ```nginx
    server {
        listen 80;
        server_name your-domain.com;

        location / {
            proxy_pass http://localhost:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
    ```

    Enable site:
    ```bash
    sudo ln -s /etc/nginx/sites-available/project-x /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl restart nginx
    ```

11. **Set up SSL with Let's Encrypt** (recommended):
    ```bash
    sudo apt install -y certbot python3-certbot-nginx
    sudo certbot --nginx -d your-domain.com
    ```

12. **Set up systemd service** (optional, for auto-restart):
    ```bash
    sudo nano /etc/systemd/system/project-x.service
    ```

    Add:
    ```ini
    [Unit]
    Description=Project X Backend
    After=docker.service
    Requires=docker.service

    [Service]
    Type=oneshot
    RemainAfterExit=yes
    WorkingDirectory=/home/ubuntu/project-x
    ExecStart=/usr/bin/docker compose up -d
    ExecStop=/usr/bin/docker compose down
    Restart=on-failure

    [Install]
    WantedBy=multi-user.target
    ```

    Enable service:
    ```bash
    sudo systemctl enable project-x
    sudo systemctl start project-x
    ```

## Database Migrations

### Create a new migration:
```bash
make migration m="description_of_changes"
# Or manually:
docker compose exec backend alembic revision --autogenerate -m "description_of_changes"
```

### Apply migrations:
```bash
make migrate
# Or manually:
docker compose exec backend alembic upgrade head
```

### Rollback migration:
```bash
docker compose exec backend alembic downgrade -1
```

## Testing

Run tests:
```bash
make test
# Or manually:
docker compose up postgres test
```

Run tests with coverage:
```bash
docker compose up postgres test
# Coverage report will be displayed in the output
```

## Project Structure

```
project-x/
├── app/
│   ├── application/      # Use cases and services
│   ├── common/           # Shared utilities
│   ├── config.py         # Configuration and environment variables
│   ├── domain/           # Business entities and repository interfaces
│   ├── infrastructure/   # Technical implementations (DB, external services)
│   ├── migrations/       # Alembic database migrations
│   └── presentation/     # HTTP/API layer (FastAPI routers)
├── tests/                # Test suite
├── alembic.ini           # Alembic configuration
├── docker-compose.yaml   # Docker Compose configuration
├── Dockerfile            # Docker build configuration
├── Makefile              # Common commands
├── pyproject.toml        # Python project configuration
└── README.md            # This file
```

## Additional Commands

- **Lint code**: `make lint`
- **Run pre-commit hooks**: `make precommit`
- **Build Docker images**: `make build`
- **Start only database**: `make up-db`

## Troubleshooting

### Database connection issues:
- Check PostgreSQL is running: `docker compose ps`
- Verify `.env` file has correct database credentials
- Check network connectivity between containers

### OAuth issues:
- Verify Google OAuth credentials are correct
- Check redirect URIs match exactly in Google Console
- Ensure `FRONTEND_REDIRECT_URI` and `GOOGLE_REDIRECT_URI` are correctly configured

### S3 upload issues:
- Verify AWS credentials are correct
- Check bucket permissions and IAM user policies
- Ensure bucket name matches `AWS_S3_MEDIA_BUCKET` in `.env`

### Port conflicts:
- Change port in `docker-compose.yaml` if port 8000 is in use
- Update `PGPORT` if PostgreSQL port conflicts
