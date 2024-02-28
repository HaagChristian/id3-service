from io import BytesIO

import pytest
from fastapi import UploadFile


@pytest.fixture
def create_upload_file():
    def _create_upload_file(content: bytes, filename: str):
        return UploadFile(filename=filename, file=BytesIO(content))

    return _create_upload_file
