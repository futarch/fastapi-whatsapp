from typing import List, Optional  
from pydantic import BaseModel, Field   


class Profile(BaseModel):  
    name: str  

class Contact(BaseModel):  
    profile: Profile  
    wa_id: str  

class Text(BaseModel):  
    body: str

class Audio(BaseModel):  
    mime_type: str  
    sha256: str  
    id: str  
    voice: bool  

class Message(BaseModel):  
    from_: str = Field(..., alias="from")  
    id: str  
    timestamp: str  
    text: Text | None = None  
    audio: Audio | None = None  
    type: str

class Metadata(BaseModel):  
    display_phone_number: str  
    phone_number_id: str

class Value(BaseModel):  
    messaging_product: str  
    metadata: Metadata  
    contacts: List[Contact] | None = None  
    messages: List[Message] | None = None  

class Change(BaseModel):  
    value: Value  
    field: str  
    statuses: List[dict] | None = None  

class Entry(BaseModel):  
    id: str  
    changes: List[Change]  

class Payload(BaseModel):  
    object: str  
    entry: List[Entry]

class User(BaseModel):  
    id: int  
    first_name: str  
    last_name: str  
    phone: str

class UserMessage(BaseModel):  
    user: User  
    message: str | None = None  
    audio: Audio | None = None