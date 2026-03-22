from pydantic import BaseModel

class ArticleCreate(BaseModel):
    titre: str
    contenu: str
    auteur: str
    categorie: str
    tags: str

class ArticleResponse(ArticleCreate):
    id: int
    
    class config:
        orm_mode = True
