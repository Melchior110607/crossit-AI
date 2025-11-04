# 🔐 Configuration Centralisée - Un Seul .env

## 🎯 Problème Actuel

Tu as raison ! Il y a **trop de fichiers .env**:
- ❌ `backend/.env` 
- ❌ `frontend/.env.local`
- ⚠️ Variables dupliquées et fragmentées

## ✅ Solution: Un seul .env à la racine

### 📝 Étape 1: Créer `/Users/melchiorrufenacht/crossit AI/.env`

Crée ce fichier à la racine du projet:

```bash
# ==============================================
# 🔐 CROSSIT - Configuration Centralisée
# ==============================================

# ==============================================
# 🌐 APPLICATION
# ==============================================
NEXT_PUBLIC_APP_URL=http://localhost:3000
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# ==============================================
# 🗄️ DATABASE (PostgreSQL)
# ==============================================
POSTGRES_USER=crossit
POSTGRES_PASSWORD=crossit
POSTGRES_DB=crossit
DATABASE_URL=postgresql://crossit:crossit@postgres:5432/crossit

# ==============================================
# 🔴 REDIS
# ==============================================
REDIS_URL=redis://redis:6379

# ==============================================
# 🔑 AUTHENTICATION (Better Auth)
# ==============================================
JWT_SECRET=dev-secret-change-in-production

# OAuth Google (OPTIONNEL pour dev)
# Console: https://console.cloud.google.com/
# Redirect URI: http://localhost:3000/api/auth/callback/google
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=

# OAuth Microsoft (OPTIONNEL pour dev)
# Portal: https://portal.azure.com/
# Redirect URI: http://localhost:3000/api/auth/callback/microsoft
MICROSOFT_CLIENT_ID=
MICROSOFT_CLIENT_SECRET=

# ==============================================
# ☁️ AWS S3 (OPTIONNEL pour dev)
# ==============================================
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_S3_BUCKET=crossit-products
AWS_REGION=us-east-1

# ==============================================
# 🐝 CELERY
# ==============================================
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ==============================================
# 🔧 DEVELOPMENT
# ==============================================
DEBUG=True
LOG_LEVEL=INFO
```

### ✅ Étape 2: Docker-compose.yml modifié !

Le fichier `docker-compose.yml` a été modifié pour:
- ✅ Charger automatiquement `.env` à la racine
- ✅ Supprimer tous les `env_file:` individuels
- ✅ Utiliser `${VAR:-default}` pour toutes les variables

### 🚀 Étape 3: Redémarrer les services

```bash
cd "/Users/melchiorrufenacht/crossit AI"

# Arrêter tous les services
docker-compose down

# Redémarrer avec le nouveau .env
docker-compose up -d
```

### 🧪 Étape 4: Vérifier que les variables sont chargées

```bash
# Vérifier frontend
docker exec crossit-frontend env | grep -E "(DATABASE_URL|GOOGLE|MICROSOFT)" | sort

# Vérifier backend
docker exec crossit-backend env | grep -E "(DATABASE_URL|AWS|JWT)" | sort
```

### ✅ Résultat Attendu

Avec le `.env` à la racine:
- ✅ **Email/Password** fonctionnera immédiatement
- ✅ **PostgreSQL** connecté
- ⏳ **OAuth Google/Microsoft** si tu ajoutes les credentials

**Sans credentials OAuth**: Les boutons seront visibles mais inactifs (NORMAL)

---

## 🎯 Résumé

### Avant (Problème):
```
❌ backend/.env
❌ frontend/.env.local
❌ Variables dupliquées
❌ Docker ne charge pas tout
```

### Après (Solution):
```
✅ .env (à la racine seulement)
✅ Docker Compose charge automatiquement
✅ Toutes les variables centralisées
✅ Facile à maintenir
```

---

## 📝 Variables Requises pour Fonctionner

### ✅ OBLIGATOIRES (déjà dans le .env minimal):
- `DATABASE_URL` ✅
- `NEXT_PUBLIC_APP_URL` ✅
- `JWT_SECRET` ✅

### ⏳ OPTIONNELLES (pour plus tard):
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET`
- `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`

---

## 🐛 Debugging du Signup

Si le signup échoue encore après avoir créé le `.env`:

```bash
# Voir les logs en temps réel
docker logs -f crossit-frontend

# Puis dans un autre terminal, teste le signup
# Les erreurs s'afficheront dans les logs
```

**Erreurs communes**:
- `"Database connection failed"` → Vérifie que postgres tourne
- `"Email already exists"` → L'email est déjà utilisé
- `"Password too short"` → Better Auth requiert 8+ caractères
- `"Failed to hash password"` → Problème de configuration Better Auth

---

## 🎉 Prochaines Étapes

1. **Crée le `.env`** à la racine (voir template ci-dessus)
2. **Redémarre**: `docker-compose down && docker-compose up -d`
3. **Teste signup** sur http://localhost:3000/signin
4. **Si erreur**: Partage les logs `docker logs crossit-frontend --tail 50`
5. **Pour OAuth** (plus tard): Ajoute les credentials dans le `.env`

