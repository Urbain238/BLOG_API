from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    
    # On enlève la limite (255) pour éviter les erreurs si un titre est long
    titre = Column(Text, nullable=False) 
    
    # Contenu reste en Text : Indispensable pour stocker le Base64 des images téléversées
    contenu = Column(Text, nullable=False)
    
    categorie = Column(String(100))
    auteur = Column(String(100))
    
    # On passe tags en String ou Text sans limite pour plus de souplesse
    tags = Column(Text)
    
    # Ton choix du ARRAY est parfait pour Vercel Postgres
    images_urls = Column(ARRAY(String), default=[])
