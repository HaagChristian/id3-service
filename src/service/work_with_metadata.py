from fastapi import UploadFile
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.myapi.metadata_model import MetadataResponse, MetadataToChange
from src.settings.error_messages import NO_METADATA_ERROR


def extract_metadata_from_mp3_file(file: UploadFile) -> MetadataResponse:
    audio = MP3(file.file, ID3=EasyID3)
    if not audio.tags:
        # there are no metadata tags in the file
        raise NoMetaDataError(NO_METADATA_ERROR)

    artist_list: list = audio.get('artist', [None])
    if artist_list:
        split_list = artist_list[0].split(';')
    else:
        split_list = None

    metadata_response = MetadataResponse(
        title=audio.get('title', [None])[0],
        artists=split_list,
        album=audio.get('album', [None])[0],
        genre=audio.get('genre', [None])[0],
        date=audio.get('date', [None])[0],
        duration=audio.info.length
    )
    return metadata_response


def update_metadata_from_file(file: UploadFile, metadata: MetadataToChange) -> UploadFile:
    audio = MP3(file.file, ID3=EasyID3)

    if metadata.title:
        audio['title'] = metadata.title
    if metadata.artists:
        audio['artist'] = metadata.artists
    if metadata.album:
        audio['album'] = metadata.album
    if metadata.genre:
        audio['genre'] = metadata.genre
    if metadata.date:
        audio['date'] = metadata.date
    audio.save()

    return file
