from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from azure.identity import DefaultAzureCredential
from azure.storage.filedatalake import DataLakeServiceClient

import traceback

app = FastAPI()
print("LOADING APP.PY")

import os

ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT")
ACCOUNT_KEY = os.getenv("STORAGE_KEY")
service_client = DataLakeServiceClient(
    account_url=f"https://{ACCOUNT_NAME}.dfs.core.windows.net",
    credential=ACCOUNT_KEY
)

@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/upload")
async def upload(
    zone: str = Form(...),
    dataset: str = Form(...),
    file: UploadFile = File(...)
):
    print("yup")
    try:
        print("=" * 50)
        print("UPLOAD REQUEST RECEIVED")
        print(f"ACCOUNT: {ACCOUNT_NAME}")
        print(f"ZONE: {zone}")
        print(f"DATASET: {dataset}")
        print(f"FILENAME: {file.filename}")

        fs_client = service_client.get_file_system_client(zone)

        print("Connected to filesystem")

        try:
            fs_client.create_directory(dataset)
            print(f"Created directory: {dataset}")
        except Exception as e:
            print(f"Directory already exists or could not be created: {e}")

        file_path = f"{dataset}/{file.filename}"

        print(f"Target path: {file_path}")

        file_client = fs_client.get_file_client(file_path)

        contents = await file.read()

        print(f"File size: {len(contents)} bytes")

        file_client.upload_data(
            contents,
            overwrite=True
        )

        print("UPLOAD SUCCESSFUL")
        print("=" * 50)

        return {
            "status": "success",
            "storage_account": ACCOUNT_NAME,
            "zone": zone,
            "dataset": dataset,
            "filename": file.filename,
            "path": file_path
        }

    except Exception as e:

        print("=" * 50)
        print("UPLOAD FAILED")
        print(str(e))
        traceback.print_exc()
        print("=" * 50)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )