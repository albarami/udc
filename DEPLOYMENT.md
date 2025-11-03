# 🚀 Production Deployment Guide

## Prerequisites

- Python 3.11+
- Docker (optional, for containerized deployment)
- Anthropic API key
- 2GB RAM minimum
- Linux/macOS/Windows

## Local Development

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables

```bash
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### 3. Run Chainlit App

```bash
chainlit run app.py
```

**Access at:** http://localhost:8000

## Docker Deployment

### 1. Build Image

```bash
docker build -t intelligence-system .
```

### 2. Run Container

```bash
docker run -p 8000:8000 \
  -e ANTHROPIC_API_KEY=your_key_here \
  -v $(pwd)/logs:/app/logs \
  intelligence-system
```

### 3. Using Docker Compose

```bash
# Set API key in .env file
echo "ANTHROPIC_API_KEY=your_key_here" > .env

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Cloud Deployment

### AWS Elastic Beanstalk

1. **Install EB CLI:**
```bash
pip install awsebcli
```

2. **Initialize:**
```bash
eb init -p docker intelligence-system
```

3. **Create environment:**
```bash
eb create production-env
```

4. **Deploy:**
```bash
eb deploy
```

### Google Cloud Run

1. **Build and push:**
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/intelligence-system
```

2. **Deploy:**
```bash
gcloud run deploy intelligence-system \
  --image gcr.io/PROJECT_ID/intelligence-system \
  --platform managed \
  --region us-central1 \
  --set-env-vars ANTHROPIC_API_KEY=your_key
```

### Azure Container Instances

```bash
az container create \
  --resource-group myResourceGroup \
  --name intelligence-system \
  --image your-registry/intelligence-system:latest \
  --dns-name-label intelligence-system \
  --ports 8000 \
  --environment-variables ANTHROPIC_API_KEY=your_key
```

## Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8000
```

### Logs

```bash
# View logs
tail -f logs/intelligence_*.log

# Docker logs
docker-compose logs -f
```

### Performance Metrics

Check logs for:
- Query execution times
- Node performance
- Cost per query
- Error rates

## Security

### Environment Variables

**Never commit .env file.** Use secrets management:

- **AWS:** AWS Secrets Manager
- **GCP:** Secret Manager
- **Azure:** Key Vault

### API Rate Limiting

Configure in `src/config/settings.py`:

```python
MAX_REQUESTS_PER_MINUTE = 60
MAX_COST_PER_HOUR = 100.00
```

### HTTPS

Use reverse proxy (nginx):

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Scaling

### Horizontal Scaling

Run multiple instances behind load balancer:

```yaml
# docker-compose-scaled.yml
services:
  intelligence-system:
    build: .
    deploy:
      replicas: 3
    # ... rest of config
  
  nginx:
    image: nginx:latest
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - intelligence-system
```

### Performance Tuning

- Enable parallel execution for speed-critical scenarios
- Use caching for repeated queries
- Implement request queuing for high load

## Backup & Recovery

### Logs

```bash
# Archive logs daily
tar -czf logs_$(date +%Y%m%d).tar.gz logs/
```

### State

The system is stateless - no database needed. Conversation history in Chainlit is ephemeral.

## Troubleshooting

### Issue: Slow responses

- Check node execution times in logs
- Consider enabling parallel execution
- Verify API latency

### Issue: High costs

- Monitor cumulative costs in logs
- Adjust MAX_COST_PER_QUERY
- Use cheaper models for extraction

### Issue: Fabrication detected

- Check extraction quality
- Review fact verification logs
- Ensure proper citation format

## Support

For issues, check:
- Logs in `logs/` directory
- Performance metrics in Chainlit UI
- Error messages in console

## Configuration

### Toggle Features

Edit `app.py`:

```python
ENABLE_PARALLEL = False  # Toggle parallel execution
SHOW_DEBUG_INFO = True   # Show performance metrics
STREAM_UPDATES = True    # Stream node updates in real-time
```

### Adjust Complexity Routing

Edit `ultimate-intelligence-system/src/nodes/classify.py` to adjust complexity thresholds.

## Production Checklist

- [ ] API key configured securely
- [ ] HTTPS enabled
- [ ] Rate limiting configured
- [ ] Logs rotation setup
- [ ] Health checks working
- [ ] Monitoring dashboard setup
- [ ] Backup strategy defined
- [ ] Error alerting configured
- [ ] Load testing completed
- [ ] Documentation reviewed

## Performance Benchmarks

Based on Phase 5 testing:

| Query Type | Execution Time | Nodes Used | Cost/Query |
|------------|----------------|------------|------------|
| Simple     | ~10 seconds    | 4 nodes    | ~$0.05     |
| Medium     | ~20 seconds    | 5 nodes    | ~$0.10     |
| Complex    | ~50 seconds    | 10 nodes   | ~$0.25     |

## Next Steps

1. Run `chainlit run app.py` to test locally
2. Test with sample queries
3. Monitor performance and costs
4. Deploy to staging environment
5. Run load tests
6. Deploy to production

---

**Built with Phase 6 - Production Ready** 🚀
