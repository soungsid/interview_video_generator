# Architecture Détaillée du Projet

## Vue d'ensemble de l'Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FASTAPI APPLICATION                             │
│                            (server.py)                                  │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         API LAYER (api/)                                │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       routes.py                                  │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────────┐  │  │
│  │  │ GET /api/      │  │ POST /generate │  │ GET /videos      │  │  │
│  │  │ (health check) │  │ (create video) │  │ (list videos)    │  │  │
│  │  └────────────────┘  └────────────────┘  └──────────────────┘  │  │
│  │  ┌────────────────┐                                             │  │
│  │  │ GET /videos/id │                                             │  │
│  │  │ (get video)    │                                             │  │
│  │  └────────────────┘                                             │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────┬───────────────────┘
                 │                                    │
                 ▼                                    ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│    SERVICE LAYER (services/)         │  │     CONFIG (config/)         │
│  ┌────────────────────────────────┐  │  │  ┌────────────────────────┐  │
│  │ ScriptGenerationService        │  │  │  │  dependencies.py       │  │
│  │  - generate_video_script()     │  │  │  │   - Singletons         │  │
│  │  - _generate_introduction()    │  │  │  │   - Factory patterns   │  │
│  │  - _generate_dialogues()       │  │  │  └────────────────────────┘  │
│  │  - _generate_conclusion()      │  │  │  ┌────────────────────────┐  │
│  └────────┬───────────────────────┘  │  │  │  database.py           │  │
│           │                           │  │  │   - MongoDB connection │  │
│  ┌────────▼───────────────────────┐  │  │  │   - Singleton instance │  │
│  │ VideoService                   │  │  │  └────────────────────────┘  │
│  │  - create_video()              │  │  └──────────────────────────────┘
│  │  - get_video_by_id()           │  │
│  │  - get_all_videos()            │  │
│  └────────┬───────────────────────┘  │
└───────────┼──────────────────────────┘
            │
            ├────────────────────────────────────────┐
            │                                        │
            ▼                                        ▼
┌──────────────────────────────┐      ┌──────────────────────────────┐
│  CLIENTS (clients/)          │      │  DATABASE                    │
│  ┌────────────────────────┐  │      │  ┌────────────────────────┐  │
│  │  AIClient              │  │      │  │  MongoDB               │  │
│  │   - api_key            │  │      │  │                        │  │
│  │   - base_url           │  │      │  │  Collections:          │  │
│  │   - default_model      │  │      │  │   - videos             │  │
│  │                        │  │      │  │   - dialogues          │  │
│  │   generate_completion()│  │      │  │                        │  │
│  │     ↓                  │  │      │  └────────────────────────┘  │
│  │  [OpenAI Compatible]   │  │      └──────────────────────────────┘
│  └────────┬───────────────┘  │
└───────────┼──────────────────┘
            │
            ▼
┌──────────────────────────────┐
│  EXTERNAL AI PROVIDERS       │
│  ┌────────────────────────┐  │
│  │  DeepSeek API          │  │
│  │  https://api.          │  │
│  │    deepseek.com/v1     │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │  OpenAI API            │  │
│  │  https://api.          │  │
│  │    openai.com/v1       │  │
│  └────────────────────────┘  │
│  ┌────────────────────────┐  │
│  │  Other Compatible APIs │  │
│  └────────────────────────┘  │
└──────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│                     ENTITIES (entities/)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │  Video       │  │  Dialogue    │  │  Requests    │              │
│  │  - id        │  │  - id        │  │  - topic     │              │
│  │  - title     │  │  - role      │  │  - num_q     │              │
│  │  - topic     │  │  - text      │  │  - model     │              │
│  │  - intro     │  │  - q_number  │  └──────────────┘              │
│  │  - conclusion│  │  - video_id  │                                 │
│  │  - created_at│  └──────────────┘                                 │
│  └──────────────┘                                                    │
└──────────────────────────────────────────────────────────────────────┘
```

## Flux de Génération de Script (Détaillé)

```
┌─────────┐
│ CLIENT  │
└────┬────┘
     │ POST /api/videos/generate
     │ { topic: "Docker", num_questions: 3 }
     │
     ▼
