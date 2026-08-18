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
    // فقط درخواست‌های GET را کش می‌کنیم؛ درخواست‌های POST/PUT/DELETE به API باید
    // همیشه مستقیم به شبکه بروند تا خطای واضح بگیرند اگر آفلاین هستیم.
    if (event.request.method !== 'GET') {
        return;
    }

    // درخواست‌های به /trips, /login و هر درخواستی با /api/ را کش نکن
    if (event.request.url.includes('/trips') ||
        event.request.url.includes('/login') ||
        event.request.url.includes('/api/')) {
        return fetch(event.request);
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // فقط پاسخ‌های با status 200 را کش کن
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => cache.put(event.request, responseClone));
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});
