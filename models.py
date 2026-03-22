from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(String(255), nullable=False)
    contenu = Column(Text, nullable=False)
    categorie = Column(String(100))
    auteur = Column(String(100))
    tags = Column(Text)
    images_urls = Column(ARRAY(String), default=[])
