from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware
import models, shemas # On garde ton orthographe "shemas"
from database import engine, sessionLocal 

app = FastAPI(title="Urban Blog API")

# --- CONFIGURATION CORS (CORRIGÉE) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=False, # Impératif pour éviter le "Serveur injoignable"
    allow_methods=["*"],
    allow_headers=["*"],
)

# Création automatique des tables
models.Base.metadata.create_all(bind=engine)

# Dépendance pour la base de données
def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. ROUTES DE RECHERCHE ---

@app.get("/articles/search")
def search_article(query: str, db: Session = Depends(get_db)):
    """Recherche des articles par titre ou contenu (insensible à la casse)"""
    return db.query(models.Article).filter(
        (models.Article.titre.ilike(f"%{query}%")) | 
        (models.Article.contenu.ilike(f"%{query}%"))
    ).all()

# --- 2. ROUTES STANDARDS (CRUD) ---

@app.get("/articles", response_model=list[shemas.ArticleReponse])
def get_articles(db: Session = Depends(get_db)):
    """Récupère tous les articles"""
    return db.query(models.Article).all()

@app.post("/articles", response_model=shemas.ArticleReponse)
def create_article(article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    """Crée un nouvel article avec le support images_urls"""
    # model_dump() extrait les données du schéma (incluant images_urls s'il est présent)
    new_article = models.Article(**article.model_dump())
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

# --- 3. ROUTES AVEC ID (PLOTS EN DERNIER) ---

@app.get("/articles/{id}", response_model=shemas.ArticleReponse)
def get_article(id: int, db: Session = Depends(get_db)):
    """Récupère un article spécifique"""
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article

@app.put("/articles/{id}")
def update_article(id: int, article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    """Met à jour un article"""
    db_article = db.query(models.Article).filter(models.Article.id == id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # Mise à jour dynamique des champs (titre, contenu, auteur, images_urls, etc.)
    update_data = article.model_dump()
    for key, value in update_data.items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return {"message": "Article modifié avec succès", "id": id}

@app.delete("/articles/{id}")
def delete_article(id: int, db: Session = Depends(get_db)):
    """Supprime un article"""
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db.delete(article)
    db.commit()
    return {"message": "Article supprimé"}
