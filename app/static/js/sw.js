const CACHE_NAME = 'courage-fx-v1';
const OFFLINE_URL = '/offline';

const ASSETS_TO_CACHE = [
    '/',
    '/offline',
    '/static/css/style.css',
    '/static/css/dashboard.css',
    '/static/js/app.js',
    '/static/js/dashboard.js',
    '/static/js/profile.js',
    '/static/js/settings.js',
    '/static/images/logo.png',
    '/static/images/icons/icon-72x72.png',
    '/static/images/icons/icon-96x96.png',
    '/static/images/icons/icon-128x128.png',
    '/static/images/icons/icon-144x144.png',
    '/static/images/icons/icon-152x152.png',
    '/static/images/icons/icon-192x192.png',
    '/static/images/icons/icon-384x384.png',
    '/static/images/icons/icon-512x512.png',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/boxicons@2.1.4/css/boxicons.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js'
];

// Install event - cache assets
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                return cache.addAll(ASSETS_TO_CACHE);
            })
            .then(() => {
                return self.skipWaiting();
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            return self.clients.claim();
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    // Skip cross-origin requests
    if (!event.request.url.startsWith(self.location.origin)) {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                if (response) {
                    return response;
                }

                return fetch(event.request)
                    .then(response => {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response
                        const responseToCache = response.clone();

                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });

                        return response;
                    })
                    .catch(() => {
                        // If the network is unavailable, return the offline page
                        if (event.request.mode === 'navigate') {
                            return caches.match(OFFLINE_URL);
                        }
                    });
            })
    );
});

// Background sync for offline actions
self.addEventListener('sync', event => {
    if (event.tag === 'sync-trading-data') {
        event.waitUntil(syncTradingData());
    }
});

// Push notification handling
self.addEventListener('push', event => {
    const options = {
        body: event.data.text(),
        icon: '/static/images/icons/icon-192x192.png',
        badge: '/static/images/icons/icon-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'view',
                title: 'View'
            },
            {
                action: 'close',
                title: 'Close'
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification('Courage FX Alert', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'view') {
        event.waitUntil(
            clients.openWindow('/dashboard')
        );
    }
});

// Helper function for background sync
async function syncTradingData() {
    try {
        const cache = await caches.open(CACHE_NAME);
        const requests = await cache.keys();
        const tradingRequests = requests.filter(request => 
            request.url.includes('/api/trading/')
        );

        for (const request of tradingRequests) {
            try {
                await fetch(request);
                await cache.delete(request);
            } catch (error) {
                console.error('Error syncing request:', error);
            }
        }
    } catch (error) {
        console.error('Error in syncTradingData:', error);
    }
}
