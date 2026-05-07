// ══════════════════════════════════════════════════════════════
// VOLTIQ Service Worker — Offline-Modus
// Version: wird bei Änderungen hochgezählt → Cache wird erneuert
// ══════════════════════════════════════════════════════════════

var CACHE_NAME = 'voltiq-v2';

var FILES_TO_CACHE = [
  '../index.html',
  '../arc-studio.html',
  '../VOLTECH-lern-basis.html',
  '../VOLTECH-lern-extra.html',
  '../VOLTECH-mechatronik-pro.html',
  '../VOLTECH-sps.html',
  '../VOLTECH-berichtsheft.html',
  '../VOLTECH-tools2.html',
  '../pwa/manifest.json'
];

// ── INSTALL: alle Dateien in Cache laden ──────────────────────
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      console.log('[VOLTIQ SW] Cache wird befüllt...');
      return cache.addAll(FILES_TO_CACHE);
    }).then(function() {
      console.log('[VOLTIQ SW] Alle Dateien gecacht — Offline-Modus aktiv');
      // Sofort aktivieren ohne auf alte SW zu warten
      return self.skipWaiting();
    })
  );
});

// ── ACTIVATE: alten Cache löschen ────────────────────────────
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames
          .filter(function(name) { return name !== CACHE_NAME; })
          .map(function(name) {
            console.log('[VOLTIQ SW] Alter Cache gelöscht:', name);
            return caches.delete(name);
          })
      );
    }).then(function() {
      // Sofort alle Clients übernehmen
      return self.clients.claim();
    })
  );
});

// ── FETCH: Cache-First Strategie ─────────────────────────────
// Zuerst aus Cache → bei Fehler Netzwerk → bei Fehler Fallback
self.addEventListener('fetch', function(event) {
  // Nur GET-Anfragen abfangen
  if (event.request.method !== 'GET') return;

  // Externe Ressourcen (Google Fonts etc.) durchlassen
  var url = new URL(event.request.url);
  if (url.origin !== self.location.origin) {
    // Externe Fonts: Network-First mit Cache-Fallback
    if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') {
      event.respondWith(
        caches.open(CACHE_NAME + '-fonts').then(function(cache) {
          return fetch(event.request).then(function(response) {
            cache.put(event.request, response.clone());
            return response;
          }).catch(function() {
            return cache.match(event.request);
          });
        })
      );
    }
    return;
  }

  // Lokale Dateien: Cache-First
  event.respondWith(
    caches.match(event.request).then(function(cached) {
      if (cached) {
        // Aus Cache bedienen + im Hintergrund aktualisieren (Stale-While-Revalidate)
        var fetchPromise = fetch(event.request).then(function(networkResponse) {
          if (networkResponse && networkResponse.status === 200) {
            caches.open(CACHE_NAME).then(function(cache) {
              cache.put(event.request, networkResponse.clone());
            });
          }
          return networkResponse;
        }).catch(function() { /* Offline — Cache bleibt */ });

        return cached;
      }

      // Nicht im Cache: Netzwerk versuchen
      return fetch(event.request).then(function(networkResponse) {
        if (networkResponse && networkResponse.status === 200) {
          var responseToCache = networkResponse.clone();
          caches.open(CACHE_NAME).then(function(cache) {
            cache.put(event.request, responseToCache);
          });
        }
        return networkResponse;
      }).catch(function() {
        // Offline + nicht gecacht → index.html als Fallback
        return caches.match('../index.html');
      });
    })
  );
});

// ── MESSAGE: Cache manuell leeren (vom UI aufrufbar) ─────────
self.addEventListener('message', function(event) {
  if (event.data === 'skipWaiting') {
    self.skipWaiting();
  }
  if (event.data === 'clearCache') {
    caches.delete(CACHE_NAME).then(function() {
      console.log('[VOLTIQ SW] Cache geleert');
    });
  }
});
