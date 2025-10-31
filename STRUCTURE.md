# Structure du Projet Backend

## Vue d'ensemble

Le projet suit une architecture en couches avec une séparation claire des responsabilités:

```
/app/backend/
├── api/                    # Couche API (routes et endpoints)
├── clients/                # Clients externes (LLM, APIs tierces)
├── config/                 # Configuration et dépendances
├── entities/               # Modèles de données (Pydantic)
├── services/               # Logique métier
├── .env                    # Variables d'environnement
├── requirements.txt        # Dépendances Python
└── server.py              # Point d'entrée FastAPI
```

## Description des Dossiers

### 📁 `/api` - Couche API
**Responsabilité**: Définir les endpoints REST et gérer les requêtes HTTP

```
api/
├── __init__.py
└── routes.py              # Définition des routes API
```

**Contenu**:
- `routes.py`: Tous les endpoints de l'API
  - `GET /api/` - Health check
  - `POST /api/videos/generate` - Génération de scripts
  - `GET /api/videos/{id}` - Récupération d'une vidéo
  - `GET /api/videos` - Liste des vidéos

**Principe**: Les routes ne contiennent que la logique de routage. La logique métier est déléguée aux services.

---

### 📁 `/clients` - Clients Externes
**Responsabilité**: Communication avec les APIs externes (LLM, services tiers)

```
clients/
├── __init__.py
└── ai_client.py           # Client pour les modèles LLM
```

**Contenu**:
- `ai_client.py`: Client pour interagir avec les modèles AI (DeepSeek, OpenAI, etc.)
  - Gestion de l'authentification
  - Appels API aux LLMs
  - Gestion des erreurs réseau

**Principe**: Encapsule toute la logique de communication externe. Facilite le changement de fournisseur.

---

### 📁 `/config` - Configuration
**Responsabilité**: Configuration globale, connexions, et injection de dépendances

```
config/
├── __init__.py
├── database.py            # Connexion MongoDB
└── dependencies.py        # Injection de dépendances (singletons)
```

**Contenu**:
- `database.py`: Gestion de la connexion MongoDB
  - Instance unique de la base de données
  - Fermeture propre des connexions
- `dependencies.py`: Injection de dépendances
  - Singletons pour AI Client et services
  - Pattern Factory pour les services

**Principe**: Centralise la configuration et évite les dépendances circulaires.

---

### 📁 `/entities` - Modèles de Données
**Responsabilité**: Définition des modèles de données avec Pydantic

```
entities/
├── __init__.py
├── dialogue.py            # Modèles Dialogue et Role
├── requests.py            # Modèles de requêtes API
└── video.py              # Modèles Video
```

**Contenu**:
- `dialogue.py`: 
  - `Role` (Enum): YOUTUBER / CANDIDATE
  - `Dialogue`: Modèle complet avec video_id
  - `DialogueResponse`: Modèle pour les réponses API
- `video.py`:
  - `Video`: Modèle de base
  - `VideoWithDialogues`: Vidéo avec ses dialogues
- `requests.py`:
  - `GenerateVideoRequest`: Requête de génération

**Principe**: Modèles Pydantic pour la validation automatique et la sérialisation.

---

### 📁 `/services` - Logique Métier
**Responsabilité**: Orchestration de la logique métier

```
services/
├── __init__.py
├── script_generation_service.py   # Génération de scripts AI
└── video_service.py              # Gestion de la persistance
```

**Contenu**:
- `script_generation_service.py`:
  - Génération d'introduction
  - Génération de dialogues avec mémoire conversationnelle
  - Génération de conclusion
  - Orchestration complète de la génération
- `video_service.py`:
  - CRUD pour les vidéos
  - CRUD pour les dialogues
  - Récupération avec jointures

**Principe**: Les services contiennent la logique métier et orchestrent les appels aux clients et à la base de données.

---

## Flux de Données

### 1. Génération de Vidéo (POST /api/videos/generate)

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ POST /api/videos/generate
       ▼
┌─────────────────────────────────────────┐
│           api/routes.py                 │
│  - Validation des paramètres            │
│  - Appel aux services                   │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│  services/script_generation_service.py  │
│  - Génère introduction                  │
│  - Génère dialogues (avec mémoire)      │
│  - Génère conclusion                    │
└──────┬──────────────────────────────────┘
       │
       ├──────► ┌────────────────────────┐
       │        │  clients/ai_client.py  │
       │        │  - Appels API LLM      │
       │        └────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│     services/video_service.py           │
