import React, { useState } from 'react';
import { 
  Rocket, 
  RotateCcw, 
  ExternalLink, 
  Download, 
  MapPin, 
  Globe, 
  Compass, 
  Check, 
  Copy,
  ChevronDown,
  ChevronUp
} from 'lucide-react';
import { POPULAR_PRESETS, downloadGpxFile } from '../services/universalSpoofer';

export function ControlPanel({ 
  targetCoords, 
  addressInfo, 
  isSpoofing, 
  onTeleport, 
  onReset, 
  onSelectPreset,
  onManualCoordinateChange 
}) {
  const [copied, setCopied] = useState(false);
  const [showManualInput, setShowManualInput] = useState(false);
  const [manualLat, setManualLat] = useState('');
  const [manualLon, setManualLon] = useState('');

  const coordString = `${targetCoords.lat.toFixed(6)}, ${targetCoords.lon.toFixed(6)}`;

  const handleCopy = () => {
    navigator.clipboard.writeText(coordString);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleOpenGoogleMaps = () => {
    const url = `https://www.google.com/maps/@${targetCoords.lat},${targetCoords.lon},17z`;
    window.open(url, '_blank');
  };

  const handleApplyManual = (e) => {
    e.preventDefault();
    const lat = parseFloat(manualLat);
    const lon = parseFloat(manualLon);
    if (!isNaN(lat) && !isNaN(lon) && lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180) {
      onManualCoordinateChange(lat, lon);
      setShowManualInput(false);
    } else {
      alert("Koordinat tidak valid! Latitude (-90 s/d 90), Longitude (-180 s/d 180)");
    }
  };

  return (
    <div className="space-y-4">

      {/* Target Location Card */}
      <div className="flat-card p-4 sm:p-5">
        <div className="flex items-center justify-between border-b-2 border-[#2c3e50] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-[#3498db] border-2 border-[#2c3e50] flex items-center justify-center text-white">
              <MapPin className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="font-extrabold text-sm sm:text-base text-[#2c3e50] uppercase tracking-wide">
                Target Koordinat
              </h2>
              <span className="text-[11px] font-semibold text-[#7f8c8d]">
                {isSpoofing ? 'Status: Terpasang di Device' : 'Status: Siap di-teleport'}
              </span>
            </div>
          </div>

          <button
            onClick={() => setShowManualInput(!showManualInput)}
            className="text-xs font-bold text-[#3498db] hover:underline flex items-center gap-1"
          >
            <span>Input Manual</span>
            {showManualInput ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* Manual Input Dropdown */}
        {showManualInput && (
          <form onSubmit={handleApplyManual} className="bg-[#ecf0f1] p-3 border-2 border-[#2c3e50] mb-4 space-y-2">
            <div className="grid grid-cols-2 gap-2">
              <div>
                <label className="text-[10px] font-extrabold uppercase text-[#2c3e50] block mb-1">Latitude</label>
                <input
                  type="number"
                  step="any"
                  value={manualLat}
                  onChange={(e) => setManualLat(e.target.value)}
                  placeholder="-6.175392"
                  className="flat-input w-full text-xs"
                  required
                />
              </div>
              <div>
                <label className="text-[10px] font-extrabold uppercase text-[#2c3e50] block mb-1">Longitude</label>
                <input
                  type="number"
                  step="any"
                  value={manualLon}
                  onChange={(e) => setManualLon(e.target.value)}
                  placeholder="106.827153"
                  className="flat-input w-full text-xs"
                  required
                />
              </div>
            </div>
            <button type="submit" className="flat-btn-primary w-full !py-1.5 text-xs uppercase font-extrabold">
              Terapkan Koordinat
            </button>
          </form>
        )}

        {/* Current Active Coordinates Box */}
        <div className="bg-[#f8fafc] border-2 border-[#2c3e50] p-3 mb-3">
          <div className="flex items-center justify-between">
            <span className="text-[10px] font-extrabold uppercase text-[#7f8c8d] tracking-wider">
              Latitude / Longitude (WGS 84)
            </span>
            <button
              onClick={handleCopy}
              className="text-[#3498db] hover:text-[#2980b9] text-xs font-bold flex items-center gap-1"
            >
              {copied ? <Check className="w-3.5 h-3.5 text-[#27ae60]" /> : <Copy className="w-3.5 h-3.5" />}
              <span>{copied ? 'Tersalin' : 'Salin'}</span>
            </button>
          </div>
          <div className="text-base sm:text-lg font-extrabold font-mono text-[#2c3e50] tracking-tight mt-1">
            {coordString}
          </div>
        </div>

        {/* Geocoded Address Box */}
        <div className="bg-[#f8fafc] border-2 border-[#2c3e50] p-3 mb-5">
          <div className="text-[10px] font-extrabold uppercase text-[#7f8c8d] tracking-wider mb-1 flex items-center gap-1">
            <Globe className="w-3 h-3 text-[#1abc9c]" />
            <span>Alamat / Lokasi Terdeteksi</span>
          </div>
          <div className="text-xs sm:text-sm font-semibold text-[#2c3e50] leading-snug">
            {addressInfo?.displayName || 'Memuat informasi alamat...'}
          </div>
        </div>

        {/* Primary Action Buttons */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <button
            onClick={onTeleport}
            className={`w-full !py-3 text-sm uppercase tracking-wide flex items-center justify-center gap-2 ${
              isSpoofing ? 'flat-btn-blue' : 'flat-btn-primary'
            }`}
          >
            <Rocket className="w-5 h-5 stroke-[2.5]" />
            <span>{isSpoofing ? 'UPDATE TELEPORT' : 'TELEPORT SEKARANG'}</span>
          </button>

          <button
            onClick={onReset}
            disabled={!isSpoofing}
            className={`w-full !py-3 text-sm uppercase tracking-wide flex items-center justify-center gap-2 ${
              isSpoofing ? 'flat-btn-danger' : 'flat-btn-white opacity-50 cursor-not-allowed'
            }`}
          >
            <RotateCcw className="w-5 h-5 stroke-[2.5]" />
            <span>RESET LOKASI NORMAL</span>
          </button>
        </div>

        {/* Secondary Utility Links */}
        <div className="grid grid-cols-2 gap-2 mt-3 pt-3 border-t-2 border-[#ecf0f1]">
          <button
            onClick={handleOpenGoogleMaps}
            className="flat-btn-white !py-1.5 text-xs font-bold flex items-center justify-center gap-1.5 text-[#2c3e50]"
          >
            <ExternalLink className="w-3.5 h-3.5 text-[#3498db]" />
            <span>Buka Google Maps</span>
          </button>

          <button
            onClick={() => downloadGpxFile(targetCoords.lat, targetCoords.lon, addressInfo?.city || 'LocSpoof')}
            className="flat-btn-white !py-1.5 text-xs font-bold flex items-center justify-center gap-1.5 text-[#2c3e50]"
          >
            <Download className="w-3.5 h-3.5 text-[#27ae60]" />
            <span>Download GPX</span>
          </button>
        </div>

      </div>

      {/* Preset Landmarks Card */}
      <div className="flat-card p-4">
        <div className="text-xs font-extrabold uppercase text-[#2c3e50] mb-3 flex items-center gap-1.5 border-b-2 border-[#2c3e50] pb-2">
          <Compass className="w-4 h-4 text-[#e67e22]" />
          <span>Preset Lokasi Populer (1-Klik Pindah)</span>
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-2 gap-2">
          {POPULAR_PRESETS.map((preset, idx) => (
            <button
              key={idx}
              onClick={() => onSelectPreset(preset)}
              className="text-left px-2.5 py-2 border border-[#2c3e50] bg-white hover:bg-[#1abc9c] hover:text-white transition-all shadow-flat-sm group"
            >
              <div className="text-xs font-bold truncate group-hover:text-white text-[#2c3e50]">
                {preset.name}
              </div>
              <div className="text-[10px] font-semibold text-[#7f8c8d] group-hover:text-white/90">
                {preset.country}
              </div>
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
