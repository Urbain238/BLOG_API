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

# Crée les tables si elles n'existent pas encore
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = sessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- 1. ROUTES DE RECHERCHE ET FILTRE ---

@app.get("/articles/search")
def search_article(query: str, db: Session = Depends(get_db)):
    # OPTIMISATION POSTGRES : .ilike(f"%{query}%") est la vraie méthode pour ignorer la casse
    return db.query(models.Article).filter(
        (models.Article.titre.ilike(f"%{query}%")) | 
        (models.Article.contenu.ilike(f"%{query}%"))
    ).all()

@app.get("/articles/filter")
def filter_articles(categorie: str, db: Session = Depends(get_db)):
    return db.query(models.Article).filter(models.Article.categorie == categorie).all()

# --- 2. ROUTES STANDARDS ---

@app.post("/articles", response_model=shemas.ArticleReponse)
def create_article(article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    # OPTIMISATION PYDANTIC V2 : model_dump() remplace dict()
    new_article = models.Article(**article.model_dump())
    db.add(new_article)
    db.commit()
    db.refresh(new_article)
    return new_article

@app.get("/articles", response_model=list[shemas.ArticleReponse])
def get_articles(db: Session = Depends(get_db)):
    return db.query(models.Article).all()

# --- 3. ROUTES AVEC ID ---

@app.get("/articles/{id}", response_model=shemas.ArticleReponse)
def get_article(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    return article
    
@app.put("/articles/{id}")
def update_article(id: int, article: shemas.ArticleCreate, db: Session = Depends(get_db)):
    db_article = db.query(models.Article).filter(models.Article.id == id).first()
    if not db_article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    # OPTIMISATION PYDANTIC V2 : model_dump() remplace dict()
    for key, value in article.model_dump().items():
        setattr(db_article, key, value)
    
    db.commit()
    db.refresh(db_article)
    return {"message": "Article modifié"}

@app.delete("/articles/{id}")
def delete_article(id: int, db: Session = Depends(get_db)):
    article = db.query(models.Article).filter(models.Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article non trouvé")
    
    db.delete(article)
    db.commit()
    return {"message": "Article supprimé"}
