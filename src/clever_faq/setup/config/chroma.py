from pydantic import BaseModel, Field


class ChromaDBConfig(BaseModel):
    max_chunk_size: int = 512
    chunk_overlap: int = 50
    host: str = Field(..., alias="CHROMA_SERVER_HTTP_HOST")
    port: int = Field(..., alias="CHROMA_SERVER_HTTP_PORT")
