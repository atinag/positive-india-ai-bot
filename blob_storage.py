from azure.storage.blob import BlobServiceClient
from logger import logger
from config import AZURE_STORAGE_CONNECTION_STRING, CONTAINER_NAME, POSTED_TWEETS_FILE, BLOB_NAME  # Import from config.py
import json  # Required for JSON operations


def download_blob(blob_name: str, download_path: str) -> None:
    """
    Downloads a blob from Azure Blob Storage.

    Args:
        blob_name: The name of the blob to download.
        download_path: The local path to save the downloaded blob.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        with open(download_path, "wb") as file:
            blob_client = container_client.get_blob_client(blob_name)
            file.write(blob_client.download_blob().readall())

        logger.info(f"Blob '{blob_name}' downloaded successfully to '{download_path}'.")
    except Exception as e:
        logger.error(f"Error downloading blob '{blob_name}': {e}")


def upload_blob(file_path: str, blob_name: str) -> None:
    """
    Uploads a file to Azure Blob Storage.

    Args:
        file_path: The local path of the file to upload.
        blob_name: The name of the blob to create or overwrite.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        with open(file_path, "rb") as file:
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(file, overwrite=True)

        logger.info(f"File '{file_path}' uploaded successfully as blob '{blob_name}'.")
    except Exception as e:
        logger.error(f"Error uploading blob '{blob_name}': {e}")


def initialize_posted_tweets():
    """
    Ensures the posted_tweets.json file exists in Azure Blob Storage.
    If it doesn't exist, initializes it with an empty list.
    """
    try:
        blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)
        container_client = blob_service_client.get_container_client(CONTAINER_NAME)

        # Check if the blob exists
        blob_client = container_client.get_blob_client(BLOB_NAME)
        if (blob_client.exists()):
            logger.info(f"Blob '{BLOB_NAME}' already exists in Azure Blob Storage. Skipping initialization.")
            return

        # If the blob doesn't exist, create it with an empty list
        with open(POSTED_TWEETS_FILE, "w") as file:
            json.dump([], file)

        # Upload the file to Azure Blob Storage
        upload_blob(POSTED_TWEETS_FILE, BLOB_NAME)
        logger.info(f"Initialized '{BLOB_NAME}' in Azure Blob Storage with an empty list.")
    except Exception as e:
        logger.error(f"Error initializing '{BLOB_NAME}': {e}")