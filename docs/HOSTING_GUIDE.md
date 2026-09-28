# Chronicle Hosting & Cloud Deployment Guide

This guide provides step-by-step instructions to host and deploy the **Chronicle Data Ingestion & Analytics Platform** to the cloud.

---

## Table of Contents
1. [Option 1: Render.com (Recommended - 1-Click / Free Tier)](#option-1-rendercom-recommended)
2. [Option 2: Railway.app (Zero-Config PaaS)](#option-2-railwayapp-fastest-setup)
3. [Option 3: Any VPS (DigitalOcean / AWS EC2 / Hetzner) with Docker Compose](#option-3-vps-with-docker-compose)
4. [Option 4: AWS Enterprise Production (ECS Fargate + RDS via Terraform)](#option-4-aws-enterprise-production)
5. [Environment Variables Reference](#environment-variables-reference)

---

## Option 1: Render.com (Recommended)

Render provides free hosting for web services and PostgreSQL databases. The repository includes an automated `render.yaml` Blueprint file for 1-click deployment.

### Steps:
1. **Sign Up / Log In**: Go to [render.com](https://render.com) and connect your GitHub account.
2. **Create New Blueprint Instance**:
   * Click **New +** → **Blueprint**.
   * Connect your GitHub repository: `https://github.com/Spidey173/Chronicle`.
   * Render will automatically detect [`render.yaml`](../render.yaml) and configure:
     * A **Web Service** (`chronicle-platform`) running FastAPI and the interactive dashboard.
     * A **PostgreSQL Database** (`chronicle-db`).
3. **Deploy**:
   * Click **Apply**.
   * Render will automatically provision PostgreSQL, install dependencies, run migrations (`alembic upgrade head`), initialize the database (`python -m app.cli init`), and start Uvicorn.
4. **Access Your Application**:
   * Your service will be live at: `https://chronicle-platform.onrender.com`
   * Open `/dashboard` for the interactive UI.
   * Open `/docs` for OpenAPI Swagger documentation.
   * Default login: `admin@example.com` / `AdminSecurePassword123!`.

---

## Option 2: Railway.app (Fastest Setup)

Railway automatically detects Dockerfiles or Python applications with zero configuration.

### Steps:
1. **Sign Up / Log In**: Go to [railway.app](https://railway.app) and sign in with GitHub.
2. **Create a New Project**:
   * Click **New Project** → **Deploy from GitHub repo**.
   * Select `Spidey173/Chronicle`.
3. **Add Database**:
   * Right-click the canvas (or click **+ New**) → **Database** → **Add PostgreSQL**.
4. **Link Database to Service**:
   * In the `Chronicle` service settings, click **Variables**.
   * Add a variable reference: `DATABASE_URL` → select `${{Postgres.DATABASE_URL}}`.
   * Add:
     * `ENVIRONMENT=production`
     * `DEBUG=false`
     * `SECRET_KEY=<generate-a-random-32-char-string>`
5. **Set Start Command** (if not using Dockerfile):
   * `alembic upgrade head && python -m app.cli init && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
6. **Generate Domain**:
   * Go to **Settings** → **Networking** → **Generate Domain**.
   * Your live URL will be active immediately.

---

## Option 3: VPS with Docker Compose

If you have a Linux server (Ubuntu/Debian on AWS EC2, DigitalOcean Droplet, Hetzner, etc.):

### Steps:
1. **SSH into your server**:
   ```bash
   ssh root@your-server-ip
   ```
2. **Install Docker & Docker Compose**:
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
   apt-get install -y git
   ```
3. **Clone the repository**:
   ```bash
   git clone https://github.com/Spidey173/Chronicle.git
   cd Chronicle
   ```
4. **Configure Environment Variables**:
   ```bash
   cp .env.example .env
   nano .env   # Adjust SECRET_KEY, POSTGRES_PASSWORD, etc.
   ```
5. **Launch the entire stack**:
   ```bash
   docker compose up -d --build
   ```
6. **Verify Services**:
   ```bash
   docker compose ps
   docker compose logs -f chronicle-api
   ```
   * Open `http://your-server-ip:8000/` in your browser.

---

## Option 4: AWS Enterprise Production

For high-availability AWS deployments using ECS Fargate, RDS PostgreSQL Multi-AZ, and Amazon S3:

1. Follow the complete guide in [`docs/DEPLOYMENT_AWS.md`](DEPLOYMENT_AWS.md).
2. Provision with Terraform:
   ```bash
   cd infra/terraform
   terraform init
   terraform apply
   ```

---

## Environment Variables Reference

| Variable | Description | Default / Example |
| :--- | :--- | :--- |
| `APP_NAME` | Name displayed across platform | `Chronicle` |
| `ENVIRONMENT` | Target environment | `production` / `development` |
| `DEBUG` | Enable FastAPI debug mode | `false` |
| `DATABASE_URL` | PostgreSQL or SQLite connection URI | `postgresql+psycopg://user:pass@host:5432/analytics_db` |
| `SECRET_KEY` | JWT signing secret (min 32 characters) | *Random cryptographic string* |
| `INITIAL_ADMIN_EMAIL` | Initial admin account email | `admin@example.com` |
| `INITIAL_ADMIN_PASSWORD` | Initial admin password | `AdminSecurePassword123!` |
| `UPLOAD_DIR` | Storage path for uploads | `./storage/uploads` |
| `QUARANTINE_DIR` | Storage path for quarantined bad records | `./storage/quarantine` |
