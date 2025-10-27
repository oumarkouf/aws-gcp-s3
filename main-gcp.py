from fastapi import FastAPI, UploadFile, File, HTTPException
from google.cloud import storage
import os

# Set environment variable for Google credentials
GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "service-account.json")
BUCKET_NAME = os.getenv("GCS_BUCKET", "my-fastapi-bucket")

# Initialize GCS client
storage_client = storage.Client()
bucket = storage_client.bucket(BUCKET_NAME)

app = FastAPI(title="GCP Storage Microservice")

@app.get("/buckets")
def list_buckets():
    """List all GCS buckets"""
    buckets = storage_client.list_buckets()
    return {"buckets": [b.name for b in buckets]}

@app.get("/buckets/{bucket_name}/objects")
def list_objects(bucket_name: str):
    """List all objects in a bucket"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blobs = bucket.list_blobs()
        return {"bucket": bucket_name, "objects": [b.name for b in blobs]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/buckets/{bucket_name}/upload")
async def upload_file(bucket_name: str, file: UploadFile = File(...)):
    """Upload file to GCS"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(file.filename)
        blob.upload_from_file(file.file, rewind=True)
        return {"message": f"File '{file.filename}' uploaded to '{bucket_name}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/buckets/{bucket_name}/download/{filename}")
def download_file(bucket_name: str, filename: str):
    """Generate signed URL for download"""
    try:
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(filename)
        url = blob.generate_signed_url(version="v4", expiration=3600, method="GET")
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
