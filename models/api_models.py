from pydantic import BaseModel



class PooledResponse(BaseModel):
    class ResponseOutput(BaseModel):
        class ResponseOutputContent(BaseModel):
            type: str
            text: str
        id: str
        type: str
        status: str
        content: list[ResponseOutputContent]
    id: str
    output: list[ResponseOutput]
    status: str

