from fastapi import FastAPI, UploadFile, File, HTTPException
import boto3
import os

# Environment variables (set these before running)
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET = os.getenv("S3_BUCKET", "my-fastapi-bucket")

# Initialize S3 client
s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION,
)

app = FastAPI(title="AWS S3 Microservice")

@app.get("/buckets")
def list_buckets():
    """List all S3 buckets"""
    response = s3.list_buckets()
    return {"buckets": [b["Name"] for b in response["Buckets"]]}

@app.get("/buckets/{bucket}/objects")
def list_objects(bucket: str):
    """List all objects in a bucket"""
    try:
        response = s3.list_objects_v2(Bucket=bucket)
        objects = [obj["Key"] for obj in response.get("Contents", [])]
        return {"bucket": bucket, "objects": objects}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/buckets/{bucket}/upload")
async def upload_file(bucket: str, file: UploadFile = File(...)):
    """Upload a file to S3"""
    try:
        s3.upload_fileobj(file.file, bucket, file.filename)
        return {"message": f"File '{file.filename}' uploaded to '{bucket}'"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/buckets/{bucket}/download/{filename}")
def download_file(bucket: str, filename: str):
    """Generate a presigned URL for download"""
    try:
        url = s3.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket, "Key": filename},
            ExpiresIn=3600,
        )
        return {"download_url": url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
