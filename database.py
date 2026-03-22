import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# On récupère l'URL de connexion que Vercel a créée automatiquement
DATABASE_URL = os.getenv("POSTGRES_URL")

# Petite correction obligatoire : SQLAlchemy a besoin de "postgresql://" et non "postgres://"
if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Connexion à la base de données Neon sur Vercel
engine = create_engine(DATABASE_URL)

sessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
