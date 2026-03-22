******************************************************************************************************************************************
# INTRODUCTION
******************************************************************************************************************************************

Ce dépôt contient le code source et la documentation de mon projet réalisé dans le cadre de mo Travaux Pratiques de d'une API. L'objectif principal de ce TP était de concevoir, développer et déployer une API complète (Full-Stack optionelle) dédiée à la gestion et à la publication d'articles.

Il était question de mettre en pratique l'architecture client-serveur en créant une **Single Page Application** capable de communiquer de manière asynchrone avec une **API REST**. 

Les défis techniques à relever incluaient :
* La mise en place d'un système CRUD (Création, Lecture, Modification, Suppression) complet.
* La gestion asynchrone des données sans rechargement de la page.
* La conception d'une interface utilisateur fluide, responsive et ergonomique (incluant un mode sombre/clair et un carrousel d'images) - optionelle.

## 2. Méthodologie et Outils Utilisés

Pour répondre à ces exigences et garder un contrôle total sur la logique de l'application, j'ai opté pour des technologies natives couplées à des outils modernes de déploiement :

### 🖥️ Côté Client (Frontend)
* **HTML5 / CSS3 :** Structuration sémantique et design responsive sous forme de grille (CSS Grid/Flexbox) avec un système de fenêtres modales personnalisées.
* **JavaScript:** Toute la logique applicative a été codée en JS natif (sans framework comme React ou Vue), afin de consolider la manipulation du DOM et la gestion des événements.
* **Fetch API :** Utilisation des promesses (`async/await`) pour consommer les données de l'API.

### ⚙️ Côté Serveur (Backend)
* **API RESTful :** Une architecture basée sur des routes HTTP (`GET`, `POST`, `PUT`, `DELETE`) pour manipuler la ressource "articles".
* **Déploiement (Vercel) :** L'API et le système de persistance des données ont été hébergés sur Vercel (`https://blog-api-ultime-version.vercel.app/articles`), garantissant une disponibilité continue pour le frontend.
* **Framework utilisisé :** FastAPI en langage python
