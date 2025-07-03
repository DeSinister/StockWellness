# 🚀 AWS Lambda + S3 Deployment Guide

Deploy StockWellness as a serverless application using AWS Lambda for compute and S3 for storage.

## 📋 Prerequisites

### 1. AWS Account Setup
```bash
# Install AWS CLI
pip install awscli

# Configure AWS credentials
aws configure
# Enter your Access Key ID, Secret Access Key, Region (us-east-1), Output format (json)
```

### 2. Install Deployment Tools
```bash
# Install Serverless Framework
npm install -g serverless

# Install Python dependencies for deployment
pip install boto3 tqdm
```

## 🎯 **HUGE ADVANTAGE: Your Pre-computed Cache!**

Instead of computing embeddings on Lambda (10+ minutes), you'll upload your existing cache to S3:
- ✅ `cache/rag/embeddings.npy` (5MB) - Your pre-computed book embeddings
- ✅ `cache/rag/chunks.json` (4.5MB) - Your processed book chunks
- ✅ Cold start time: 30 seconds instead of 10+ minutes!
- ✅ Cost savings: $100s saved on computation

## 🚀 Step-by-Step Deployment

### Step 1: Upload Your Cache to S3
```bash
# Upload all your pre-computed assets to S3
python upload_to_s3.py
```

This uploads:
- 📚 Your RAG cache (`embeddings.npy`, `chunks.json`) 
- 📖 Investment books (`Books/` folder)
- 🎨 Static assets (`static/`, `templates/`)

### Step 2: Configure Serverless
```bash
# Edit serverless.yml if needed
# - Change S3 bucket name
# - Adjust memory/timeout settings
# - Set environment variables
```

### Step 3: Deploy to Lambda
```bash
# Install serverless plugins
npm install serverless-python-requirements serverless-wsgi

# Deploy to AWS
serverless deploy

# Get the endpoint URL
serverless info
```

### Step 4: Set Environment Variables
```bash
# Set your API keys in AWS Lambda console or via CLI
aws lambda update-function-configuration \
  --function-name stockwellness-dev-app \
  --environment Variables='{
    "ANTHROPIC_API_KEY":"your_anthropic_key",
    "NEWS_API_KEY":"your_news_api_key",
    "SECRET_KEY":"your_secret_key"
  }'
```

## 💰 Cost Estimation

**Lambda Pricing (10GB RAM):**
- Memory: $0.0000166667 per GB-second
- Requests: $0.20 per 1M requests

**Example Usage:**
- 1000 analyses/month
- 30 seconds average per analysis
- **Monthly cost: ~$8-15** (much cheaper than dedicated servers!)

**S3 Storage:**
- Standard storage: $0.023 per GB/month  
- Your cache (~10MB): **~$0.01/month**

## 🔧 Configuration Details

### Lambda Function Settings:
- **Runtime:** Python 3.11
- **Memory:** 10GB (needed for sentence transformers + embeddings)
- **Timeout:** 15 minutes (max Lambda limit)
- **Handler:** `lambda_handler.handler`

### S3 Bucket Structure:
```
stockwellness-models/
├── rag/
│   ├── embeddings.npy      # Your pre-computed embeddings!
│   └── chunks.json         # Your processed book chunks
├── books/                  # Investment PDFs (backup)
├── static/                 # Web assets  
└── templates/              # HTML templates
```

### Environment Variables:
- `ANTHROPIC_API_KEY` - Your Claude API key
- `NEWS_API_KEY` - Your NewsAPI key  
- `SECRET_KEY` - Random secret for Flask
- `S3_BUCKET_NAME` - Your S3 bucket name
- `USE_S3_CACHE` - Set to "true"

## 🚀 Performance Optimizations

### Cold Start Optimization:
1. **Container Reuse:** Global variables cache models in memory
2. **S3 Download:** Downloads embeddings once per container
3. **Lazy Loading:** Models loaded only when needed
4. **Batch Processing:** Efficient embedding computation

### Memory Management:
- Lambda containers reuse loaded models
- Embeddings cached in `/tmp` folder
- Automatic cleanup after container recycling

## 📊 Monitoring & Debugging

### View Logs:
```bash
# Real-time logs
serverless logs -f app -t

# CloudWatch logs
aws logs filter-log-events \
  --log-group-name /aws/lambda/stockwellness-dev-app \
  --start-time $(date -d '1 hour ago' +%s)000
```

### Common Issues:
1. **Timeout Errors:** Increase timeout in `serverless.yml`
2. **Memory Errors:** Increase `memorySize` to 10240 (10GB)
3. **S3 Access:** Check IAM permissions for S3 bucket
4. **Cold Starts:** First request takes 30-60 seconds (normal)

## 🔄 Updates & Maintenance

### Deploy Updates:
```bash
# Deploy code changes
serverless deploy

# Deploy single function (faster)
serverless deploy function -f app
```

### Update S3 Cache:
```bash
# Re-upload cache if you retrain embeddings
python upload_to_s3.py
```

## 🎉 Testing Your Deployment

### Test Endpoint:
```bash
# Get your Lambda endpoint
ENDPOINT=$(serverless info --verbose | grep ServiceEndpoint | cut -d' ' -f2)

# Test health check
curl $ENDPOINT/health

# Test full analysis (will take 30-60 seconds first time)
curl -X POST $ENDPOINT/analyze -d "ticker=AAPL"
```

### Expected Response Times:
- **Cold start:** 30-60 seconds (first request)
- **Warm requests:** 5-15 seconds
- **Cached analysis:** 1-3 seconds

## 🆚 Lambda vs Traditional Deployment

| Aspect | Lambda + S3 | Traditional Server |
|--------|-------------|-------------------|
| **Cost** | $8-15/month | $25-100/month |
| **Scaling** | Automatic | Manual |
| **Maintenance** | Zero | High |
| **Cold Starts** | 30-60s first request | None |
| **Warm Performance** | 5-15s | 3-10s |
| **Setup Complexity** | Medium | Low |

## 🎯 Success Checklist

- ✅ AWS credentials configured
- ✅ S3 bucket created and files uploaded
- ✅ Serverless framework installed
- ✅ Lambda function deployed
- ✅ Environment variables set
- ✅ Health check returns 200
- ✅ Test analysis completes successfully
- ✅ Your embeddings loading from S3 cache

**Your StockWellness app is now serverless! 🚀**

No more server management, automatic scaling, and you're only paying for what you use! 