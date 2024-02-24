import logging

from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from mutagen import MutagenError
from starlette import status
from starlette.background import BackgroundTask
from starlette.responses import Response, FileResponse

from src.api.middleware.cleanup import cleanup
from src.api.middleware.custom_exceptions.MissingFileName import MissingFileNameError
from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.middleware.custom_exceptions.NoMetadataPassedError import NoMetadataPassedError
from src.api.myapi.metadata_model import MetadataResponse, MetadataToChangeInput
from src.service.work_with_metadata import extract_metadata_from_mp3_file, update_metadata_from_file
from src.settings.error_messages import MISSING_PARAMETER

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
def update_metadata(metadata: MetadataToChangeInput = Body(...), file: UploadFile = File(..., media_type="audio/mpeg",
                                                                                         description="The mp3 file where the metadata should be updated")):
    try:
        # check input
        if 'None' in metadata.album and 'None' in metadata.artist and 'None' in metadata.genre and \
                'None' in metadata.title and 'None' in metadata.date:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=MISSING_PARAMETER)

        temp_file_path, temp_file = update_metadata_from_file(file=file, metadata=metadata)
        return FileResponse(temp_file_path,
                            background=BackgroundTask(cleanup, temp_file_path=temp_file_path, temp_file=temp_file))
    except (MutagenError, NoMetaDataError, IOError, NoMetaDataError, MissingFileNameError, FileNotFoundError) as e:
        if type(e) == NoMetaDataError or type(e) == NoMetadataPassedError or type(e) == MissingFileNameError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e.args[0]))
        else:
            logging.error(f'Error occurred while updating metadata: {e}')
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail='Internal server error occurred. Please try again later.')
