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
## 2. Côté Client (Frontend) : Interface Dynamique en Vanilla JS

L'interface utilisateur a été conçue comme une **Single Page Application (SPA)**. Pour garantir une application légère et consolider la compréhension des fondamentaux du web, aucun framework frontend (comme React ou Vue) n'a été utilisé. Toute la logique repose sur **HTML5, CSS3 et Vanilla JavaScript**.

Le frontend gère l'affichage asynchrone des données, l'interaction utilisateur via des fenêtres modales, et un traitement complexe des médias (images locales en Base64 et liens externes).

Voici le détail des implémentations techniques majeures :

### 🔗 2.1. Communication avec l'API (Fetch API)
L'application communique avec le backend FastAPI en utilisant l'API `fetch` native avec la syntaxe moderne `async/await`. 

**Exemple : Chargement initial des articles (`GET`)**
La fonction `load()` interroge le serveur et met à jour le DOM en cas de succès, ou affiche un message d'erreur si le serveur est injoignable.

```javascript
const API_BASE_URL = '[https://blog-api-ultime-version.vercel.app](https://blog-api-ultime-version.vercel.app)';
const API = `${API_BASE_URL}/articles`;

let store = []; // Stockage local des articles pour éviter les requêtes redondantes

async function load() {
    try {
        const response = await fetch(API);
        if (!response.ok) throw new Error("Erreur de réponse serveur");
        
        store = await response.json();
        render(store); // Appel de la fonction de rafraîchissement de l'interface
    } catch (erreur) {
        console.error("Erreur de chargement:", erreur);
        document.getElementById('mainGrid').innerHTML = "<p>Le serveur n'est pas joignable.</p>";
    }
}
```

### 2.2. Rendu Dynamique et Manipulation du DOM
La fonction `render(data)` prend le tableau d'articles et génère dynamiquement des cartes HTML (Cards) en injectant les données via des *Template Literals* (littéraux de gabarits). 

Pour garder des cartes propres, une logique d'extraction de texte (Retrait des balises HTML) et de limitation de caractères (Substring) est appliquée au contenu.

```javascript
function render(data) {
    const grille = document.getElementById('mainGrid');
    
    grille.innerHTML = data.slice().reverse().map(article => {
        // Nettoyage du contenu HTML pour générer l'extrait de texte
        const texteBrut = article.contenu ? article.contenu.replace(/<[^>]*>?/gm, '') : '';
        const extrait = texteBrut.substring(0, 100) + (texteBrut.length > 100 ? '...' : '');

        return `
        <div class="card">
            <h3 class="card-title">${article.titre}</h3>
            <p class="card-text">${extrait}</p>
            <button onclick="openView(${article.id})">Lire l'article</button>
        </div>`;
    }).join('');
}
```

### 2.3. Gestion Avancée des Images (Base64 et Carrousel)
L'un des défis majeurs de ce TP a été la gestion des images. L'utilisateur peut soit renseigner des URLs, soit uploader une image depuis son appareil (convertie en **Base64** par un `FileReader`).

**A. Conversion des fichiers locaux en Base64 :**
```javascript
function insertImage() {
    const imgFile = document.getElementById('imgFile').files[0];
    const contenu = document.getElementById('contenu');

    if (imgFile) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const base64 = e.target.result;
            // Injection de la balise image directement dans le contenu HTML
            contenu.value += `\n<img src="${base64}" alt="Image locale"/>\n`;
        };
        reader.readAsDataURL(imgFile);
    }
}
```

**B. Génération de la miniature et du carrousel intelligent :**
Lors de l'affichage d'un article, un algorithme fouille le contenu HTML pour en extraire les balises `<img>` générées précédemment, et les combine avec les URLs du carrousel pour créer une galerie unifiée.

```javascript
// Extraction dynamique des images cachées dans le contenu pour le carrousel
const tempDiv = document.createElement('div');
tempDiv.innerHTML = article.contenu;
const imagesInContent = tempDiv.querySelectorAll('img');

let allImages = article.images_urls ? [...article.images_urls] : [];

// Fusion des images du contenu avec celles de l'entête
imagesInContent.forEach(img => {
    if (!allImages.includes(img.src)) {
        allImages.push(img.src);
    }
});
```

