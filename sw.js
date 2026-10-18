const CACHE = 'efirio-alpha-0-3-0';
const APP_SHELL = [
  './',
  './index.html',
  './styles.css',
  './app.js',
  './manifest.webmanifest',
  './collections/efirio-paper/package.json',
  './collections/efirio-paper/icons/grid.svg',
  './collections/efirio-paper/placeholders/wallpapers/README.md',
  './collections/efirio-signature/package.json',
  './collections/efirio-signature/assets/wallpaper-portrait.svg',
  './collections/efirio-signature/assets/wallpaper-landscape.svg',
  './collections/efirio-signature/assets/collection-cover.svg',
  './collections/efirio-signature/assets/preview.svg'
  ,'./collections/efirio-signature/assets/wallpaper-portrait.png'
  ,'./collections/efirio-signature/assets/wallpaper-landscape.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE)
      .then(cache => cache.addAll(APP_SHELL))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));

self.addEventListener('fetch', event => {
  if (event.request.method !== 'GET') return;
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request).then(response => {
      if (!response || response.status !== 200 || response.type === 'opaque') return response;
      const copy = response.clone();
      caches.open(CACHE).then(cache => cache.put(event.request, copy));
      return response;
    }))
  );
});
