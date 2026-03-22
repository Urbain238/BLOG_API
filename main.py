from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
import models, shemas
from database import engine, sessionLocal 
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. ROUTES DE RECHERCHE ET FILTRE (DOIVENT ÊTRE EN HAUT) ---

@app.get("/articles/search")
def search_article(query: str, db: Session = Depends(get_db)):
    # Utilisation de .ilike pour une recherche insensible à la casse
    return db.query(models.Article).filter(
        (models.Article.titre.contains(query)) | 
        (models.Article.contenu.contains(query))
    ).all()

@app.get("/articles/filter") # Corrigé /article -> /articles
def filter_articles(categorie: str, db: Session = Depends(get_db)):
    return db.query(models.Article).filter(models.Article.categorie == categorie).all()

# --- 2. ROUTES STANDARDS ---

@app.post("/articles", response_model=shemas.ArticleReponse)
def create_article(article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    new_article = models.Article(**article.dict())
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

@app.get("/articles", response_model=list[shemas.ArticleReponse])
def get_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).all()

# --- 3. ROUTES AVEC ID (À LA FIN) ---

@app.get("/articles/{id}", response_model=shemas.ArticleReponse)
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first() # .filter corrigé
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé") # raise sur une ligne
    return article
    
@app.put("/articles/{id}")
def update_article(id: int, article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    for key, value in article.dict().items():
        setattr(db_article, key, value)
    
    db.commit() # Commit après la boucle
    db.refresh(db_article)
    return {"message": "Article modifié"}

@app.delete("/articles/{id}") # "artilces" corrigé en "articles"
def delete_article(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db.delete(article) # Ajout de la suppression effective
    db.commit()
    return {"message": "Article supprimé"}
