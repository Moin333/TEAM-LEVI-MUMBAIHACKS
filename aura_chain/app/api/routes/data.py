from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
import pandas as pd
import uuid
import io
import json
import redis.asyncio as redis
from app.config import get_settings

router = APIRouter(prefix="/data", tags=["data"])

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    """
    Upload dataset (CSV, Excel, JSON)
    Returns dataset_id for use in queries
    """
    try:
        content = await file.read()
        
        # Detect file type and parse
        if file.filename.endswith('.csv'):
            # Handle byte content for CSV
            df = pd.read_csv(io.BytesIO(content))
        elif file.filename.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(io.BytesIO(content))
        elif file.filename.endswith('.json'):
            df = pd.read_json(io.BytesIO(content))
        else:
            raise HTTPException(400, "Unsupported file format")
        
        dataset_id = str(uuid.uuid4())
        settings = get_settings()
        
        # Store in Redis
        # FIX 1: Initialize Redis properly
        redis_client = await redis.from_url(settings.REDIS_URL)
        
        # FIX 2: Explicitly use orient='records' for reliable JSON structure
        # This converts DataFrame to a list of dicts: [{"col": val}, ...]
        json_data = df.to_json(orient='records')
        
        await redis_client.setex(
            f"dataset:{dataset_id}",
            3600,  # 1 hour TTL
            json_data
        )
        await redis_client.close()
        
        return {
            "dataset_id": dataset_id,
            "filename": file.filename,
            "shape": df.shape,
            "columns": list(df.columns),
            "preview": df.head(5).to_dict('records')
        }
        
    except Exception as e:
        # Log the actual error for debugging
        print(f"Upload Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dataset/{dataset_id}")
async def get_dataset(dataset_id: str):
    """Retrieve dataset by ID"""
    try:
        settings = get_settings()
        redis_client = await redis.from_url(settings.REDIS_URL)
        
        # Fetch data (comes back as bytes)
        data = await redis_client.get(f"dataset:{dataset_id}")
        await redis_client.close()
        
        if not data:
            raise HTTPException(404, "Dataset not found")
        
        # FIX 3: Read using BytesIO and the same orientation
        # Redis returns bytes, so we wrap it in BytesIO
        df = pd.read_json(io.BytesIO(data), orient='records')
        
        return {
            "dataset_id": dataset_id,
            "shape": df.shape,
            "columns": list(df.columns),
            "data": df.to_dict('records')
        }
        
    except Exception as e:
        print(f"Retrieve Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))