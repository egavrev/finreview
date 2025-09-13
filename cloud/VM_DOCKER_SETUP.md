# PostgreSQL Docker Setup on e2-micro VM

## **🐳 Docker Approach**

### **Step 1: Create e2-micro VM**
Same as before - create e2-micro VM in GCP Console.

### **Step 2: Install Docker**
```bash
# SSH into VM
gcloud compute ssh finreview-db --zone=europe-west1-b

# Install Docker
sudo apt update
sudo apt install docker.io docker-compose -y

# Add user to docker group
sudo usermod -aG docker $USER

# Logout and login again (or run: newgrp docker)
exit
gcloud compute ssh finreview-db --zone=europe-west1-b
```

### **Step 3: Copy Files to VM**
```bash
# Copy docker-compose file
scp cloud/docker-compose-vm.yml YOUR_VM_IP:~/
scp cloud/migrate.sql YOUR_VM_IP:~/

# SSH back into VM
gcloud compute ssh finreview-db --zone=europe-west1-b

# Create directory and move files
mkdir finreview-db
mv docker-compose-vm.yml finreview-db/
mv migrate.sql finreview-db/
cd finreview-db
```

### **Step 4: Start PostgreSQL with Docker**
```bash
# Start PostgreSQL container
docker-compose up -d

# Check if running
docker ps

# View logs
docker logs finreview-postgres
```

### **Step 5: Configure Firewall**
Same firewall rules as before - allow port 5432.

## **⚖️ Which Should You Choose?**

### **Choose Direct Install If:**
- ✅ You want simplicity
- ✅ You want lower resource usage
- ✅ You prefer traditional server setup
- ✅ You want easier maintenance

### **Choose Docker If:**
- ✅ You prefer containerized deployments
- ✅ You want consistent environments
- ✅ You plan to run multiple services
- ✅ You're familiar with Docker

## **💰 Cost Impact:**
Both approaches cost the same (~$9.71/month) since the VM is the same.

## **🔧 My Recommendation:**
**Go with Direct Install** - it's simpler, uses fewer resources, and is more reliable for a single PostgreSQL service.