│  - Sauvegarde vidéo                     │
│  - Sauvegarde dialogues                 │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────────────────────────────────┐
│       config/database.py                │
│  - Insertion MongoDB                    │
└──────┬──────────────────────────────────┘
       │
       ▼
┌─────────────┐
│   MongoDB   │
└─────────────┘
```

### 2. Récupération de Vidéo (GET /api/videos/{id})

```
Client → routes.py → video_service.py → database.py → MongoDB
                                      ←               ←
                     VideoWithDialogues
```

## Principes de Design

### 1. Séparation des Responsabilités
- **API**: Routage et validation HTTP
- **Services**: Logique métier
- **Clients**: Communication externe
- **Entities**: Validation de données
- **Config**: Configuration globale

### 2. Injection de Dépendances
```python
# config/dependencies.py
def get_script_service() -> ScriptGenerationService:
    ai_client = get_ai_client()
    return ScriptGenerationService(ai_client)

# api/routes.py
script_service = get_script_service()
```

### 3. Single Responsibility
Chaque module a une seule raison de changer:
- `ai_client.py` change si l'API LLM change
- `video_service.py` change si la logique de persistance change
- `routes.py` change si les endpoints changent

### 4. Dependency Inversion
Les services dépendent d'abstractions (clients), pas d'implémentations:
```python
class ScriptGenerationService:
    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client  # Dépend de l'abstraction
```

## Avantages de cette Structure

### ✅ Testabilité
- Services testables indépendamment
- Clients mockables facilement
- Tests unitaires par couche

### ✅ Maintenabilité
- Code organisé par responsabilité
- Facile à localiser le code
- Modifications isolées

### ✅ Évolutivité
- Ajout de nouveaux endpoints facile
- Changement de base de données isolé
- Remplacement de LLM simplifié

### ✅ Lisibilité
- Structure claire et prévisible
- Nommage explicite
- Documentation intégrée

## Exemples d'Extension

### Ajouter un nouveau LLM Provider
```python
# clients/gemini_client.py
class GeminiClient:
    def generate_completion(self, messages, model):
        # Implémentation Gemini
        pass

# config/dependencies.py
def get_ai_client() -> AIClient:
    provider = os.environ.get('AI_PROVIDER', 'deepseek')
    if provider == 'gemini':
        return GeminiClient()
    return AIClient()
```

### Ajouter un nouveau Endpoint
```python
# api/routes.py
@api_router.get("/videos/{video_id}/dialogues")
async def get_video_dialogues(video_id: str):
    video_service = await get_video_service()
    return await video_service.get_dialogues(video_id)

# services/video_service.py
async def get_dialogues(self, video_id: str):
    dialogues = await self.db.dialogues.find({"video_id": video_id})
    return await dialogues.to_list(1000)
```

### Ajouter une nouvelle Entité
```python
# entities/audio.py
class Audio(BaseModel):
    id: str
    video_id: str
    audio_url: str
    duration: int
```

## Points d'Attention

### 🔴 À NE PAS FAIRE
- ❌ Mettre de la logique métier dans les routes
- ❌ Accéder directement à la base depuis les routes
- ❌ Hardcoder les configurations
- ❌ Créer des dépendances circulaires

### ✅ À FAIRE
- ✓ Garder les routes simples (validation + appel service)
- ✓ Centraliser la logique métier dans les services
- ✓ Utiliser les variables d'environnement
- ✓ Utiliser l'injection de dépendances

## Commandes Utiles

```bash
# Voir la structure
cd /app/backend && tree -L 2

# Tester un module
python -m pytest services/test_video_service.py

# Vérifier les imports
python -c "from api.routes import api_router; print('OK')"

# Lancer le serveur
uvicorn server:app --reload
```

## Fichiers Importants

| Fichier | Rôle |
|---------|------|
| `server.py` | Point d'entrée de l'application |
| `api/routes.py` | Définition de tous les endpoints |
| `config/dependencies.py` | Création des instances de services |
| `services/script_generation_service.py` | Cœur de la génération de scripts |
| `clients/ai_client.py` | Communication avec les LLMs |

---

**Date de dernière mise à jour**: 2025-10-31  
**Version**: 1.0.0
