******************************************************************************************************************************************
# INTRODUCTION
******************************************************************************************************************************************

Ce dépôt contient le code source et la documentation de mon projet réalisé dans le cadre de mon Travaux Pratiques de développement web. L'objectif principal de ce TP était de concevoir, développer et déployer une API complète (Full-Stack - optionelle) dédiée à la gestion et à la publication d'articles.

Il était question de mettre en pratique l'architecture client-serveur **(optionelle)** en créant une **Single Page Application** capable de communiquer de manière asynchrone avec une **API REST**. 

Les défis techniques à relever incluaient :
* La mise en place d'un système CRUD (Création, Lecture, Modification, Suppression) complet.
* La gestion asynchrone des données sans rechargement de la page.
* Le traitement avancé des médias.
* La conception d'une interface utilisateur fluide, responsive et ergonomique (incluant un mode sombre/clair - optionelle).

## Méthodologie et Outils Utilisés

Pour répondre à ces exigences et garder un contrôle total sur la logique de l'application, j'ai opté pour des technologies natives pour l'interface, couplées à un backend robuste en Python :

* **Côté Client (Frontend) :** HTML5, CSS3, et Vanilla JavaScript (Fetch API, manipulation du DOM).
* **Côté Serveur (Backend) :** Python avec le framework FastAPI.
* **Base de données :** PostgreSQL manipulée via l'ORM SQLAlchemy.

---

## 1. Côté Serveur : API RESTful avec FastAPI & PostgreSQL

Pour gérer la logique métier et la persistance des données, le backend a été développé en **Python** avec le framework **FastAPI**. Ce choix a été motivé par sa rapidité, sa génération automatique de documentation (Swagger) et sa validation des données via **Pydantic**. 

La persistance des données est assurée par une base de données **PostgreSQL**, manipulée via l'ORM (Object-Relational Mapping) **SQLAlchemy**.

Voici le détail de l'architecture backend, étape par étape :

###  1.1. Connexion à la Base de Données (`database.py`)
L'application utilise SQLAlchemy pour se connecter à la base de données PostgreSQL. Une session de base de données (`SessionLocal`) est créée pour chaque requête, garantissant que les transactions sont gérées de manière isolée et sécurisée.

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# URL de connexion à la base de données PostgreSQL
SQLALCHEMY_DATABASE_URL = "postgresql://user:password@host/dbname"

# Création du moteur de base de données
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Création d'une session locale pour interagir avec la DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Classe de base pour la création des modèles
Base = declarative_base()

# Dépendance pour obtenir la session de DB dans les routes
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 1.2. Modélisation des Données (`models.py`)
Le modèle de données représente la structure exacte de la table `articles` dans PostgreSQL. 
*Point technique important :* Nous utilisons le type `ARRAY` spécifique au dialecte PostgreSQL pour stocker la liste des URLs d'images directement, et le type `Text` (sans limite de caractères) pour pouvoir stocker les lourdes chaînes Base64 des images téléversées.

```python
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
from database import Base

class Article(Base):
    __tablename__ = "articles"

    id = Column(Integer, primary_key=True, index=True)
    titre = Column(Text, nullable=False)
    contenu = Column(Text, nullable=False) # Type Text pour supporter le Base64
    categorie = Column(String(100))
    auteur = Column(String(100))
    tags = Column(Text)
    images_urls = Column(ARRAY(String), default=[]) # Tableau natif PostgreSQL
```

### 1.3. Validation des Données (`schemas.py`)
Avant même d'atteindre la base de données, FastAPI valide les requêtes du frontend grâce à **Pydantic**. Si un champ obligatoire manque, l'API renvoie automatiquement une erreur 422 (Unprocessable Entity).

```python
from pydantic import BaseModel
from typing import List, Optional

class ArticleCreate(BaseModel):
    titre: str
    auteur: Optional[str] = "Inconnu"
    categorie: Optional[str] = "Général"
    contenu: str
    tags: Optional[str] = None
    images_urls: Optional[List[str]] = []
```

### 1.4. Les Routes de l'API (Opérations CRUD)

Le fichier principal (`main.py`) expose les différents endpoints (routes) permettant au Frontend d'interagir avec la base de données via la session SQLAlchemy (`db`).

#### A. Lecture des Articles (GET)
Récupère tous les articles stockés. L'ORM traduit la requête en `SELECT * FROM articles`.

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas

@app.get("/articles", response_model=List[schemas.ArticleCreate])
def read_articles(db: Session = Depends(get_db)):
    # Récupération de tous les articles
    articles = db.query(models.Article).all()
    return articles
```

#### B. Ajout d'un Article (POST)
Prend les données validées par Pydantic, crée une instance du modèle SQLAlchemy, l'ajoute à la session, valide la transaction (`commit`) et rafraîchit l'objet pour obtenir son `id` généré.

```python
@app.post("/articles", response_model=schemas.ArticleCreate)
def create_article(article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    # Conversion du schéma Pydantic en modèle SQLAlchemy
    db_article = models.Article(**article.dict())
    
    db.add(db_article)
    db.commit()          # Sauvegarde dans la base
    db.refresh(db_article) # Récupération de l'ID généré
    
    return db_article
```

#### C. Modification d'un Article (PUT)
Recherche l'article par son ID. S'il existe, ses attributs sont mis à jour avec les nouvelles valeurs fournies par le client.

```python
@app.put("/articles/{article_id}")
def update_article(article_id: int, article: schemas.ArticleCreate, db: Session = Depends(get_db)):
    # Recherche de l'article dans la DB
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Mise à jour des champs
    for key, value in article.dict().items():
        setattr(db_article, key, value)
        
    db.commit()
    db.refresh(db_article)
    return db_article
```

#### D. Suppression d'un Article (DELETE)
Supprime définitivement un article de la base de données.

```python
@app.delete("/articles/{article_id}")
def delete_article(article_id: int, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == article_id).first()
    
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
        
    db.delete(db_article)
    db.commit()
    return {"message": "Article supprimé avec succès"}
```

#### E. Moteur de Recherche (GET)
Permet de filtrer les articles côté serveur en utilisant l'opérateur `ilike` de SQLAlchemy (recherche insensible à la casse) sur le titre ou le contenu.

```python
@app.get("/articles/search")
def search_articles(query: str, db: Session = Depends(get_db)):
    # Recherche 'LIKE %query%' sur le titre ou le contenu
    resultats = db.query(models.Article).filter(
        (models.Article.titre.ilike(f"%{query}%")) | 
        (models.Article.contenu.ilike(f"%{query}%"))
    ).all()
    
    return resultats
```
