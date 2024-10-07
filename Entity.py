from pydantic import BaseModel,validator

# Define the TextRequest model with validators
class TextRequest(BaseModel):
    text: str
    max_tokens: int
    temperature: float
    presence_penalty: float

    @validator("text")
    def check_valid_text(cls, v):
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Text must be a non-empty string.")
        if len(v)<220:
            raise ValueError("Text Length Must be gretaer than 220.")
        return v

    @validator("max_tokens")
    def check_max_tokens(cls, v):
        if not isinstance(v, int):
            raise ValueError("max_tokens must be an integer.")
        if v < 10 or v > 400:
            raise ValueError("max_tokens must be between 10 and 400.")
        return v

    @validator("temperature")
    def check_temperature(cls, v):
        if not isinstance(v, float):
            raise ValueError("temperature must be a float.")
        if v < 0 or v > 1:
            raise ValueError("temperature must be between 0 and 1.")
        return v

    @validator("presence_penalty")
    def check_presence_penalty(cls, v):
        if not isinstance(v, float):
            raise ValueError("presence_penalty must be a float.")
        if v < 0 or v > 1:
            raise ValueError("presence_penalty must be between 0 and 1.")
        return v

class Meta(BaseModel):
    model :str
    total_tokens:int
#define the response model 
class ResponseModel(BaseModel):
    summary:str
    meta:Meta