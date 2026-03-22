******************************************************************************************************************************************
# INTRODUCTION
******************************************************************************************************************************************
À l'ère de la numérisation croissante et de la diffusion instantanée de l'information, la création de contenu web nécessite des outils à la fois robustes, agiles et profondément centrés sur l'expérience utilisateur. Si l'écosystème du développement web foisonne aujourd'hui de frameworks complexes, une problématique d'ingénierie fondamentale persiste : **comment concevoir une application web complète, réactive et performante tout en maîtrisant la complexité et en s'appuyant sur les technologies natives ?**

C'est dans cette perspective que s'inscrit le projet **Matrice Blog**. Ce travail présente la conception, l'architecture et l'implémentation d'une plateforme Full-Stack de publication d'articles entièrement autonome. L'objectif de ce projet est de démontrer la viabilité d'un écosystème découplé, garantissant une communication fluide entre une interface client asynchrone et un serveur de données centralisé.

Pour répondre à cette problématique, le projet a été structuré autour de deux axes architecturaux majeurs :

1. **Le Backend (API RESTful) :** Déployé via Vercel, il constitue le moteur logique de l'application. Conçu pour être léger et hautement disponible, il expose une série d'endpoints permettant de gérer de manière sécurisée les opérations de création, lecture, mise à jour et suppression (CRUD) des ressources (articles, métadonnées, images).
2. **Le Frontend (Interface Utilisateur) :** Développée selon le paradigme des *Single Page Applications* (SPA) en utilisant exclusivement HTML, CSS et Vanilla JavaScript. L'interface s'affranchit des rechargements de page classiques en consommant l'API via des requêtes asynchrones (`fetch`). Elle intègre des fonctionnalités avancées telles qu'un moteur de recherche en temps réel, la gestion dynamique et conditionnelle des médias (extraction de données Base64 et URLs vers un carrousel interactif), ainsi qu'une adaptation thématique (Mode Sombre/Clair) pour l'ergonomie de lecture.

Ce dépôt documente l'ensemble de cette architecture logicielle, les choix techniques adoptés, ainsi que les instructions nécessaires au déploiement et à la prise en main de cet environnement.
