from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Any



class PooledResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")
    class ResponseOutput(BaseModel):
        class ResponseOutputContent(BaseModel):
            type: str
            text: str
        id: Optional[str] = None
        type: Optional[str] = None    
        status: Optional[str] = None
        content: Optional[List[ResponseOutputContent]] = []
    id: str
    status: str
    reasoning: Optional[Any] = None
    output: List[ResponseOutput] = []
    
    

