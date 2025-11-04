# 🚀 Deploying Dhanvantri to Render

Complete guide for deploying the Dhanvantri Healthcare Chatbot to Render.com - a simple, scalable cloud platform.

## 🌟 Why Render?

- **Zero DevOps**: No infrastructure management needed
- **Auto-scaling**: Automatic scaling based on traffic
- **Built-in SSL**: Free SSL certificates with auto-renewal
- **Git Integration**: Deploy directly from GitHub
- **Cost-effective**: Pay only for what you use
- **Health Monitoring**: Built-in health checks and monitoring

## 📋 Prerequisites

1. **Render Account**: Sign up at [render.com](https://render.com)
2. **GitHub Repository**: Your code should be in a GitHub repository
3. **Ollama Service**: You'll need an external Ollama service (see options below)

## 🚀 Deployment Options

### Option 1: One-Click Deploy (Recommended)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/your-username/dhanvantri-chatbot)

### Option 2: Manual Deployment

#### Step 1: Prepare Your Repository

1. **Push your code to GitHub**:
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push origin main
   ```

2. **Ensure you have the Render configuration files**:
   - `render.yaml` (service configuration)
   - `Dockerfile.render` (optimized Dockerfile)
   - `render-entrypoint.sh` (startup script)

#### Step 2: Create Render Services

1. **Go to Render Dashboard**: https://dashboard.render.com
2. **Click "New +"** and select **"Blueprint"**
3. **Connect your GitHub repository**
4. **Select the repository** containing your Dhanvantri code
5. **Render will automatically detect** the `render.yaml` file

#### Step 3: Configure Environment Variables

Set these environment variables in your Render service:

```env
# Core Configuration
OLLAMA_BASE=https://your-ollama-service.onrender.com
MODEL_NAME=alibayram/medgemma:4b
WHISPER_BASE=http://localhost:5001
LOG_LEVEL=INFO
ENABLE_PRODUCTION_FEATURES=true

# Performance
MAX_CONCURRENT_REQUESTS=50
REQUEST_TIMEOUT=30

# Security (Render will auto-configure CORS_ORIGINS)
# CORS_ORIGINS will be automatically set based on your Render URL
```

#### Step 4: Deploy

1. **Click "Apply"** to start the deployment
2. **Wait for build to complete** (usually 5-10 minutes)
3. **Access your application** at the provided Render URL

## 🔧 Ollama Service Options

Since Render has resource limitations, you have several options for the Ollama service:

### Option A: External Ollama Service

**Recommended for production**

1. **Deploy Ollama on a dedicated server**:
   - Use a cloud provider with GPU support (AWS, GCP, Azure)
   - Use a specialized AI hosting service (Replicate, Hugging Face)

2. **Configure the endpoint**:
   ```env
   OLLAMA_BASE=https://your-ollama-server.com:11434
   ```

### Option B: Ollama on Render (Limited)

**For testing only - may have performance issues**

1. **Create a separate Render service** for Ollama:
   ```yaml
   # In render.yaml
   - type: web
     name: ollama-service
     env: docker
     plan: standard  # Minimum required
     dockerfilePath: ./ollama/Dockerfile
     envVars:
       - key: OLLAMA_KEEP_ALIVE
         value: 24h
   ```

2. **Create Ollama Dockerfile**:
   ```dockerfile
   # ollama/Dockerfile
   FROM ollama/ollama:latest
   
   # Pre-pull the model (optional, increases build time)
   # RUN ollama pull alibayram/medgemma:4b
   
   EXPOSE 11434
   CMD ["ollama", "serve"]
   ```

### Option C: Use Alternative Models

**For Render's resource constraints**

1. **Use smaller models**:
   ```env
   MODEL_NAME=llama2:7b  # Smaller, faster model
   # or
   MODEL_NAME=mistral:7b
   ```

2. **Use API-based models**:
   - OpenAI GPT-3.5/4
   - Anthropic Claude
   - Google Gemini

## 📊 Render Service Configuration

### Service Plans

| Plan | CPU | RAM | Price | Recommended For |
|------|-----|-----|-------|-----------------|
| Starter | 0.5 CPU | 512MB | $7/month | Development/Testing |
| Standard | 1 CPU | 2GB | $25/month | Production |
| Pro | 2 CPU | 4GB | $85/month | High Traffic |

### Recommended Configuration

```yaml
# render.yaml
services:
  - type: web
    name: dhanvantri-app
    env: docker
    plan: standard  # Minimum for production
    dockerfilePath: ./Dockerfile.render
    healthCheckPath: /api/health
    envVars:
      - key: OLLAMA_BASE
        value: https://your-ollama-service.com
      - key: LOG_LEVEL
        value: INFO
      - key: ENABLE_PRODUCTION_FEATURES
        value: true
```

## 🔒 Security Configuration

### Environment Variables

**Never commit sensitive data**. Use Render's environment variables:

1. **Go to your service dashboard**
2. **Click "Environment"**
3. **Add sensitive variables**:
   ```env
   OPENAI_API_KEY=your_api_key_here
   DATABASE_URL=postgresql://...
   JWT_SECRET=your_jwt_secret
   ```

### CORS Configuration

Render automatically configures CORS for your domain:
- Your app will be accessible at `https://your-service-name.onrender.com`
- CORS is automatically configured for this domain
- Additional domains can be added via `CORS_ORIGINS` environment variable

## 📈 Monitoring & Scaling

### Built-in Monitoring

Render provides:
- **Health Checks**: Automatic health monitoring
- **Metrics**: CPU, memory, and request metrics
- **Logs**: Real-time log streaming
- **Alerts**: Email notifications for issues

### Auto-scaling

```yaml
# In render.yaml
services:
  - type: web
    name: dhanvantri-app
    scaling:
      minInstances: 1
      maxInstances: 5
      targetCPUPercent: 70
```

### Custom Health Checks

Your app includes comprehensive health endpoints:
- `/api/health` - Overall system health
- `/api/ready` - Readiness probe
- `/api/live` - Liveness probe

## 🚨 Troubleshooting

### Common Issues

#### 1. Build Failures

```bash
# Check build logs in Render dashboard
# Common fixes:
- Ensure all dependencies are in requirements.txt
- Check Python version compatibility
- Verify Dockerfile syntax
```

#### 2. Service Won't Start

```bash
# Check service logs
# Common causes:
- Port configuration (use $PORT env var)
- Missing environment variables
- Ollama service unavailable
```

#### 3. Ollama Connection Issues

```bash
# Verify Ollama endpoint
curl https://your-ollama-service.com/api/tags

# Check environment variables
echo $OLLAMA_BASE
```

#### 4. Performance Issues

```bash
# Upgrade service plan
# Optimize model size
# Enable caching
# Use CDN for static assets
```

### Debug Commands

```bash
# View logs
render logs --service dhanvantri-app --tail

# Check service status
render services list

# Restart service
render services restart dhanvantri-app
```

## 💰 Cost Optimization

### Tips to Reduce Costs

1. **Use Starter plan** for development
2. **Sleep services** when not in use (Render feature)
3. **Optimize Docker image** size
4. **Use external Ollama** on cheaper GPU providers
5. **Implement caching** to reduce compute

### Estimated Monthly Costs

| Configuration | Cost | Use Case |
|---------------|------|----------|
| Starter + External Ollama | $7-15 | Development |
| Standard + External Ollama | $25-50 | Small Production |
| Pro + Dedicated Ollama | $100-200 | High Traffic |

## 🔄 CI/CD Integration

### Automatic Deployments

Render automatically deploys when you push to your main branch:

```bash
# Make changes
git add .
git commit -m "Update feature"
git push origin main

# Render automatically builds and deploys
```

### Manual Deployments

```bash
# Trigger manual deployment
render deploy --service dhanvantri-app
```

### Environment-based Deployments

```yaml
# Different branches for different environments
services:
  - type: web
    name: dhanvantri-staging
    branch: staging
    
  - type: web
    name: dhanvantri-production
    branch: main
```

## 📚 Additional Resources

### Render Documentation
- [Render Docs](https://render.com/docs)
- [Blueprint Specification](https://render.com/docs/blueprint-spec)
- [Environment Variables](https://render.com/docs/environment-variables)

### Optimization Guides
- [Docker Optimization](https://render.com/docs/docker)
- [Performance Best Practices](https://render.com/docs/performance)
- [Scaling Applications](https://render.com/docs/scaling)

## 🎉 Success!

Once deployed, your Dhanvantri Healthcare Chatbot will be available at:
- **URL**: `https://your-service-name.onrender.com`
- **Health Check**: `https://your-service-name.onrender.com/api/health`
- **API Docs**: `https://your-service-name.onrender.com/docs`

### Next Steps

1. **Configure custom domain** (optional)
2. **Set up monitoring alerts**
3. **Implement user analytics**
4. **Add database for persistence**
5. **Configure CDN for better performance**

---

**🏥 Your healthcare chatbot is now live and helping users worldwide!**

Need help? Check the [troubleshooting section](#-troubleshooting) or create an issue in the repository.