# Migration vers Better-Auth

## ✅ Ce qui a été fait

1. **Installation de better-auth**
   - Ajouté `better-auth` dans `package.json`
   - Créé `/frontend/src/lib/auth.ts` (configuration serveur)
   - Créé `/frontend/src/lib/auth-client.ts` (client React)

2. **Routes API**
   - Créé `/frontend/src/app/api/auth/[...all]/route.ts` pour gérer les endpoints d'authentification

3. **Pages d'authentification**
   - Créé `/frontend/src/app/(auth)/signin/page.tsx` (vide - à compléter)
   - Créé `/frontend/src/app/(auth)/sign-up/page.tsx` (vide - à compléter)

4. **Context simplifié**
   - Mis à jour `AuthContext.tsx` pour utiliser better-auth au lieu de JWT custom

## 📝 À faire

### 1. Installer les dépendances

```bash
cd frontend
npm install
```

### 2. Configurer la base de données

Better-auth peut utiliser la même DB PostgreSQL que le backend. Ajoutez à `frontend/.env.local`:

```env
DATABASE_URL=postgresql://crossit:crossit@localhost:5432/crossit
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

### 3. Mettre à jour auth.ts avec la DB

```typescript
import { betterAuth } from 'better-auth';
import { Pool } from 'pg';

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

export const auth = betterAuth({
  database: pool,
  emailAndPassword: {
    enabled: true,
    // ... reste de la config
  },
  // ... reste de la config
});
```

### 4. Compléter les pages signin et sign-up

Exemple pour `signin/page.tsx`:

```typescript
'use client';

import { useState } from 'react';
import { signIn } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';

export default function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await signIn.email({ email, password });
      router.push('/dashboard');
    } catch (error) {
      console.error('Sign in failed', error);
    }
  };

  // Votre UI ici
}
```

### 5. OAuth Google/Microsoft/Apple (optionnel)

Si vous voulez les boutons sociaux:

```typescript
import { signIn } from '@/lib/auth-client';

// Dans votre composant
<button onClick={() => signIn.social({ provider: 'google' })}>
  Sign in with Google
</button>
```

## 🔄 Backend simplifié

Avec better-auth, l'authentification est gérée côté Next.js. Le backend FastAPI devient une **API de données uniquement**.

### Option 1: Garder l'API backend séparée
- Better-auth gère l'auth (Next.js)
- Backend FastAPI = API pour produits, listings, marketplaces
- Frontend envoie les tokens better-auth au backend pour authentifier les requêtes

### Option 2: Tout en Next.js
- Migrer les APIs backend vers Next.js API routes
- Utiliser Prisma + better-auth
- Plus simple mais moins scalable

**Recommandation**: Garder l'architecture actuelle (Option 1) car vous avez déjà tous les connecteurs marketplace en Python.

## 📚 Ressources

- [Better-auth Docs](https://www.better-auth.com)
- [Better-auth GitHub](https://github.com/better-auth/better-auth)
- [Migration Guide](https://www.better-auth.com/docs/migration)

## 🚀 Prochaines étapes

1. Installez better-auth: `npm install`
2. Complétez les pages signin/sign-up avec votre UI
3. Testez l'authentification
4. Intégrez avec l'API backend existante

