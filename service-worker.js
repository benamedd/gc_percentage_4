self.addEventListener('install', event => {
    event.waitUntil(
        caches.open('bioinfo-cache-v1').then(cache => {
            return cache.addAll([
                '/gc_percentage_4/',
                '/gc_percentage_4/index.html',
                '/gc_percentage_4/manifest.json',
                '/gc_percentage_4/192x192.png',
                '/gc_percentage_4/512x512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
