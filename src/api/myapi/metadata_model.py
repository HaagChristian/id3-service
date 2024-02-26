import json
from typing import Optional, List

from pydantic import BaseModel, model_validator


class MetadataResponse(BaseModel):
    title: Optional[str] = None
    artists: Optional[List[str]] = None
    album: Optional[str] = None
    genre: Optional[str] = None
    date: Optional[str] = None
    duration: Optional[float] = None
    failed_tags: list = []

    # check if any of the fields are None
    # if so add the field name to the failed_tags list
    def __init__(self, **data):
        super().__init__(**data)
        for field_name, field_value in self:
            if field_value is None:
                self.failed_tags.append(field_name)


class MetadataToChangeInput(BaseModel):
    artist: Optional[str] = None
    genre: Optional[str] = None
    album: Optional[str] = None
    title: Optional[str] = None
    date: Optional[str] = None

    # map input data (json string) to the model
    # None type is mapped to 'None' string
    # this mapping is necessary because the input data is a json string --> accepting file and json data
    @model_validator(mode='before')
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
