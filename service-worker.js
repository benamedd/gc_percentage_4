const CACHE_NAME = 'dna-calculator-v3'; // Change à chaque mise à jour
const urlsToCache = [
  '/', // page principale
  '/manifest.json',
  '/192x192.png',
  '/512x512.png'
];

// Installation du Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log('📦 Cache ouvert');
      return Promise.allSettled(
        urlsToCache.map(url => cache.add(url).catch(err => console.warn('⚠️ Ressource non cachée :', url, err)))
      );
    })
  );
  self.skipWaiting(); // Active le SW immédiatement
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
  self.clients.claim(); // Contrôle immédiat des pages ouvertes
});

// Interception des requêtes
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => {
      if (response) {
        return response; // Retourne depuis le cache
      }

      // Sinon va chercher sur le réseau et met en cache si possible
      return fetch(event.request).then(networkResponse => {
        if (!networkResponse || networkResponse.status !== 200 || networkResponse.type === 'opaque') {
          return networkResponse;
        }

        const responseToCache = networkResponse.clone();
        caches.open(CACHE_NAME).then(cache => {
          cache.put(event.request, responseToCache);
        });

        return networkResponse;
      }).catch(() => {
        // Ici tu peux renvoyer une page offline par défaut
      });
    })
  );
});
