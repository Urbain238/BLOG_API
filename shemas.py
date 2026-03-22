from pydantic import BaseModel
from typing import Optional, List

class ArticleCreate(BaseModel):
    titre: str
    contenu: str
    auteur: Optional[str] = None
    categorie: Optional[str] = None
    tags: Optional[str] = None
    images_urls: Optional[List[str]] = []
class ArticleReponse(ArticleCreate):
    id: int
    model_config = {"from_attributes": True}
