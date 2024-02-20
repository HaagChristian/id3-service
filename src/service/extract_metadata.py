from fastapi import UploadFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.myapi.metadata_model import MetadataResponse
from src.settings.error_messages import NO_METADATA_ERROR


def extract_metadata_from_mp3_file(file: UploadFile):
    audio = MP3(file.file, ID3=EasyID3)
    if not audio.tags:
        # there are no metadata tags in the file
        raise NoMetaDataError(NO_METADATA_ERROR)

    metadata_response = MetadataResponse(
        title=audio.get('title', [None])[0],
        artist=audio.get('artist', [None])[0],
        album=audio.get('album', [None])[0],
        genre=audio.get('genre', [None])[0],
        date=audio.get('date', [None])[0]
    )
    return metadata_response
