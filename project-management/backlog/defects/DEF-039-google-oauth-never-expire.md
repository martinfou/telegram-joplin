# Defect: DEF-039 — Google OAuth Token Doit Ne JAMAIS Expirer

**Statut**: 🟡 Partially Fixed (root cause removed, DB persistence pending)
**Priorité**: 🔴 Critique
**Story Points**: 5
**Créé**: 2026-05-20
**Mis à jour**: 2026-05-20
**Sprint**: Backlog
**Rapporté par**: Martin Fournier

---

## Énoncé du Problème

Le token Google OAuth expire régulièrement (2-7 jours), forçant une
ré-approbation manuelle. Pourtant, le code demande déjà `access_type=offline`
qui est censé garantir un refresh token permanent.

**Objectif :** Le token NE DOIT JAMAIS expirer. Aucune ré-approbation manuelle
ne devrait être nécessaire après la configuration initiale.

**Impact utilisateur :** Martin doit ré-approuver Google Tasks toutes les
quelques jours. Le flux GTD est interrompu. Le bot devient inutilisable
pour les tâches jusqu'à la ré-approbation.

---

## Root Cause Analysis

### Code actuel (`google_tasks_client.py`)

```python
session.authorization_url(
    self.AUTH_URL,
    access_type="offline",     # ✅ Refresh token demandé (bon)
    prompt="consent"           # ❌ FORCE la ré-approbation à chaque auth
)
```

### Pourquoi le token expire

1. **`prompt="consent"`** : Ce paramètre FORCE Google à afficher l'écran de
   consentement à CHAQUE authorization, même si l'utilisateur a déjà approuvé.
   
2. **Google invalide l'ancien refresh token** : Quand l'utilisateur ré-approuve
   (à cause de prompt=consent), Google invalide l'ANCIEN refresh token et en
   émet un NOUVEAU. Si le nouveau n'est pas correctement stocké → le token
   est perdu.

3. **Stockage non persistant** : Le token (incluant refresh_token) est stocké
   en mémoire mais probablement pas persisté entre les redémarrages du serveur
   Fly.io. À chaque redéploiement, le token est perdu.

### Chronologie d'une défaillance

```
Jour 1 : Auth Google → refresh_token stocké ✅
Jour 3 : Refresh token utilisé → nouveau access_token ✅
Jour 7 : Serveur Fly.io redémarre → refresh_token perdu ❌
Jour 8 : Token expired → tentative refresh → échec → "ré-approuvez"
```

### DEF-027 (complété) n'a pas résolu le problème

DEF-027 a amélioré les messages d'erreur ("Use /tasks_connect") mais n'a PAS
corrigé la cause racine : le token continue d'expirer.

---

## Solution Requise : Token Permanent

### 1. Supprimer `prompt="consent"` (root cause #1)

```python
# Avant (BUG)
session.authorization_url(self.AUTH_URL, access_type="offline", prompt="consent")

# Après (FIX)
session.authorization_url(self.AUTH_URL, access_type="offline")
# ou : prompt="auto" (ne force pas la ré-approbation)
```

Google retourne un refresh token UNIQUEMENT la première fois que l'utilisateur
approuve (avec `access_type=offline`). `prompt="consent"` force une
ré-approbation à chaque fois, ce qui invalide le refresh token précédent.

### 2. Stockage persistant du refresh token (root cause #2)

Le token DOIT être persisté en base de données (SQLite), pas seulement en mémoire :
- Table `google_tokens` : `user_id, access_token, refresh_token, token_uri, client_id, client_secret, scopes, expiry`
- Chargé au démarrage du serveur
- Sauvegardé après chaque rafraîchissement

### 3. Refresh automatique robuste (root cause #3)

```python
class GoogleTasksClient:
    def __init__(self):
        self.token = self._load_token_from_db()
        
    def _load_token_from_db(self):
        """Charge le token depuis la base de données au démarrage."""
        ...
    
    def _save_token_to_db(self, token):
        """Persiste le token après chaque refresh."""
        ...
    
    def refresh_token_if_expired(self):
        """Vérifie et refresh automatiquement au démarrage + périodiquement."""
        if self.token and self._is_expired():
            self._refresh_token()
            self._save_token_to_db(self.token)
```

---

## Acceptance Criteria

- [ ] Le `prompt="consent"` est supprimé → Google ne redemande PAS l'approbation
- [ ] Le refresh token est stocké en base de données (SQLite)
- [ ] Au démarrage du serveur, le token est chargé depuis la DB
- [ ] Après chaque refresh, le nouveau token est persisté en DB
- [ ] Le bot fonctionne 30+ jours sans ré-approbation manuelle
- [ ] Après redémarrage du serveur Fly.io, le token est toujours valide
- [ ] Aucune régression sur le flux d'auth initial (première connexion)

---

## Fichiers à Modifier

| Fichier | Changement |
|---------|------------|
| `src/google_tasks_client.py` | Supprimer `prompt="consent"`, ajouter stockage DB |
| `src/container.py` | Ajouter `GoogleTokenRepository` au container DI |
| Base de données | Nouvelle table `google_tokens` |
| `src/auth_service.py` | Charger/sauvegarder token dans la DB |

---

## Code à Supprimer

```python
# Ligne 68 de google_tasks_client.py — À SUPPRIMER
prompt="consent",
```

Un seul mot supprime la cause racine.

---

## Test

- [ ] Auth flow complet → refresh token stocké en DB
- [ ] Démarrage → token chargé depuis DB → pas de ré-auth
- [ ] Refresh automatique → nouveau token persisté
- [ ] 30 jours sans ré-approbation manuelle
- [ ] Redémarrage serveur → token toujours valide

---

## Related Defects

- DEF-027 (Google Tasks token expired — complété mais root cause non adressée)
- DEF-001 (Google Tasks sync no token)
