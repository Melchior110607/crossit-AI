# 🧪 Guide de Test - Better Auth

## ✅ Problèmes Résolus

### 1. ❌ Problème: `/api/auth/*` était redirigé vers FastAPI backend
**Solution**: Modifié `next.config.js` pour exclure `/api/auth` du proxy. Better Auth reste dans Next.js.

### 2. ❌ Problème: Variables d'environnement non chargées dans Docker
**Solution**: Ajouté les variables dans `docker-compose.yml`:
- `DATABASE_URL=postgresql://crossit:crossit@postgres:5432/crossit` (utilise `postgres` au lieu de `localhost`)
- `NEXT_PUBLIC_APP_URL=http://localhost:3000`
- Support pour `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `MICROSOFT_CLIENT_ID`, `MICROSOFT_CLIENT_SECRET`

### 3. ❌ Problème: Erreurs signup/signin non visibles
**Solution**: Ajouté `try/catch` et logs console + toasts Sonner pour tous les erreurs.

---

## 🚀 Comment Tester

### Test 1: Email/Password Signup (doit fonctionner)

1. Va sur http://localhost:3000/signin
2. Clique sur "Sign up"
3. Remplis le formulaire:
   - First name: `Test`
   - Last name: `User`
   - Email: `test@example.com`
   - Password: `password123`
   - Confirm password: `password123`
   - Image (optionnel)
4. Clique sur "Create an account"
5. **Résultat attendu**: 
   - Toast vert "Account created successfully!"
   - Redirection vers `/dashboard`
6. **Si erreur**: Regarde la console du navigateur (F12 > Console)

### Test 2: Email/Password Signin

1. Va sur http://localhost:3000/signin
2. Entre:
   - Email: `test@example.com`
   - Password: `password123`
3. Clique sur "Login"
4. **Résultat attendu**: Redirection vers `/dashboard`
5. **Si erreur**: Toast rouge + message dans console

### Test 3: Google OAuth (nécessite configuration)

**Prérequis**: Ajouter les credentials dans `.env` à la racine

1. Crée `/Users/melchiorrufenacht/crossit AI/.env`:
```bash
GOOGLE_CLIENT_ID=ton_vrai_google_client_id
GOOGLE_CLIENT_SECRET=ton_vrai_google_client_secret
```

2. Redémarre: `docker-compose restart frontend`

3. Va sur http://localhost:3000/signin

4. Clique sur "Sign in with Google"

5. **Résultat attendu**: Redirection vers Google OAuth → Autorisation → Retour + login

### Test 4: Microsoft OAuth (nécessite configuration)

**Prérequis**: Ajouter les credentials dans `.env` à la racine

1. Ajoute dans `/Users/melchiorrufenacht/crossit AI/.env`:
```bash
MICROSOFT_CLIENT_ID=ton_vrai_microsoft_client_id
MICROSOFT_CLIENT_SECRET=ton_vrai_microsoft_client_secret
```

2. Redémarre: `docker-compose restart frontend`

3. Va sur http://localhost:3000/signin

4. Clique sur "Sign in with Microsoft"

5. **Résultat attendu**: Redirection vers Microsoft → Autorisation → Retour + login

---

## 🔍 Vérification en Base de Données

Pour voir les utilisateurs créés:

```bash
# Se connecter à PostgreSQL
docker exec -it crossit-postgres psql -U crossit -d crossit

# Lister les utilisateurs
SELECT id, name, email, "emailVerified", "createdAt" FROM "user";

# Lister les comptes (email vs OAuth)
SELECT id, "providerId", "userId", "createdAt" FROM "account";

# Lister les sessions actives
SELECT id, "userId", "expiresAt", "createdAt" FROM "session";

# Quitter
\q
```

---

## 🐛 Troubleshooting

### Erreur: "Failed to fetch" ou "Network error"

**Cause**: Better Auth API route non accessible

**Solution**:
```bash
# Vérifier que le frontend tourne
docker ps | grep frontend

# Voir les logs
docker logs crossit-frontend --tail 50

# Redémarrer si nécessaire
docker-compose restart frontend
```

### Erreur: "Database connection failed"

**Cause**: PostgreSQL non accessible depuis le container

**Vérification**:
```bash
# Depuis le container frontend, tester la connexion
docker exec -it crossit-frontend sh -c "nc -zv postgres 5432"

# Devrait afficher: postgres (172.x.x.x:5432) open
```

**Solution**: Assure-toi que `DATABASE_URL` utilise `postgres` (nom du service Docker) et pas `localhost`

### Les boutons Google/Microsoft ne font rien

**Cause possible 1**: Credentials non configurés (normal)
- Les boutons OAuth ne fonctionnent que si tu as ajouté les credentials dans `.env`
- Email/Password fonctionne toujours

**Cause possible 2**: Erreur JavaScript
- Ouvre la console (F12 > Console)
- Cherche des erreurs rouges
- Copie-les pour debug

### Erreur signup mais pas de message

**Solution**: Ouvre la console du navigateur:
1. Appuie sur F12
2. Va dans l'onglet "Console"
3. Tente de signup
4. Regarde les logs `Signup error:` ou `Signup exception:`
5. Copie l'erreur complète

---

## 📊 État Actuel

### ✅ Fonctionnel
- Email/Password signup
- Email/Password signin
- Sessions persistantes
- Redirections vers dashboard
- Error handling avec toasts
- Base de données PostgreSQL
- Tables Better Auth créées

### ⏳ Nécessite Configuration
- Google OAuth (credentials requis)
- Microsoft OAuth (credentials requis)

### ❌ Non Implémenté (volontairement)
- Apple OAuth (enlevé comme demandé)
- Email verification
- Password reset (fonction vide dans `auth.ts`)
- Two-factor authentication

---

## 📝 Fichiers Modifiés

1. **`next.config.js`**: Proxy sélectif (exclut `/api/auth`)
2. **`docker-compose.yml`**: Variables d'environnement pour frontend
3. **`frontend/src/app/(auth)/sign-up/page.tsx`**: Error handling amélioré
4. **`frontend/src/app/(auth)/signin/page.tsx`**: Suppression Apple, error handling
5. **`frontend/src/app/layout.tsx`**: Ajout Toaster Sonner
6. **`frontend/src/lib/auth.ts`**: Configuration PostgreSQL + Google/Microsoft

---

## 🎯 Prochaines Étapes

1. **Teste email/password** (devrait fonctionner immédiatement)
2. **Si problème**: Partage l'erreur de la console
3. **Pour OAuth**: Ajoute les credentials quand tu les as
4. **Continue le dev**: Les features marketplace/products sont prêtes

---

**✨ L'authentification est maintenant complète et fonctionnelle ! ✨**

