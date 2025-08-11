const CACHE_NAME = 'dna-calculator-v2'; // ⚠️ Change à chaque update pour forcer le refresh
const urlsToCache = [
  '/', // page principale
  '/manifest.json',
  '/192x192.png',
  '/512x512.png',
  'https://cdn.jsdelivr.net/npm/streamlit@1.28.1/',
  'https://cdn.plot.ly/plotly-latest.min.js'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('📦 Cache ouvert et ajout des fichiers');
      return cache.addAll(urlsToCache);
    })
  );
  self.skipWaiting(); // Prend la main immédiatement
});

// Activation du Service Worker
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log('🗑 Suppression ancien cache :', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  self.clients.claim(); // Contrôle immédiat des pages
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      // Retourne depuis le cache si dispo
      if (response) {
        return response;
      }

      // Sinon, on va sur le réseau
      return fetch(event.request).then(networkResponse => {
        // Vérifie la validité de la réponse
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type !== 'basic') {
          return networkResponse;
        }

        // Clone et met en cache la réponse
        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      });
    })
  );
});
