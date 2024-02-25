import logging
import tempfile
from typing import Tuple

from fastapi import UploadFile
from mutagen import MutagenError
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3

from src.api.middleware.cleanup import cleanup
from src.api.middleware.custom_exceptions.MissingFileName import MissingFileNameError
from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.api.myapi.metadata_model import MetadataResponse, MetadataToChangeInput
from src.settings.error_messages import NO_METADATA_ERROR, MISSING_FILENAME


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


def update_metadata_from_file(file: UploadFile, metadata: MetadataToChangeInput) -> Tuple[str, tempfile.TemporaryFile]:
    """
    Input file (file) needs to be written to a temporary file in order to be able to update the metadata.
    This is because the file is a stream and cannot be updated directly.
    The audio file is read again from the temporary file to update the original file.

    The temporary file needs to be delete = False, because otherwise the audio object could not
    read the temporary file (PermissionError).

    :param file: MP3 file
    :param metadata: MetadataToChangeInput
    :return: UploadFile

    :raises:
    FileNotFoundError: mp3 file not found
    MutagenError: general error while updating the metadata
    """
    try:
        if not file.filename:
            raise MissingFileNameError(MISSING_FILENAME)

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(file.file.read())

            audio = MP3(temp_file_path, ID3=EasyID3)

            if 'None' not in metadata.title:
                audio['title'] = metadata.title
            if 'None' not in metadata.artist:
                audio['artist'] = metadata.artist
            if 'None' not in metadata.album:
                audio['album'] = metadata.album
            if 'None' not in metadata.genre:
                audio['genre'] = metadata.genre
            if 'None' not in metadata.date:
                audio['date'] = metadata.date

            audio.save()
            with open(temp_file_path, 'rb') as updated_file:
                updated_content = updated_file.read()

            file.file.seek(0)

            # Update the content of the original file with the updated content
            file.file.write(updated_content)

            file.file.seek(0)
            if not audio.filename:
                # file.filename is invalid
                raise MissingFileNameError(MISSING_FILENAME)
            return temp_file_path, temp_file
    except (FileNotFoundError, MutagenError) as e:
        try:
            cleanup(temp_file_path=temp_file_path, temp_file=temp_file)
        except (FileNotFoundError, PermissionError, OSError) as e:
            logging.error('Could not close temporary file.')
            pass
        raise e
