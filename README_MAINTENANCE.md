# StockWellness Maintenance Scripts

## S3 Data Management

### `complete_fix_s3.py` ⭐ IMPORTANT
**Purpose**: Regenerates both `chunks.json` and `embeddings.npy` in S3 from clean local data
**When to use**: If S3 data gets corrupted or embeddings/chunks become mismatched
**What it does**:
- Loads clean data from `extracted_books_final.json`
- Creates matching embeddings for all text chunks  
- Uploads both files to S3 with proper field mapping
- Ensures Lambda function works correctly

### `quick_fix_metadata.py`
**Purpose**: Quick fix for metadata field mapping issues
**When to use**: If book names/page numbers are missing but text is OK

### `original_chunks.json`  
**Purpose**: Backup of S3 chunks.json before our fixes
**Use**: Reference for debugging or rollback if needed

## Key Files for Deployment

### Core Application
- `app.py` - Main Flask application
- `requirements.txt` - Python dependencies
- `Dockerfile` - Container configuration for Render
- `utils/llm_client_lambda_api.py` - AWS Lambda integration

### Data Files
- `extracted_books_final.json` - Clean book data (43 chunks)
- Source of truth for regenerating S3 data

### AWS Lambda
- `lambda_deploy/lambda_function_semantic.py` - Optimized semantic search function
- Uses precomputed embeddings from S3 for fast queries

## Emergency Procedures

### If S3 Data Gets Corrupted
1. Run: `python complete_fix_s3.py`
2. Wait 2-3 minutes for Lambda to pick up new data
3. Test endpoint: `https://7dg4etgob2uxmrv23yv5tawslu0dnhvj.lambda-url.us-east-2.on.aws/`

### If Lambda Seems Slow
- Lambda uses cached embeddings - corruption forces expensive recomputation
- Solution: Fix S3 data with `complete_fix_s3.py`

### If Books/Page Numbers Missing
- Field mapping issue between S3 data and Lambda expectations
- Lambda expects: `book`, `page`, `text`
- Local data has: `book_name`, `page_number`, `text`
- Script handles this conversion automatically 