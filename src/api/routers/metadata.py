from fastapi import APIRouter, UploadFile, File, HTTPException
from mutagen import MutagenError
from starlette import status
from starlette.responses import Response

from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.myapi.metadata_model import MetadataResponse, MetadataToChange
from src.service.work_with_metadata import extract_metadata_from_mp3_file, update_metadata_from_file

router = APIRouter(
    prefix="/api/metadata", tags=["ID3 Service"]
)


@router.post("/get-data", response_model=MetadataResponse, response_model_exclude_none=True)
def upload_file(response: Response,
                file: UploadFile = File(..., media_type="audio/mpeg", description="The mp3 file to upload")):
    try:
        metadata: MetadataResponse = extract_metadata_from_mp3_file(file)
        if metadata.failed_tags:
            # specifies that the request was successful but some parts of the metadata are missing
            response.status_code = status.HTTP_206_PARTIAL_CONTENT
        return metadata
    except (MutagenError, NoMetaDataError, IOError) as e:
        if type(e) == NoMetaDataError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e.args[0]))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e.args[0]))


@router.post("/update-metadata")
def update_metadata(metadata: MetadataToChange, file: UploadFile = File(..., media_type="audio/mpeg",
                                                                        description="The mp3 file where the metadata should be updated")):
    try:
        update_metadata_from_file(file=file, metadata=metadata)
    except (MutagenError, NoMetaDataError, IOError) as e:
        if type(e) == NoMetaDataError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e.args[0]))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e.args[0]))
