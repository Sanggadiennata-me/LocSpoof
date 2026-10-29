/**
 * Universal Spoofer Engine & Utility Service
 * Provides multi-device spoofing, script injection, bookmarklets, and GPX generation.
 */

/**
 * Reverse geocode coordinates to human-readable address
 */
export async function reverseGeocode(lat, lon) {
  try {
    const url = `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lon}&zoom=18&addressdetails=1`;
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'LocSpoof-UniversalWeb/1.0'
      }
    });
    if (!res.ok) throw new Error("Geocoding failed");
    const data = await res.json();
    return {
      displayName: data.display_name || `${lat.toFixed(6)}, ${lon.toFixed(6)}`,
      city: data.address?.city || data.address?.town || data.address?.county || 'Unknown Area',
      country: data.address?.country || '',
      road: data.address?.road || '',
    };
  } catch (err) {
    return {
      displayName: `${lat.toFixed(6)}, ${lon.toFixed(6)}`,
      city: 'Unknown Area',
      country: '',
      road: '',
    };
  }
}

/**
 * Search location by query name (Geocoding search)
 */
export async function searchLocations(query) {
  if (!query || query.trim().length < 2) return [];
  try {
    const url = `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=6`;
    const res = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'User-Agent': 'LocSpoof-UniversalWeb/1.0'
      }
    });
    if (!res.ok) return [];
    const data = await res.json();
    return data.map(item => ({
      name: item.display_name,
      lat: parseFloat(item.lat),
      lon: parseFloat(item.lon),
      type: item.type,
    }));
  } catch {
    return [];
  }
}

/**
 * Generate a Universal Browser Geolocation Override Bookmarklet
 * Allows spoofing on ANY device (iPhone Safari, Android Chrome, Mac, Windows)
 * with zero installation and without connecting cables to a laptop!
 */
export function generateBookmarkletCode(lat, lon, accuracy = 5) {
  const code = `javascript:(function(){
    const targetLat = ${lat};
    const targetLon = ${lon};
    const targetAcc = ${accuracy};
    const fakePosition = {
      coords: {
        latitude: targetLat,
        longitude: targetLon,
        accuracy: targetAcc,
        altitude: 12.0,
        altitudeAccuracy: 1.0,
        heading: 0,
        speed: 0
      },
      timestamp: Date.now()
    };
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition = function(success) {
        setTimeout(() => success(fakePosition), 10);
      };
      navigator.geolocation.watchPosition = function(success) {
        setTimeout(() => success(fakePosition), 10);
        return 999999;
      };
    }
    const banner = document.createElement('div');
    banner.style = 'position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:9999999;background:#1abc9c;color:#fff;font-family:sans-serif;font-size:13px;font-weight:700;padding:8px 16px;border-radius:4px;box-shadow:3px 3px 0 #2c3e50;display:flex;align-items:center;gap:8px;';
    banner.innerHTML = '🎯 <span>LocSpoof Active: ' + targetLat.toFixed(5) + ', ' + targetLon.toFixed(5) + '</span>';
    document.body.appendChild(banner);
    setTimeout(() => banner.remove(), 4000);
  })();`;
  return code.replace(/\s+/g, ' ').trim();
}

/**
 * Generate and download GPX file for import into Mobile Mock Apps
 */
export function downloadGpxFile(lat, lon, locationName = "Spoofed Location") {
  const gpxContent = `<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="LocSpoof Web" xmlns="http://www.topografix.com/GPX/1/1">
  <wpt lat="${lat}" lon="${lon}">
    <name>${locationName}</name>
    <desc>Spoofed via LocSpoof Flat Web</desc>
    <sym>Pin</sym>
  </wpt>
</gpx>`;

  const blob = new Blob([gpxContent], { type: 'application/gpx+xml' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `locspoof_${lat.toFixed(4)}_${lon.toFixed(4)}.gpx`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

/**
 * Pre-defined World & Indonesia Landmark Presets
 */
export const POPULAR_PRESETS = [
  { name: "Monas, Jakarta", lat: -6.175392, lon: 106.827153, country: "Indonesia", category: "landmark" },
  { name: "Pantai Kuta, Bali", lat: -8.718492, lon: 115.168925, country: "Indonesia", category: "landmark" },
  { name: "Bundaran HI, Jakarta", lat: -6.195048, lon: 106.823028, country: "Indonesia", category: "city" },
  { name: "Shibuya Crossing, Tokyo", lat: 35.6595, lon: 139.7005, country: "Japan", category: "world" },
  { name: "Eiffel Tower, Paris", lat: 48.8584, lon: 2.2945, country: "France", category: "world" },
  { name: "Times Square, New York", lat: 40.7580, lon: -73.9855, country: "USA", category: "world" },
  { name: "Big Ben, London", lat: 51.5007, lon: -0.1246, country: "UK", category: "world" },
  { name: "Masjidil Haram, Mekkah", lat: 21.4225, lon: 39.8262, country: "Saudi Arabia", category: "world" },
  { name: "Sydney Opera House", lat: -33.8568, lon: 151.2153, country: "Australia", category: "world" },
  { name: "Marina Bay Sands, Singapore", lat: 1.2834, lon: 103.8607, country: "Singapore", category: "world" },
];
