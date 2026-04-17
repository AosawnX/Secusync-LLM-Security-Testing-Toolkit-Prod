import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

// Firebase client config — these values are public by design.
// Firebase enforces security via Authorized Domains (Console → Auth → Settings)
// and server-side token verification. The service account key (secret) never
// touches the frontend.
const firebaseConfig = {
  apiKey: "AIzaSyBoo1hJbp3_ZbnLlCTcl5t_1SNmhoAOT68",
  authDomain: "secusync-auth.firebaseapp.com",
  projectId: "secusync-auth",
  storageBucket: "secusync-auth.firebasestorage.app",
  messagingSenderId: "153371983858",
  appId: "1:153371983858:web:b252184bceee58b3c0756b",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
