# Cloud Deployment Files

This folder contains all files related to Google Cloud Platform deployment.

## Files Overview

### Core Deployment Files
- **`postgres.Dockerfile`** - PostgreSQL container configuration
- **`cloudbuild.yaml`** - Cloud Build pipeline for automated deployment
- **`cloud-scheduler.yaml`** - Cloud Scheduler configuration for keeping containers warm
- **`DEPLOYMENT_GUIDE.md`** - Complete deployment instructions

### Configuration Files
- **`env.gcp.example`** - Environment variables template for production
- **`migrate_production.py`** - Script to migrate SQLite data to production PostgreSQL

## Quick Start

1. **Deploy to Cloud Run**:
   ```bash
   # Push code to GitHub, then trigger Cloud Build
   # Or manually run the deployment steps from DEPLOYMENT_GUIDE.md
   ```

2. **Migrate Existing Data**:
   ```bash
   # After deployment, run migration script
   python cloud/migrate_production.py
   ```

3. **Keep Containers Warm**:
   ```bash
   # Set up Cloud Scheduler jobs using cloud-scheduler.yaml
   ```

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Cloud Run     │    │   Cloud Run     │
│   Hosting       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Cost Estimation

- **Weekend usage** (2 hours/weekend, 4 weekends/month): ~$0.21/month
- **With $300 credits**: 1,400+ months (practically free!)

## Support

See `DEPLOYMENT_GUIDE.md` for detailed instructions and troubleshooting.
