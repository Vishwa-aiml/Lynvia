// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
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
const analytics = getAnalytics(app);