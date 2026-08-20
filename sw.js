const CACHE_NAME = 'abarham-cache-v1';
const STATIC_ASSETS = ['/', '/manifest.json', '/logo.png'];

self.addEventListener('install', (event) => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys()
            .then((keys) => Promise.all(
                keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
            ))
            .then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests
  if (event.request.method !== 'GET') {
    return; // let browser handle non-GET (network)
  }

  // Bypass caching for API routes
  const url = event.request.url;
  if (
    url.includes('/trips') ||
    url.includes('/participants') ||
    url.includes('/payments') ||
    url.includes('/login') ||
    url.includes('/api/')
  ) {
    return event.respondWith(
      fetch(event.request)
        .then(response => {
          if (!response.ok) throw new Error('API response not ok');
          return response;
        })
    );
  }

  // Otherwise, try network then cache
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Only cache successful responses
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, responseClone));
        }
        if (!response.ok) throw new Error('Network response not ok');
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
