# 🔐 OAuth Configuration Guide - Better Auth

Ce guide explique comment configurer Google et Microsoft OAuth pour votre application CrossIt.

## ✅ Ce qui est déjà fait

- ✅ Better Auth installé et configuré
- ✅ Base de données PostgreSQL avec les tables créées
- ✅ Pages Sign In / Sign Up avec OAuth buttons
- ✅ Email/Password authentication fonctionnelle
- ✅ Redirection automatique vers `/dashboard` après connexion

## 🔑 Configuration OAuth

### 📁 Fichier .env.local à créer

Crée le fichier `frontend/.env.local` avec le contenu suivant:

```bash
# Application URL
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Database Connection
DATABASE_URL=postgresql://crossit:crossit@localhost:5432/crossit

# Google OAuth Credentials
# Redirect URL: http://localhost:3000/api/auth/callback/google
GOOGLE_CLIENT_ID=ton_google_client_id_ici
GOOGLE_CLIENT_SECRET=ton_google_client_secret_ici

# Microsoft OAuth Credentials  
# Redirect URL: http://localhost:3000/api/auth/callback/microsoft
MICROSOFT_CLIENT_ID=ton_microsoft_client_id_ici
MICROSOFT_CLIENT_SECRET=ton_microsoft_client_secret_ici
```

---

## 🌐 Google OAuth Setup

### 1. Accède à Google Cloud Console
- Ouvre: https://console.cloud.google.com/
- Crée un nouveau projet ou sélectionne-en un existant

### 2. Active l'API Google+ 
- Va dans **APIs & Services** > **Library**
- Cherche "Google+ API" et active-la

### 3. Crée les Credentials OAuth 2.0
- Va dans **APIs & Services** > **Credentials**
- Clique sur **Create Credentials** > **OAuth client ID**
- Type d'application: **Web application**
- Nom: `CrossIt Local Development`

### 4. Configure les Redirect URIs
Ajoute ces URLs dans **Authorized redirect URIs**:
```
http://localhost:3000/api/auth/callback/google
```

Pour production, ajoute aussi:
```
https://ton-domaine.com/api/auth/callback/google
```

### 5. Récupère les credentials
- Copie le **Client ID**
- Copie le **Client Secret**
- Mets-les dans `.env.local`

---

## 🏢 Microsoft OAuth Setup (Azure Entra ID)

### 1. Accède à Azure Portal
- Ouvre: https://portal.azure.com/
- Va dans **Azure Active Directory** (ou **Microsoft Entra ID**)

### 2. Enregistre une application
- Va dans **App registrations** > **New registration**
- Nom: `CrossIt Local`
- Supported account types: **Accounts in any organizational directory and personal Microsoft accounts**
- Redirect URI:
  - Type: **Web**
  - URL: `http://localhost:3000/api/auth/callback/microsoft`

### 3. Crée un Client Secret
- Dans ton app, va dans **Certificates & secrets**
- Clique sur **New client secret**
- Description: `CrossIt Local Secret`
- Expires: 24 months (ou jamais pour dev)
- **Copie immédiatement la VALUE** (tu ne pourras plus la voir après !)

### 4. Récupère les credentials
- **Client ID (Application ID)**: Dans **Overview** > **Application (client) ID**
- **Client Secret**: La valeur que tu viens de copier
- Mets-les dans `.env.local`

### 5. Configure les permissions (optionnel)
- Va dans **API permissions**
- Par défaut, Better Auth demande: `openid`, `profile`, `email`
- Ces permissions sont déjà accordées

---

## 🚀 Test de l'authentification

### 1. Démarre les services Docker
```bash
docker-compose up -d postgres redis
```

### 2. Démarre le frontend
```bash
cd frontend
npm run dev
```

### 3. Teste les fonctionnalités

#### Email/Password (déjà fonctionnel)
- Va sur http://localhost:3000/signin
- Crée un compte avec email/password
- Tu seras redirigé vers `/dashboard`

#### OAuth Google (après configuration)
- Clique sur "Sign in with Google"
- Autorise l'application
- Tu seras redirigé vers `/dashboard`

#### OAuth Microsoft (après configuration)
- Clique sur "Sign in with Microsoft"
- Choisis ton compte
- Tu seras redirigé vers `/dashboard`

---

## 🔍 Vérification de la DB

Pour voir les utilisateurs créés:

```bash
# Connecte-toi à PostgreSQL
docker exec -it crossit-postgres psql -U crossit -d crossit

# Liste les utilisateurs
SELECT id, name, email, "emailVerified", "createdAt" FROM "user";

# Liste les comptes OAuth
SELECT id, "providerId", "userId", "createdAt" FROM "account";

# Liste les sessions
SELECT id, "userId", "expiresAt", "createdAt" FROM "session";

# Quitter
\q
```

---

## 📦 Structure des Tables Better Auth

Better Auth a créé automatiquement ces tables:

### Table: `user`
- `id`: UUID unique
- `name`: Nom complet
- `email`: Email (unique)
- `emailVerified`: Date de vérification
- `image`: URL de la photo de profil
- `createdAt`, `updatedAt`: Timestamps

### Table: `session`
- `id`: UUID unique
- `token`: Token de session
- `expiresAt`: Date d'expiration
- `userId`: Référence à `user`
- `ipAddress`, `userAgent`: Info de connexion

### Table: `account`
- `id`: UUID unique
- `accountId`: ID du compte OAuth
- `providerId`: `google`, `microsoft`, `email`
- `userId`: Référence à `user`
- `accessToken`, `refreshToken`: Tokens OAuth
- `accessTokenExpiresAt`, `refreshTokenExpiresAt`: Expirations
- `scope`: Scopes autorisés
- `password`: Hash du mot de passe (si email/password)

### Table: `verification`
- `id`: UUID unique
- `identifier`: Email à vérifier
- `value`: Token de vérification
- `expiresAt`: Date d'expiration

---

## 🐛 Troubleshooting

### "Social provider google/microsoft is missing clientId or clientSecret"
- C'est un **warning**, pas une erreur !
- Ça signifie que OAuth n'est pas encore configuré
- L'email/password fonctionne quand même
- Une fois les credentials ajoutés dans `.env.local`, redémarre le serveur

### OAuth callback error
- Vérifie que les redirect URIs sont exactement:
  - Google: `http://localhost:3000/api/auth/callback/google`
  - Microsoft: `http://localhost:3000/api/auth/callback/microsoft`
- Vérifie que `NEXT_PUBLIC_APP_URL=http://localhost:3000` dans `.env.local`

### Database connection error
- Vérifie que PostgreSQL tourne: `docker ps | grep postgres`
- Vérifie le `DATABASE_URL` dans `.env.local`

---

## 🎯 Prochaines étapes

1. **Maintenant**: Configure Google et Microsoft OAuth avec ce guide
2. **Ensuite**: Continue le développement des features (marketplaces, products, listings)
3. **Plus tard**: Configure OAuth en production avec ton domaine réel

---

**🎉 Félicitations ! L'authentification est maintenant configurée avec Better Auth !**

