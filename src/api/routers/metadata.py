from fastapi import APIRouter, UploadFile, File, HTTPException
from mutagen import MutagenError
from starlette import status
from starlette.responses import Response

from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.myapi.metadata_model import MetadataResponse
from src.service.extract_metadata import extract_metadata_from_mp3_file

router = APIRouter(
    prefix="/api/metadata", tags=["ID3 Service"]
)


@router.post("/get-data", response_model=MetadataResponse, response_model_exclude_none=True)
def upload_file(response: Response, file: UploadFile = File(..., media_type="audio/mpeg", description="The mp3 file to upload")):
    try:
        metadata: MetadataResponse = extract_metadata_from_mp3_file(file)
        if metadata.failed_tags:
            # specifies that the request was successful but some parts of the metadata are missing
            response.status_code = status.HTTP_206_PARTIAL_CONTENT
        return metadata
    except (MutagenError, NoMetaDataError, IOError) as e:
        if type(e) == NoMetaDataError:
            # 404 indicates normally that the specified resource was not found,
            # but it is also possible to use it when requested data is missing (metadata)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e.args[0]))
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e.args[0]))
