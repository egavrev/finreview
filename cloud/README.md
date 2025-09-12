# Financial Review App - GCP Cloud Deployment

This folder contains all files related to Google Cloud Platform deployment.

## Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Firebase      │    │   Cloud Run     │    │   Cloud Run     │
│   Hosting       │◄──►│   (FastAPI)     │◄──►│   (PostgreSQL)  │
│   (Frontend)    │    │   (Backend)     │    │   (Database)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Files Overview

### Core Deployment Files
- **`Dockerfile.backend`** - FastAPI container configuration
- **`Dockerfile.postgres`** - PostgreSQL container configuration
- **`cloudbuild.yaml`** - Cloud Build pipeline for automated deployment
- **`cloud-scheduler.yaml`** - Cloud Scheduler configuration for keeping containers warm

### Configuration Files
- **`env.gcp.example`** - Environment variables template for production
- **`migrate.sql`** - Complete migration script with database initialization
- **`run_migration.sh`** - Bash script for easy migration execution

## Prerequisites

- ✅ GCP Project created
- ✅ Billing enabled ($300 free credits)
- ✅ APIs enabled (Cloud Run, Cloud Build, Container Registry)
- ✅ Service accounts created
- ✅ Secret Manager configured
- ✅ GitHub repository connected

## Quick Start

### 1. Connect GitHub Repository

1. **Go to GCP Console** → **Cloud Build** → **Triggers**
2. **Click "Create Trigger"**
3. **Fill in the details**:
   - **Name**: `finreview-deploy`
   - **Event**: `Push to a branch`
   - **Source**: Connect your GitHub repository
   - **Repository**: Select your `finreview` repository
   - **Branch**: `main`
   - **Configuration**: `Cloud Build configuration file (yaml or json)`
   - **Location**: `cloud/cloudbuild.yaml`

### 2. Deploy to Cloud Run

1. **Push your code** to GitHub
2. **Go to Cloud Build** → **Triggers**
3. **Click "Run"** to trigger deployment
4. **Watch the build progress** (takes 5-10 minutes)

### 3. Initialize Database

```bash
# Run the simple SQL migration
./cloud/run_migration.sh

# Or manually:
psql "postgresql://finreview_user:FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0@postgres-service-xxxxx-uc.a.run.app:5432/finreview" -f cloud/migrate.sql
```

### 4. Test the Deployment

After deployment, you'll get two URLs:
- **FastAPI**: `https://finreview-app-xxxxx-uc.a.run.app`
- **PostgreSQL**: `https://postgres-service-xxxxx-uc.a.run.app`

Test the health endpoints:
```bash
# Test FastAPI
curl https://finreview-app-xxxxx-uc.a.run.app/health

# Test Database Connection
curl https://finreview-app-xxxxx-uc.a.run.app/health/database
```

### 5. Keep Containers Warm (Optional)

To prevent cold starts during weekend usage:

1. **Go to Cloud Scheduler** in GCP Console
2. **Create new job** with these settings:
   - **Name**: `finreview-warm-up`
   - **Schedule**: `*/30 * * * *` (every 30 minutes)
   - **Target**: HTTP
   - **URL**: `https://finreview-app-xxxxx-uc.a.run.app/health`
   - **HTTP method**: GET

## Configuration Details

### Environment Variables

**FastAPI Service:**
- `DATABASE_URL`: PostgreSQL connection string
- `ENVIRONMENT`: production
- `FRONTEND_URL`: Firebase Hosting URL
- Secrets: Google OAuth credentials, JWT secret

**PostgreSQL Service:**
- `POSTGRES_DB`: finreview
- `POSTGRES_USER`: finreview_user
- `POSTGRES_PASSWORD`: Generated secure password

### Security

- **PostgreSQL Password**: `FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0`
- **OAuth Secrets**: Stored in Secret Manager
- **JWT Secret**: Stored in Secret Manager

## Cost Estimation

### Weekend Usage (2 hours per weekend, 4 weekends/month):
- **Cloud Run CPU**: ~$0.19/month
- **Cloud Run Memory**: ~$0.02/month
- **Cloud Scheduler**: Free (3 jobs)
- **Total**: ~$0.21/month

### With $300 Credits:
- **Duration**: 1,400+ months (practically free!)

## Troubleshooting

### Common Issues:

1. **Cold Start Delays**
   - Solution: Set up Cloud Scheduler
   - First request: 5-15 seconds
   - Subsequent requests: 50-100ms

2. **Database Connection Errors**
   - Check: PostgreSQL service is running
   - Check: Environment variables are correct
   - Check: Network connectivity between services

3. **Build Failures**
   - Check: All required files are committed
   - Check: Docker builds successfully locally
   - Check: Cloud Build logs for specific errors

### Health Check Endpoints:

- `/health` - Basic health check
- `/health/database` - Database connection test

## Next Steps

1. **Deploy Frontend** to Firebase Hosting
2. **Configure Custom Domain** (optional)
3. **Set up Monitoring** and alerts
4. **Add Backup Strategy** for PostgreSQL data

## Support

If you encounter issues:
1. Check Cloud Build logs
2. Check Cloud Run logs
3. Test health endpoints
4. Verify environment variables