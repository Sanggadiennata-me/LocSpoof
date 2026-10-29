import React, { useEffect, useRef, useState } from 'react';
import L from 'leaflet';
import { Search, Layers, Compass, Loader2, Navigation, Crosshair } from 'lucide-react';
import { searchLocations, reverseGeocode } from '../services/universalSpoofer';

// Custom Flat SVG Marker Icon
const createFlatIcon = (isSpoofed) => {
  const color = isSpoofed ? '#2ecc71' : '#e74c3c';
  const shadowColor = '#2c3e50';
  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="40" height="48" viewBox="0 0 24 28">
      <path d="M12 2C7.58 2 4 5.58 4 10c0 5.25 8 16 8 16s8-10.75 8-16c0-4.42-3.58-8-8-8z" 
            fill="${color}" stroke="${shadowColor}" stroke-width="2"/>
      <circle cx="12" cy="10" r="3.5" fill="#ffffff" stroke="${shadowColor}" stroke-width="1.5"/>
    </svg>
  `;
  return L.divIcon({
    className: 'custom-flat-pin',
    html: svg,
    iconSize: [40, 48],
    iconAnchor: [20, 46],
    popupAnchor: [0, -40]
  });
};

const TILE_PROVIDERS = {
  googleRoad: {
    name: 'Google Maps Jalan',
    url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    maxZoom: 20
  },
  googleSat: {
    name: 'Google Maps Satelit',
    url: 'https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    maxZoom: 20
  },
  googleHybrid: {
    name: 'Google Maps Hybrid',
    url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
    subdomains: ['mt0', 'mt1', 'mt2', 'mt3'],
    maxZoom: 20
  },
  osm: {
    name: 'OpenStreetMap',
    url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    subdomains: ['a', 'b', 'c'],
    maxZoom: 19
  }
};

export function MapViewer({ targetCoords, isSpoofing, onLocationSelect }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markerRef = useRef(null);
  const tileLayerRef = useRef(null);

  const [activeTile, setActiveTile] = useState('googleRoad');
  const [showLayerMenu, setShowLayerMenu] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isLocating, setIsLocating] = useState(false);

  // Initialize Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const initialLat = targetCoords?.lat || -6.175392;
      const initialLon = targetCoords?.lon || 106.827153;

      const map = L.map(mapContainerRef.current, {
        center: [initialLat, initialLon],
        zoom: 14,
        zoomControl: false // custom flat zoom controls
      });

      const provider = TILE_PROVIDERS[activeTile];
      const tile = L.tileLayer(provider.url, {
        subdomains: provider.subdomains,
        maxZoom: provider.maxZoom,
        attribution: '&copy; Google / OSM / LocSpoof'
      }).addTo(map);

      tileLayerRef.current = tile;

      const marker = L.marker([initialLat, initialLon], {
        icon: createFlatIcon(isSpoofing),
        draggable: true
      }).addTo(map);

      marker.on('dragend', async (e) => {
        const { lat, lng } = e.target.getLatLng();
        onLocationSelect({ lat, lon: lng });
      });

      markerRef.current = marker;

      // Click on map to select location
      map.on('click', (e) => {
        const { lat, lng } = e.latlng;
        marker.setLatLng([lat, lng]);
        onLocationSelect({ lat, lon: lng });
      });

      mapInstanceRef.current = map;
    }

    return () => {
      // Cleanup on unmount
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  // Update marker position and icon when targetCoords or isSpoofing changes
  useEffect(() => {
    if (!mapInstanceRef.current || !markerRef.current || !targetCoords) return;

    const currentPos = markerRef.current.getLatLng();
    if (Math.abs(currentPos.lat - targetCoords.lat) > 0.00001 || Math.abs(currentPos.lng - targetCoords.lon) > 0.00001) {
      markerRef.current.setLatLng([targetCoords.lat, targetCoords.lon]);
      mapInstanceRef.current.panTo([targetCoords.lat, targetCoords.lon], { animate: true });
    }
    markerRef.current.setIcon(createFlatIcon(isSpoofing));
  }, [targetCoords, isSpoofing]);

  // Handle Tile Provider Switch
  const handleSwitchTile = (providerKey) => {
    if (!mapInstanceRef.current) return;
    const provider = TILE_PROVIDERS[providerKey];
    if (tileLayerRef.current) {
      mapInstanceRef.current.removeLayer(tileLayerRef.current);
    }
    const newTile = L.tileLayer(provider.url, {
      subdomains: provider.subdomains,
      maxZoom: provider.maxZoom,
      attribution: '&copy; Google / OSM / LocSpoof'
    }).addTo(mapInstanceRef.current);

    tileLayerRef.current = newTile;
    setActiveTile(providerKey);
    setShowLayerMenu(false);
  };

  // Search Places Handler
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setIsSearching(true);
    try {
      const results = await searchLocations(searchQuery);
      setSearchResults(results);
    } catch {
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const handleSelectSearchResult = (res) => {
    if (!mapInstanceRef.current || !markerRef.current) return;
    mapInstanceRef.current.setView([res.lat, res.lon], 16, { animate: true });
    markerRef.current.setLatLng([res.lat, res.lon]);
    onLocationSelect({ lat: res.lat, lon: res.lon, name: res.name });
    setSearchResults([]);
    setSearchQuery(res.name.split(',')[0]);
  };

  // Locate Current Real Position
  const handleLocateMe = () => {
    if (!navigator.geolocation) {
      alert("Browser tidak mendukung geolokasi.");
      return;
    }
    setIsLocating(true);
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setIsLocating(false);
        const { latitude, longitude } = pos.coords;
        if (mapInstanceRef.current && markerRef.current) {
          mapInstanceRef.current.setView([latitude, longitude], 16, { animate: true });
          markerRef.current.setLatLng([latitude, longitude]);
          onLocationSelect({ lat: latitude, lon: longitude });
        }
      },
      (err) => {
        setIsLocating(false);
        alert("Gagal membaca GPS saat ini: " + err.message);
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );
  };

  return (
    <div className="relative w-full h-[450px] lg:h-[600px] border-2 border-[#2c3e50] shadow-flat bg-[#ecf0f1] overflow-hidden">
      
      {/* Map Element Container */}
      <div ref={mapContainerRef} className="w-full h-full" />

      {/* Floating Search Bar */}
      <div className="absolute top-4 left-4 right-16 sm:right-auto sm:w-96 z-30">
        <form onSubmit={handleSearch} className="flex items-center">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Cari tempat (cth: Monas, Tokyo, Kuta)..."
            className="flat-input w-full text-xs sm:text-sm py-2 px-3 shadow-flat-sm border-r-0"
          />
          <button
            type="submit"
            disabled={isSearching}
            className="flat-btn-primary !px-3 !py-2 text-xs uppercase"
            title="Cari Tempat"
          >
            {isSearching ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
          </button>
        </form>

        {/* Search Results Dropdown */}
        {searchResults.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white border-2 border-[#2c3e50] shadow-flat z-40 max-h-60 overflow-y-auto">
            {searchResults.map((res, idx) => (
              <button
                key={idx}
                type="button"
                onClick={() => handleSelectSearchResult(res)}
                className="w-full text-left px-3 py-2 text-xs font-semibold hover:bg-[#1abc9c] hover:text-white border-b border-[#ecf0f1] flex items-start gap-2 transition-colors"
              >
                <Navigation className="w-3.5 h-3.5 mt-0.5 flex-shrink-0 text-[#3498db]" />
                <span className="line-clamp-2">{res.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Top Right Controls: Layer Switcher & Locate Me */}
      <div className="absolute top-4 right-4 z-30 flex flex-col gap-2">
        {/* Layer Switcher */}
        <div className="relative">
          <button
            type="button"
            onClick={() => setShowLayerMenu(!showLayerMenu)}
            className="flat-btn-white !p-2 shadow-flat-sm"
            title="Ganti Jenis Peta / Satelit"
          >
            <Layers className="w-5 h-5 text-[#2c3e50]" />
          </button>

          {showLayerMenu && (
            <div className="absolute right-0 top-full mt-2 w-48 bg-white border-2 border-[#2c3e50] shadow-flat z-50 p-1">
              <div className="text-[10px] font-extrabold uppercase text-[#7f8c8d] px-2 py-1">
                Gaya Tampilan Peta
              </div>
              {Object.entries(TILE_PROVIDERS).map(([key, provider]) => (
                <button
                  key={key}
                  type="button"
                  onClick={() => handleSwitchTile(key)}
                  className={`w-full text-left px-3 py-1.5 text-xs font-bold flex items-center justify-between transition-colors ${
                    activeTile === key ? 'bg-[#1abc9c] text-white' : 'hover:bg-[#ecf0f1] text-[#2c3e50]'
                  }`}
                >
                  <span>{provider.name}</span>
                  {activeTile === key && <span className="text-[10px] font-extrabold">✓</span>}
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Locate Real GPS */}
        <button
          type="button"
          onClick={handleLocateMe}
          disabled={isLocating}
          className="flat-btn-white !p-2 shadow-flat-sm"
          title="Pusatkan ke Lokasi Saya Saat Ini"
        >
          {isLocating ? (
            <Loader2 className="w-5 h-5 text-[#3498db] animate-spin" />
          ) : (
            <Crosshair className="w-5 h-5 text-[#2c3e50]" />
          )}
        </button>

        {/* Flat Zoom Controls */}
        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomIn()}
          className="flat-btn-white !p-2 shadow-flat-sm font-extrabold text-sm"
          title="Perbesar Peta"
        >
          +
        </button>
        <button
          type="button"
          onClick={() => mapInstanceRef.current?.zoomOut()}
          className="flat-btn-white !p-2 shadow-flat-sm font-extrabold text-sm"
          title="Perkecil Peta"
        >
          -
        </button>
      </div>

      {/* Bottom Map Helper Banner */}
      <div className="absolute bottom-2 left-2 z-30 pointer-events-none">
        <div className="bg-[#2c3e50] text-white text-[11px] font-bold px-3 py-1 border border-white shadow-flat-sm flex items-center gap-1.5">
          <span className="w-2 h-2 bg-[#1abc9c] inline-block"></span>
          <span>Klik atau seret pin merah untuk langsung memilih lokasi target</span>
        </div>
      </div>

    </div>
  );
}
