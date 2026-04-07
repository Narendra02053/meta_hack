from pydantic import BaseModel
from typing import Dict, List, Optional, Any

class Observation(BaseModel):
    inventory: Dict[str, int]
    current_order: Optional[Dict[str, int]]
    current_deadline: Optional[int]
    priority: str
    returns_pending: List[str]
    inspection_pending: List[str]
    packed_orders: int
    shipped_orders: int
    time_left: int
    total_orders: int
    time_limit: int

class Action(BaseModel):
    action: str

class StepResponse(BaseModel):
    observation: Observation
    reward: float
    done: bool
    info: Dict[str, Any]
