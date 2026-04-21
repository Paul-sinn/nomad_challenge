from pydantic import BaseModel

class UserAccountContext(BaseModel):


    customer_id: int
    name:str
    email: str
    tier: str = "basic" # premium entreprise

class InputGuardRailOutput (BaseModel):

    is_off_topic: bool
    reason : str

class TechOutputGuardRailOutput(BaseModel):
    contains_off_topic:bool
    contains_billing_data:bool
    contains_order_data:bool
    contains_account_data:bool

    reason:str
    
class AccountOutputGuardRailOutput(BaseModel):
    contains_off_topic:bool
    contains_billing_data:bool
    contains_order_data:bool
    contains_technical_data:bool

    reason:str

class BillOutputGuardRailOutput(BaseModel):
    contains_off_topic:bool
    contains_technical_data:bool
    contains_order_data:bool
    contains_account_data:bool

    reason:str

class OrderOutputGuardRailOutput(BaseModel):
    contains_off_topic:bool
    contains_technical_data:bool
    contains_billing_data:bool
    contains_account_data:bool

    reason:str

class HandoffData (BaseModel):

    to_agent_name:str
    reason: str
    description:str
    issue_type:str