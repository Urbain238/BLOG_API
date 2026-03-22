from pydantic import BaseModel
from typing import Optional

class ArticleCreate(BaseModel):
    titre: str
    contenu: str
    auteur: Optional[str] = None
    categorie: Optional[str] = None
    tags: Optional[str] = None

# J'ai mis "Reponse" sans le "s" pour que ça corresponde EXACTEMENT à ton main.py
class ArticleReponse(ArticleCreate):
    id: int
    
    # La nouvelle syntaxe obligatoire pour Pydantic V2 (remplace orm_mode=True)
    model_config = {"from_attributes": True}
