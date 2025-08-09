import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import math

# Configuration PWA
st.set_page_config(
    page_title="DNA Sequence Statistics Calculator",
    page_icon="??",
    layout="wide",
    initial_sidebar_state="collapsed",  # Optimisé pour mobile
    menu_items={
        'Get Help': 'https://github.com/benamedd/gc_percentage_4',
        'Report a bug': "https://github.com/benamedd/gc_percentage_4/issues",
        'About': "# DNA Sequence Calculator PWA\nAnalyze DNA sequences on any device!"
    }
)

# Injection du code PWA
def inject_pwa_code():
    pwa_code = """
    <script>
    // Enregistrement du Service Worker
    if ('serviceWorker' in navigator) {
      window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
          .then(function(registration) {
            console.log('ServiceWorker registration successful');
          }, function(err) {
            console.log('ServiceWorker registration failed: ', err);
          });
      });
    }
    
    // Gestion de l'installation PWA
    let deferredPrompt;
    window.addEventListener('beforeinstallprompt', (e) => {
      e.preventDefault();
      deferredPrompt = e;
      
      // Afficher bouton d'installation custom
      const installButton = document.createElement('button');
      installButton.textContent = 'Installer l\\'app ??';
      installButton.style.cssText = `
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background: #4CAF50;
        color: white;
        border: none;
        padding: 10px 15px;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
      `;
      
      installButton.addEventListener('click', (e) => {
        installButton.style.display = 'none';
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
          if (choiceResult.outcome === 'accepted') {
            console.log('User accepted the install prompt');
          }
          deferredPrompt = null;
        });
      });
      
      document.body.appendChild(installButton);
    });
    
    // CSS pour mobile
    const mobileCSS = `
    <style>
    @media (max-width: 768px) {
      .main .block-container {
        padding-top: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
      }
      
      .stColumns > div {
        margin-bottom: 1rem;
      }
      
      .stTextArea textarea {
        font-size: 16px !important;
      }
      
      .stButton button {
        width: 100%;
        margin: 0.25rem 0;
      }
      
      .stPlotlyChart {
        height: 300px !important;
      }
    }
    
    /* Masquer le bouton hamburger sur mobile */
    @media (max-width: 768px) {
      .css-1rs6os.edgvbvh3 {
        display: none;
      }
    }
    </style>
    `;
    
    document.head.insertAdjacentHTML('beforeend', mobileCSS);
    </script>
    
    <!-- Manifest PWA -->
    <link rel="manifest" href="/manifest.json">
    <meta name="theme-color" content="#4CAF50">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="default">
    <meta name="apple-mobile-web-app-title" content="DNA Calc">
    <link rel="apple-touch-icon" href="https://cdn-icons-png.flaticon.com/192/8847/8847419.png">
    """
    st.components.v1.html(pwa_code, height=0)

# Injection du code PWA
inject_pwa_code()

# [Ici, copiez tout le reste de votre code app.py existant...]
# Toutes vos fonctions : clean_sequence, compute_gc_skew, etc.
# Interface utilisateur optimisée pour mobile

def create_mobile_optimized_ui():
    st.title("?? DNA Sequence Calculator")
    
    # Interface compacte pour mobile
    with st.expander("?? Comment utiliser", expanded=False):
        st.markdown("""
        1. Collez votre séquence ADN ci-dessous
        2. Format FASTA accepté
        3. Analyse automatique
        4. Téléchargez les résultats en CSV
        """)
    
    sequence_input = st.text_area(
        "Séquence ADN:",
        height=150,
        placeholder="Exemple: ATGCGCTAGCTAGCTAGCATGC ou format FASTA"
    )
    
    if sequence_input:
        # [Votre logique de calcul existante...]
        pass

# Utilisation de l'interface optimisée
create_mobile_optimized_ui()
