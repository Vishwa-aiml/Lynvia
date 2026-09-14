import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyDJJosIyT150Gs_DgaYST9W4f-uqwKXFEs",
  authDomain: "lynvia-58164.firebaseapp.com",
  projectId: "lynvia-58164",
  storageBucket: "lynvia-58164.firebasestorage.app",
  messagingSenderId: "69597520559",
  appId: "1:69597520559:web:1f7a53303c0a3462766a5a",
  measurementId: "G-4DR699VF2H"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const googleProvider = new GoogleAuthProvider();

export { app, auth, googleProvider };
