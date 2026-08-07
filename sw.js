const CACHE_NAME = 'abarham-app-v1';
const ASSETS_TO_CACHE = [
    '/',
    '/manifest.json',
    'https://cdn.jsdelivr.net/npm/vazirmatn@33.0.3/Vazirmatn-font-face.css'
];

// ۱. نصب و ذخیره‌سازی اولیه فایل‌ها در کش
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
    self.skipWaiting();
});

// ۲. فعال‌سازی و پاک‌سازی کش‌های قدیمی در صورت به‌روزرسانی
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keys) => {
            return Promise.all(
                keys.map((key) => {
                    if (key !== CACHE_NAME) {
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// ۳. استراتژی درخواست‌ها: ابتدا تلاش برای دریافت آنلاین، در صورت عدم اتصال خواندن از کش
self.addEventListener('fetch', (event) => {
    // درخواست‌های مربوط به API پایتون را از فرآیند کش متنی استثنا می‌کنیم
    if (event.request.url.includes('/trips/') || event.request.url.includes('/participants/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // اگر پاسخ موفق بود، یک کپی در کش بروز می‌کنیم
                if (response.status === 200) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // اگر آفلاین بودیم، از فایل‌های ذخیره‌شده در کش استفاده کن
                return caches.match(event.request);
            })
    );
});