### 2.4. Création et Mise à Jour (Opérations de Sauvegarde)
La fonction `save()` est intelligente : elle vérifie si le champ caché `artId` est rempli. S'il y a un ID, elle effectue une requête `PUT` (modification). Sinon, elle fait un `POST` (création).

```javascript
async function save() {
    const id = document.getElementById('artId').value;
    const body = {
        titre: document.getElementById('titre').value,
        contenu: document.getElementById('contenu').value,
        // ... autres champs
    };

    const urlFinal = id ? `${API}/${id}` : API;
    const methodFinal = id ? 'PUT' : 'POST';

    const res = await fetch(urlFinal, {
        method: methodFinal,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });

    if (res.ok) {
        closeModal();
        load(); // Rafraîchissement automatique de la grille
    }
}
```

### 2.5. Expérience Utilisateur (UX) : Mode Sombre
Un script gère le basculement entre le mode clair et le mode sombre en ajoutant ou retirant une classe `dark-mode` sur la balise `<body>`. Les couleurs sont gérées par des variables CSS (`--bg-color`, `--text-color`).

```javascript
function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    // Changement de l'icône du bouton
    document.getElementById('tBtn').innerHTML = isDark ? '<i class="fas fa-sun"></i>' : '<i class="fas fa-moon"></i>';
}
```

# CONCLUSION

Ce projet de développement a été une excellente opportunité de consolider mes compétences en architecture Full-Stack. En faisant le choix délibéré de ne pas utiliser de framework frontend lourd (comme React ou Angular), j'ai pu démystifier le fonctionnement interne d'une **Single Page Application (SPA)**, maîtriser la manipulation avancée du DOM en Vanilla JavaScript, et comprendre en profondeur les mécanismes de communication asynchrone client-serveur via l'API Fetch.

Du côté serveur, l'utilisation de **Python avec FastAPI et SQLAlchemy** s'est révélée être un choix particulièrement efficace. Ce stack technologique m'a permis de concevoir une API robuste, fortement typée et sécurisée, tout en simplifiant les interactions complexes avec la base de données PostgreSQL.

Bien que la plateforme soit aujourd'hui pleinement fonctionnelle et réponde aux exigences initiales du TP, plusieurs améliorations pourraient être envisagées pour faire évoluer ce projet vers une application de niveau production :

* ** Éditeur de Texte Riche (WYSIWYG) :** Remplacer le simple champ `textarea` par un éditeur complet (type Quill ou TinyMCE) pour faciliter la mise en page des articles sans avoir à taper des balises HTML à la main.
* ** Pagination Côté Serveur :** Actuellement, le frontend charge l'intégralité des articles au démarrage. Implémenter une pagination (avec `limit` et `offset`) allégerait la charge réseau et améliorerait les performances si le blog venait à contenir des centaines d'articles.
* ** Système de Commentaires :** Ajouter une table relationnelle dans la base de données pour permettre aux lecteurs de réagir sous chaque article.

### **Merci d'avoir pris le temps de parcourir ce compte-rendu et d'explorer le code source de ce projet !**

## 🚀 Démo en Ligne et Liens Utiles

Le projet est entièrement déployé et accessible en direct. Vous pouvez interagir avec l'interface utilisateur ou tester directement les endpoints via la documentation interactive (Swagger UI) générée par FastAPI :

* 🌐 **Interface Web (Frontend sur Netlify) :** [https://api-project-blog.netlify.app](https://api-project-blog.netlify.app)
* ⚙️ **Documentation de l'API (Swagger UI) :** [https://blog-api-ultime-version-l485rwox5-urbain238s-projects.vercel.app/docs](https://blog-api-ultime-version-l485rwox5-urbain238s-projects.vercel.app/docs)

*(Note : L'API étant hébergée sur la version gratuite de Vercel, la première requête peut prendre quelques secondes le temps que le serveur sorte de son mode veille).*
