# Frontend

React + Vite frontend for the AI Marketing Partner.

## Run Locally

```powershell
cd frontend
npm install
npm run dev
```

The app runs at:

```text
http://localhost:5173
```

## Firebase

Firebase Web SDK config is loaded from `frontend/.env.local`.
Use `frontend/.env.example` as the template for another machine.

Enable Email/Password in Firebase Authentication before using the login page:

1. Open Firebase Console.
2. Select the `ai-agent-dhaanyashree` project.
3. Go to Authentication.
4. Click Get started if Authentication has not been initialized.
5. Open Sign-in method.
6. Enable Email/Password.
