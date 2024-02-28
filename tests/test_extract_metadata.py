from mutagen.mp3 import HeaderNotFoundError

from mutagen.mp3 import HeaderNotFoundError

from src.api.middleware.custom_exceptions.NoMetadataError import NoMetaDataError
from src.service.work_with_metadata import extract_metadata_from_mp3_file
from src.settings.error_messages import NO_METADATA_ERROR


def test_with_no_metadata(create_upload_file):
    content = b'\x00'
    filename = 'file_without_metadata.mp3'
    upload_file = create_upload_file(content, filename)
    try:
        extract_metadata_from_mp3_file(upload_file)
        assert False, "HeaderNotFoundError exception was not raised."
    except HeaderNotFoundError as e:
        assert type(e) == HeaderNotFoundError
        assert e.args[0] == "can't sync to MPEG frame"


def test_extract_metadata_with_metadata(create_upload_file):
    with open("tests/resources/HORST WESSEL LIED (DIE FAHNE HOCH - GROSSES BLAS ORCHESTER.mp3", "rb") as file:
        content = file.read()
        upload_file = create_upload_file(content, "HORST WESSEL LIED (DIE FAHNE HOCH - GROSSES BLAS ORCHESTER.mp3")

        res = extract_metadata_from_mp3_file(upload_file)
        assert res.title == 'HORST WESSEL LIED (DIE FAHNE HOCH)'
        assert res.artists == ['GROSSES BLAS ORCHESTER', 'CHOR SA STURM 33']
        assert res.album == 'HORST WESSEL LIED (DIE FAHNE HOCH)'
        assert res.date is None
        assert res.genre == 'Popular Music'


def test_extract_metadata_with_metadata_and_date(create_upload_file):
    with open("tests/resources/Seligkeit mit Jahr.mp3", "rb") as file:
        content = file.read()
        upload_file = create_upload_file(content, "Seligkeit mit Jahr.mp3")

        res = extract_metadata_from_mp3_file(upload_file)
        assert res.title is None
        assert res.artists is None
        assert res.album is None
        assert res.date == 2022
        assert res.genre == 'Blues'
        assert res.failed_tags == ['title', 'artists', 'album']


def test_extract_metadata_with_no_metadata(create_upload_file):
    with open("tests/resources/Seligkeit.mp3", "rb") as file:
        content = file.read()
        upload_file = create_upload_file(content, "Seligkeit.mp3")

        try:
            res = extract_metadata_from_mp3_file(upload_file)
            assert False, "NoMetaDataError exception was not raised."
        except NoMetaDataError as e:
            assert type(e) == NoMetaDataError
            assert e.args[0] == NO_METADATA_ERROR
