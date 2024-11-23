import React from 'react';
import ReactDOM from 'react-dom/client';
import App from "./pages/App";

const root = document.getElementById('root')
console.log(root)

if (root) {
    ReactDOM.createRoot(root).render(
        <React.StrictMode>
            <App />
        </React.StrictMode>
    );
}