┌─────────────────────────────────────────────────────────┐
│ API LAYER (routes.py)                                   │
│  1. Validation des données (Pydantic)                   │
│  2. Récupération des services (dependencies)            │
│  3. Appel script_service.generate_video_script()        │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ SCRIPT GENERATION SERVICE                               │
│                                                         │
│  Phase 1: Introduction                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │ Messages = [                                   │    │
│  │   {system: "YouTuber prompt"},                 │    │
│  │   {user: "Create intro for Docker"}            │    │
│  │ ]                                              │    │
│  └────────────┬───────────────────────────────────┘    │
│               │                                         │
│               ▼                                         │
│       ┌──────────────────┐                             │
│       │   ai_client      │ ──────► DeepSeek API        │
│       │ generate_         │ ◄────── "Welcome to..."    │
│       │ completion()      │                             │
│       └──────────────────┘                             │
│                                                         │
│  Phase 2: Dialogues (avec mémoire conversationnelle)   │
│  ┌────────────────────────────────────────────────┐    │
│  │ conversation_history = [                       │    │
│  │   {system: "Interview simulation context"},    │    │
│  │ ]                                              │    │
│  │                                                │    │
│  │ Pour chaque question (1 à num_questions):      │    │
│  │                                                │    │
│  │   # Question YOUTUBER                          │    │
│  │   conversation_history.append(                 │    │
│  │     {user: "As YOUTUBER, ask Q1"}              │    │
│  │   )                                            │    │
│  │   question = ai_client.generate(history)       │ ───┐
│  │   conversation_history.append(question)        │    │
│  │                                                │    │
│  │   # Réponse CANDIDATE                          │    │
│  │   conversation_history.append(                 │    │
│  │     {user: "As CANDIDATE, answer"}             │    │
│  │   )                                            │    │
│  │   answer = ai_client.generate(history)         │ ───┤
│  │   conversation_history.append(answer)          │    │
│  │                                                │    │
│  │   dialogues.append(question, answer)           │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  Phase 3: Conclusion                                    │
│  ┌────────────────────────────────────────────────┐    │
│  │ Messages = [                                   │    │
│  │   {system: "YouTuber conclusion"},             │    │
│  │   {user: "Create conclusion"}                  │    │
│  │ ]                                              │    │
│  └────────────┬───────────────────────────────────┘    │
│               │                                         │
│               ▼                                         │
│       ┌──────────────────┐                             │
│       │   ai_client      │ ──────► DeepSeek API        │
│       │ generate_         │ ◄────── "Thanks for..."    │
│       │ completion()      │                             │
│       └──────────────────┘                             │
│                                                         │
│  Return: {                                             │
│    introduction: "...",                                │
│    dialogues: [...],                                   │
│    conclusion: "..."                                   │
│  }                                                     │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ VIDEO SERVICE                                           │
│                                                         │
│  1. Créer objet Video                                   │
│  ┌────────────────────────────────────────────────┐    │
│  │ video = Video(                                 │    │
│  │   id=uuid(),                                   │    │
│  │   title="Simulated Interview: Docker",        │    │
│  │   topic="Docker",                              │    │
│  │   introduction="...",                          │    │
│  │   conclusion="...",                            │    │
│  │   created_at=now()                             │    │
│  │ )                                              │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  2. Sauvegarder vidéo dans MongoDB                      │
│     db.videos.insert_one(video)                         │
│                                                         │
│  3. Sauvegarder dialogues                               │
│  ┌────────────────────────────────────────────────┐    │
│  │ for dialogue_data in dialogues:                │    │
│  │   dialogue = Dialogue(                         │    │
│  │     id=uuid(),                                 │    │
│  │     role=YOUTUBER/CANDIDATE,                   │    │
│  │     text="...",                                │    │
│  │     question_number=i,                         │    │
│  │     video_id=video.id                          │    │
│  │   )                                            │    │
│  │   db.dialogues.insert_one(dialogue)            │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  4. Récupérer vidéo complète                            │
│     return get_video_by_id(video.id)                    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ MONGODB                                                 │
│                                                         │
│  Collection: videos                                     │
│  ┌────────────────────────────────────────────────┐    │
│  │ {                                              │    │
│  │   id: "uuid-123",                              │    │
│  │   title: "Simulated Interview: Docker",       │    │
│  │   topic: "Docker",                             │    │
│  │   introduction: "Welcome...",                  │    │
│  │   conclusion: "Thanks...",                     │    │
│  │   created_at: "2025-10-31T..."                 │    │
│  │ }                                              │    │
│  └────────────────────────────────────────────────┘    │
│                                                         │
│  Collection: dialogues                                  │
│  ┌────────────────────────────────────────────────┐    │
│  │ { id: "d1", role: "YOUTUBER",                  │    │
│  │   text: "What is Docker?",                     │    │
│  │   question_number: 1, video_id: "uuid-123" }   │    │
│  │                                                │    │
│  │ { id: "d2", role: "CANDIDATE",                 │    │
│  │   text: "Docker is...",                        │    │
│  │   question_number: 1, video_id: "uuid-123" }   │    │
│  │                                                │    │
│  │ { id: "d3", role: "YOUTUBER",                  │    │
│  │   text: "You mentioned containers...",         │    │
│  │   question_number: 2, video_id: "uuid-123" }   │    │
│  │   ↑ Référence à la réponse précédente!        │    │
│  └────────────────────────────────────────────────┘    │
└─────────────────────────┬───────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│ RESPONSE                                                │
│  {                                                      │
│    id: "uuid-123",                                      │
│    title: "Simulated Interview: Docker",               │
│    topic: "Docker",                                     │
│    introduction: "Welcome...",                          │
│    conclusion: "Thanks...",                             │
│    created_at: "2025-10-31T...",                        │
│    dialogues: [                                         │
│      { id: "d1", role: "YOUTUBER", ... },               │
│      { id: "d2", role: "CANDIDATE", ... },              │
│      { id: "d3", role: "YOUTUBER", ... },               │
│      { id: "d4", role: "CANDIDATE", ... }               │
│    ]                                                    │
│  }                                                      │
└─────────────────────────────────────────────────────────┘
```

## Mémoire Conversationnelle

La clé de cette architecture est la **mémoire conversationnelle** maintenue dans `conversation_history`:

```python
conversation_history = [
    {role: "system", content: "Context..."}
]

