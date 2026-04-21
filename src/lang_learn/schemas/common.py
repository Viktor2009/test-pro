"""Общие типы и ограничения для DTO."""

from typing import Annotated

from pydantic import Field, StringConstraints

# BCP 47 / ISO-подобный код языка, например "en-US", "de-DE".
LanguageCode = Annotated[
    str,
    StringConstraints(min_length=2, max_length=32, strip_whitespace=True),
]

# Идентификатор сущности в хранилище (UUID или slug).
EntityId = Annotated[str, Field(min_length=1, max_length=128)]
