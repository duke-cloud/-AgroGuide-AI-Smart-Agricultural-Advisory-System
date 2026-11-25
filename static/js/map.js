/* ═══════════════════════════════════════════════════════════════
   AgroGuide AI — Leaflet Map Helper

   Tile strategy (fixes the "Access blocked" OSM tile error):
   1. OpenStreetMap is the default, sent with a proper Referer
      (referrerPolicy option + server header + <meta> tag).
   2. If OSM tiles keep failing (blocked / offline / rate-limited),
      the map automatically switches to CARTO Voyager.
   3. Esri satellite imagery is available via the layer switcher,
      which is handy for viewing actual farmland.
═══════════════════════════════════════════════════════════════ */
function initFarmMap(lat, lon, containerId, editable) {
  if (!window.L) {
    console.warn('AgroGuide: Leaflet failed to load — map disabled');
    return;
  }
  const el = document.getElementById(containerId);
  if (!el) return;

  // Default: Abuja, FCT
  lat = parseFloat(lat) || 9.0579;
  lon = parseFloat(lon) || 7.4951;

  const map = L.map(containerId, { scrollWheelZoom: !!editable }).setView([lat, lon], 13);

  /* ── Base layers ───────────────────────────────────────────── */
  const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    referrerPolicy: 'strict-origin-when-cross-origin',   // send Referer (required by OSM)
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
  });

  const carto = L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
    subdomains: 'abcd',
    maxZoom: 20,
    attribution: '&copy; OpenStreetMap contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
  });

  const satellite = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 19,
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics',
    });

  osm.addTo(map);
  L.control.layers({
    'Street map': osm,
    'Street (alt)': carto,
    'Satellite': satellite,
  }, null, { position: 'topright', collapsed: true }).addTo(map);

  /* ── Auto-fallback: if OSM keeps erroring, switch to CARTO ─── */
  let osmErrors = 0;
  osm.on('tileerror', function () {
    osmErrors += 1;
    if (osmErrors >= 3 && map.hasLayer(osm)) {
      console.warn('AgroGuide: OpenStreetMap tiles failing — switching to CARTO');
      map.removeLayer(osm);
      carto.addTo(map);
    }
  });

  /* ── Farm marker ───────────────────────────────────────────── */
  const marker = L.marker([lat, lon], { draggable: !!editable }).addTo(map)
    .bindPopup('Farm Location').openPopup();

  if (editable) {
    marker.on('dragend', function (e) {
      const pos = e.target.getLatLng();
      const latIn = document.getElementById('id_latitude');
      const lonIn = document.getElementById('id_longitude');
      if (latIn) latIn.value = pos.lat.toFixed(6);
      if (lonIn) lonIn.value = pos.lng.toFixed(6);
    });

    // Click the map to move the marker
    map.on('click', function (e) {
      marker.setLatLng(e.latlng);
      const latIn = document.getElementById('id_latitude');
      const lonIn = document.getElementById('id_longitude');
      if (latIn) latIn.value = e.latlng.lat.toFixed(6);
      if (lonIn) lonIn.value = e.latlng.lng.toFixed(6);
    });

    // Browser geolocation
    const geoBtn = document.getElementById('geoLocBtn');
    if (geoBtn) {
      geoBtn.addEventListener('click', function () {
        if (!navigator.geolocation) {
          alert('Geolocation is not supported by this browser.');
          return;
        }
        navigator.geolocation.getCurrentPosition(function (pos) {
          const lt = pos.coords.latitude, ln = pos.coords.longitude;
          map.setView([lt, ln], 15);
          marker.setLatLng([lt, ln]);
          const latIn = document.getElementById('id_latitude');
          const lonIn = document.getElementById('id_longitude');
          if (latIn) latIn.value = lt.toFixed(6);
          if (lonIn) lonIn.value = ln.toFixed(6);
        }, () => alert('Could not get location. Please enter coordinates manually.'));
      });
    }
  }

  // Fix grey/partial tiles when the container is laid out after init
  setTimeout(() => map.invalidateSize(), 250);
  return map;
}

