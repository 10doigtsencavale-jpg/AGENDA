// Service worker — AGENDA
// Pages : réseau d'abord (pour toujours voir les concerts à jour), cache en secours hors connexion.
// Affiches (ev-/th-, noms uniques) : cache d'abord. Pictos et autres images : réseau d'abord, cache en secours (pour voir les nouveautés).
const CACHE = "agenda-chansigne-v3"; // v3 : purge les anciens caches (anciens pictos restés en mémoire)
const SHELL = ["./", "index.html", "manifest.json", "icon-192.png", "icon-512.png", "mentions-legales.html", "confidentialite.html", "cgu.html"];
self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if(req.method !== "GET") return;
  const url = new URL(req.url);
  if(url.origin !== location.origin) return;
  if(req.mode === "navigate"){
    e.respondWith(fetch(req).then(r => { if(r.ok){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return r; })
      .catch(() => caches.match(req).then(hit => hit || caches.match("index.html"))));
    return;
  }
  if(!/\/(ev|th)-[0-9a-f]+\.jpg$/.test(url.pathname)){
    e.respondWith(fetch(req).then(r => { if(r.ok){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); } return r; })
      .catch(() => caches.match(req)));
    return;
  }
  e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(r => {
    if(r.ok){ const copy = r.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return r;
  })));
});