# Question 1
conversation_history.append({role: "user", content: "Ask Q1"})
q1 = generate(conversation_history)
conversation_history.append({role: "assistant", content: q1})

conversation_history.append({role: "user", content: "Answer Q1"})
a1 = generate(conversation_history)
conversation_history.append({role: "assistant", content: a1})

# Question 2 (avec contexte Q1+A1)
conversation_history.append({role: "user", content: "Ask Q2"})
q2 = generate(conversation_history)  # ← A accès à Q1 et A1!
conversation_history.append({role: "assistant", content: q2})

conversation_history.append({role: "user", content: "Answer Q2"})
a2 = generate(conversation_history)  # ← A accès à Q1, A1, Q2!
```

Cela permet:
- **Q2** de référencer **A1**: "You mentioned containers..."
- **A2** de référencer **Q1** et **A1**: "As I mentioned earlier..."
- Progression naturelle de la difficulté
- Cohérence conversationnelle

## Patterns de Design Utilisés

1. **Layered Architecture** (Architecture en couches)
   - API → Services → Clients/Database
   - Séparation claire des responsabilités

2. **Dependency Injection** (Injection de dépendances)
   - Services reçoivent leurs dépendances
   - Facilite les tests et le changement

3. **Repository Pattern**
   - VideoService encapsule l'accès aux données
   - Abstraction de la base de données

4. **Factory Pattern**
   - `get_video_service()` crée les instances
   - Gestion centralisée des dépendances

5. **Singleton Pattern**
   - AIClient et ScriptGenerationService sont des singletons
   - Évite la création multiple d'instances coûteuses

6. **Strategy Pattern** (implicite)
   - AIClient peut utiliser différents providers
   - Changement facile de modèle LLM
