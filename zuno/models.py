from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ComparisonWeights(BaseModel):
    """User-defined weights for product ranking."""
    price: float = 0.5
    rating: float = 0.5

class AgentRequest(BaseModel):
    """The request model sent from the frontend to the MCP server."""
    query: str
    image_data: Optional[str] = None  # Base64 encoded image
    weights: ComparisonWeights

class Product(BaseModel):
    """A structured model for a single product."""
    title: str
    price: Optional[float] = None
    rating: Optional[float] = None
    reviews: Optional[int] = None
    source: str
    link: str
    thumbnail: Optional[str] = None
    score: Optional[float] = 0.0 # Our calculated ranking score

class MediaResult(BaseModel):
    """A structured model for image or video results."""
    title: str
    link: str
    thumbnail: str

class AgentResponse(BaseModel):
    """The response model sent from the server back to the frontend."""
    summary: str
    ranked_products: List[Product] = []
    image_results: List[MediaResult] = []
    video_results: List[MediaResult] = []
    lens_results: List[MediaResult] = []