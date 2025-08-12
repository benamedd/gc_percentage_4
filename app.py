import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import math

# --- CONFIGURATION PWA ---
st.set_page_config(
    page_title="DNA Sequence Statistics Calculator",
    page_icon="192x192.png",  # Icône locale
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Get Help': 'https://github.com/benamedd/gc_percentage_4',
        'Report a bug': "https://github.com/benamedd/gc_percentage_4/issues",
        'About': "# DNA Sequence Calculator PWA\nAnalyze DNA sequences on any device!"
    }
)

# --- INJECTION DU CODE PWA ---
def inject_pwa_code():
    pwa_code = """
    <script>
    // Enregistrement du Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
          .then(reg => console.log('ServiceWorker OK'))
          .catch(err => console.log('ServiceWorker error:', err));
      });
    }

    // Prompt d'installation PWA
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      const btn = document.createElement('button');
      btn.textContent = '?? Installer l\'application';
      btn.style.cssText = `
        position: fixed; top: 10px; right: 10px; z-index: 1000;
        background: #4CAF50; color: white; border: none;
        padding: 10px 15px; border-radius: 5px; cursor: pointer;
      `;
      btn.addEventListener('click', () => {
        btn.style.display = 'none';
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then(() => deferredPrompt = null);
      });
      document.body.appendChild(btn);
    });
    </script>

    <!-- Manifest et meta -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#4CAF50">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="DNA Calc">
    <link rel="apple-touch-icon" href="/192x192.png">
    """
    st.components.v1.html(pwa_code, height=0)

inject_pwa_code()

# --- INTERFACE ---
def create_mobile_optimized_ui():
    st.title("?? DNA Sequence Calculator")

    with st.expander("?? Comment utiliser", expanded=False):
        st.markdown("""
        1. Collez votre séquence ADN ci-dessous
        2. Format FASTA accepté
        3. Analyse automatique
        4. Téléchargez les résultats en CSV
        """)

    sequence_input = st.text_area(
        "Séquence ADN :",
        height=150,
        placeholder="Exemple: ATGCGCTAGCTAGCTAGCATGC ou format FASTA"
    )

    if sequence_input:
        # Ici, ta logique de calcul
        pass

create_mobile_optimized_ui()
