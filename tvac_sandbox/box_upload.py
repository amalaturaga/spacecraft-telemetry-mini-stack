# tvac_sandbox/box_upload.py
"""
Module for uploading files to a Box folder using a Client Credentials Grant auth.

This module provides a BoxUploader class that handles authentication and file uploads to a specified Box folder. 
It uses the boxsdk library to interact with the Box API.

"""
import os
from pathlib import Path
from box_sdk_gen import (
    BoxClient,
    BoxCCGAuth,
    CCGConfig,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class BoxUploader:
    """ 
    Uploades files to a Box using CCG auth.

    Class allows for creating one setup state so no need to re-authenticate for each upload.

    """
    def __init__(self, client_id=None, client_secret=None, enterprise_id=None):
        """
        Authenticate to Box and create a reusable client.

        All three credentials can be passed directly OR read from env vars:
            - BOX_CLIENT_ID
            - BOX_CLIENT_SECRET
            - BOX_ENTERPRISE_ID
        """
        client_id = client_id or os.getenv('BOX_CLIENT_ID')
        client_secret = client_secret or os.getenv('BOX_CLIENT_SECRET')
        enterprise_id = enterprise_id or os.getenv('BOX_ENTERPRISE_ID')

        # If credentials are missing, raise error
        if not all([client_id, client_secret, enterprise_id]):
            missing = [
                name for name, value in [
                    ("BOX_CLIENT_ID", client_id),
                    ("BOX_CLIENT_SECRET", client_secret),
                    ("BOX_ENTERPRISE_ID", enterprise_id),
                ] if not value
            ]
            raise RuntimeError(
                f"Missing Box credentials: {missing}. Set them in .env or pass to BoxUploader()."
            )
        
        # Authenticate using CCG
        ccg_config = CCGConfig(
            client_id=client_id,
            client_secret=client_secret,
            enterprise_id=enterprise_id,
        )
        auth = BoxCCGAuth(config=ccg_config)
        self.client = BoxClient(auth=auth)

    def upload_file(self, local_path, folder_id, new_name=None):
        """
        Upload a local file to a Box folder.

        Args:
            local_path (str): Path to the local file to upload.
            folder_id (str): ID of the Box folder to upload to.
            new_name (str, optional): New name for the file in Box. If not provided, original name is used.

        Returns:
            The Box web URL for the uploaded file that can be pasted into Epsilon3 procedure step.
        """
        # Validate local file path before attempting upload
        local_path = Path(local_path)
        if not local_path.exists():
            raise FileNotFoundError(f"Local file not found: {local_path}")
        
        # Determine name to use in Box
        upload_name = new_name or local_path.name

        # Build metadata Box needs for upload
        attributes = UploadFileAttributes(
            name=upload_name,
            parent=UploadFileAttributesParentField(id=str(folder_id)),
        )

        # Open local file in binary mode and upload to Box
        with open(local_path, "rb") as file_stream:
            uploaded_files = self.client.uploads.upload_file(
                attributes=attributes,
                file=file_stream,
            )

        # Upload returns a list of uploaded files, but we only upload one, so take the first entry
        uploaded_file = uploaded_files.entries[0]

        # Construct the Box web URL for the uploaded file
        file_url = f"https://app.box.com/file/{uploaded_file.id}"

        return file_url

if __name__ == "__main__":
    # Quick test of the BoxUploader class
    test_folder = os.getenv('BOX_TEST_FOLDER_ID')
    if not test_folder:
        print("Set BOX_TEST_FOLDER_ID in .env to run the test upload.")
        print("(it should be a folder you can write to, for testing only)")
        exit(1)

    # Create a test file to upload
    test_path = "/tmp/test_upload.txt"
    with open(test_path, "w") as f:
        f.write("Hello from BoxUploader test!\n")

    print("Authenticating and uploading test file to Box...")
    uploader = BoxUploader()
    print("Authenticated successfully.")

    print(f"Uploading {test_path} to Box folder {test_folder}...")
    url = uploader.upload_file(test_path, test_folder)
    print(f"Success! View at: {url}")