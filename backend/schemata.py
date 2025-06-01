from pydantic import BaseModel, Base64Bytes


class CreateDocument(BaseModel):
    file_name: str
    bytes: Base64Bytes

    class Config:
        from_attributes = True


class Document(BaseModel):
    id: int
    file_name: str
    bytes: Base64Bytes

    class Config:
        from_attributes = True
