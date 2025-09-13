# PostgreSQL VM Setup Guide

## **🎯 Overview**
Set up a PostgreSQL database server on Google Cloud e2-micro VM for your Financial Review application.

## **💰 Cost**
- **Monthly Cost**: ~$9.71/month
- **Annual Cost**: ~$116/year
- **Perfect for**: Weekend-only usage, low traffic

## **📋 Step 1: Create e2-micro VM**

### **In GCP Console:**
1. **Go to**: Compute Engine → VM instances
2. **Click**: "Create Instance"
3. **Configure**:
   ```
   Name: finreview-db
   Region: europe-west1 (Belgium)
   Zone: europe-west1-b
   Machine type: e2-micro
   Boot disk: 30 GB SSD (Ubuntu 22.04 LTS)
   Firewall: Allow HTTP and HTTPS traffic ✅
   ```

### **Network Configuration:**
1. **Click**: "Networking, Disks, Security, Management, Sole-tenancy"
2. **Networking tab**:
   - **Network tags**: `postgres-server`
   - **External IP**: Ephemeral (will get a static IP later)

## **📋 Step 2: Configure Firewall**

### **Create Firewall Rule:**
1. **Go to**: VPC Network → Firewall
2. **Click**: "Create Firewall Rule"
3. **Configure**:
   ```
   Name: allow-postgresql
   Direction: Ingress
   Target tags: postgres-server
   Source IP ranges: 0.0.0.0/0
   Protocols and ports: TCP 5432
   ```

## **📋 Step 3: Install PostgreSQL**

### **SSH into your VM:**
```bash
gcloud compute ssh finreview-db --zone=europe-west1-b
```

### **Install PostgreSQL:**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Start and enable PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Check status
sudo systemctl status postgresql
```

## **📋 Step 4: Configure PostgreSQL**

### **Set up database and user:**
```bash
# Switch to postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE finreview;

# Create user
CREATE USER finreview_user WITH PASSWORD 'FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0';

# Grant privileges
GRANT ALL PRIVILEGES ON DATABASE finreview TO finreview_user;

# Exit PostgreSQL
\q
```

### **Configure PostgreSQL for external connections:**
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/14/main/postgresql.conf

# Find and change:
listen_addresses = '*'

# Edit pg_hba.conf
sudo nano /etc/postgresql/14/main/pg_hba.conf

# Add at the end:
host    finreview    finreview_user    0.0.0.0/0    md5

# Restart PostgreSQL
sudo systemctl restart postgresql
```

## **📋 Step 5: Get Static IP (Optional but Recommended)**

### **Reserve Static IP:**
1. **Go to**: VPC Network → External IP addresses
2. **Click**: "Reserve Static Address"
3. **Configure**:
   ```
   Name: finreview-db-ip
   Region: europe-west1
   ```
4. **Attach to VM**: `finreview-db`

## **📋 Step 6: Update Cloud Build Configuration**

### **Replace in cloudbuild.yaml:**
```yaml
# Line 36: Replace YOUR_VM_EXTERNAL_IP with your actual IP
- 'DATABASE_URL=postgresql://finreview_user:FlhugG77XDC1_0SlYUfhuzd-TkEySuwTtYFcV3luIh0@YOUR_ACTUAL_IP:5432/finreview'
```

## **📋 Step 7: Test Connection**

### **From your local machine:**
```bash
# Test connection (replace with your actual IP)
psql -h YOUR_ACTUAL_IP -p 5432 -U finreview_user -d finreview
```

### **Expected output:**
```
Password for user finreview_user: [enter password]
psql (14.x)
SSL connection (protocol: TLSv1.3, cipher: TLS_AES_256_GCM_SHA384, bits: 256, compression: off)
Type "help" for help.

finreview=>
```

## **✅ Verification Checklist**

- [ ] VM created and running
- [ ] PostgreSQL installed and running
- [ ] Database `finreview` created
- [ ] User `finreview_user` created with password
- [ ] Firewall rule allows port 5432
- [ ] PostgreSQL accepts external connections
- [ ] Static IP reserved (optional)
- [ ] Connection test successful
- [ ] Cloud Build DATABASE_URL updated with actual IP

## **🔧 Troubleshooting**

### **Connection refused:**
- Check firewall rule
- Verify PostgreSQL is listening on all interfaces
- Check pg_hba.conf configuration

### **Authentication failed:**
- Verify user password
- Check pg_hba.conf for correct user/database combination

### **Can't connect from Cloud Run:**
- Ensure external IP is correct in DATABASE_URL
- Check if VM is running
- Verify PostgreSQL service status

## **💡 Security Notes**

- **Change default password** in production
- **Consider SSL** for production use
- **Limit source IPs** in firewall rules if possible
- **Regular backups** recommended
- **Keep PostgreSQL updated**
