# Defect: DEF-006 — Google OAuth Token Expires Fréquemment

**Status**: 🔴 Open  
**Priority**: 🔴 Critical  
**Story Points**: 3  
**Created**: 2026-05-20  
**Updated**: 2026-05-20  
**Assigned Sprint**: Backlog  
**Reported by**: Martin Fournier

## Description

L'accès Google Tasks (OAuth) expire régulièrement, forçant une ré-approbation
manuelle. Le token refresh n'est pas persistant ou le refresh token expire.

Symptômes :
- "Google token expired" après quelques jours
- Doit refaire le flow OAuth complet
- Perturbation du flux GTD (tâches non synchronisées)

## Steps to Reproduce

1. Configurer Google Tasks OAuth
2. Utiliser le bot normalement pendant 2-7 jours
3. Constater que le token a expiré
4. Recevoir une erreur et devoir ré-approuver

## Analyse du Code (vérifié 2026-05-20)

Le code `google_tasks_client.py` a déjà :
- ✅ `access_type="offline"` → Refresh token demandé
- ❌ `prompt="consent"` → Force la ré-approbation à CHAQUE auth
- ❌ **Refresh token probablement pas rafraîchi automatiquement**

## Root Cause Probable

1. **prompt="consent"** : Le paramètre `prompt="consent"` force Google à
demander l'approbation à chaque fois, même si l'utilisateur a déjà approuvé.
**Solution** : Utiliser `prompt="auto"` ou supprimer le paramètre.

2. **Refresh token non rafraîchi** : Google invalide le refresh token si
l'utilisateur ré-approuve (à cause du prompt=consent). Le nouveau refresh token
n'est pas stocké → perte de la session.

3. **Token storage** : Le token (incluant refresh_token) est stocké mais
probablement pas persisté entre les redémarrages du serveur.

## Solution Proposée

1. Vérifier que le scope OAuth demande `https://www.googleapis.com/auth/tasks`
   **avec** `access_type=offline` (garantit un refresh token)
2. Stocker le refresh token en base (pas seulement le access token)
3. Implémenter le refresh automatique : si `access_token` expire, utiliser
   `refresh_token` pour en obtenir un nouveau
4. Ajouter un log quand le refresh réussit ou échoue (debug)

## Code à Modifier

- `src/google_tasks_client.py` — Vérifier le scope OAuth + refresh logic
- Base de données des tokens — Ajouter colonne `refresh_token` si manquante
- `src/auth_service.py` — Gestion du refresh automatique

## Test

- [ ] Simuler une expiration de token → refresh automatique réussi
- [ ] Vérifier que le refresh token est stocké après la première approbation
- [ ] Vérifier que le bot fonctionne 7+ jours sans ré-approbation manuelle

## Related

- DEF-001 (Google Tasks Sync — marqué complété mais root cause token refresh non adressée)
