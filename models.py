from sqlalchemy import Column, Integer, String
from database import Base 

class Article(Base):
    __tablename__ = "articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    titre = Column(String(255), nullable=False)
    contenu = Column(String(1000))
    categorie = Column(String(100))
    auteur = Column(String(100))
    tags = Column(String(255))
    
