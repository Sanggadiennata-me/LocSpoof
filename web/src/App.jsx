import React, { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { MapViewer } from './components/MapViewer';
import { ControlPanel } from './components/ControlPanel';
import { DeviceModeSelector } from './components/DeviceModeSelector';
import { KeyAuthModal } from './components/KeyAuthModal';
import { KeyGeneratorModal } from './components/KeyGeneratorModal';
import { reverseGeocode } from './services/universalSpoofer';
import { verifyLicenseKey } from './services/cryptoKey';

export default function App() {
  // Auth Session State
  const [session, setSession] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showKeyGenModal, setShowKeyGenModal] = useState(false);

  // Coordinate & Spoofing State
  const [targetCoords, setTargetCoords] = useState({ lat: -6.175392, lon: 106.827153 });
  const [addressInfo, setAddressInfo] = useState({
    displayName: 'Monumen Nasional, Gambir, Jakarta Pusat, DKI Jakarta, Indonesia',
    city: 'Jakarta Pusat',
    country: 'Indonesia'
  });
  const [isSpoofing, setIsSpoofing] = useState(false);
  const [spoofedCoords, setSpoofedCoords] = useState(null);
  const [toastMessage, setToastMessage] = useState(null);

  // Check saved license on mount
  useEffect(() => {
    const savedKey = localStorage.getItem('locspoof_license_key');
    if (savedKey) {
      const res = verifyLicenseKey(savedKey);
      if (res.valid) {
        setSession(res.payload);
      } else {
        localStorage.removeItem('locspoof_license_key');
        setShowAuthModal(true);
      }
    } else {
      setShowAuthModal(true);
    }
  }, []);

  // Update reverse geocode whenever targetCoords change
  useEffect(() => {
    let active = true;
    const fetchAddress = async () => {
      const info = await reverseGeocode(targetCoords.lat, targetCoords.lon);
      if (active) {
        setAddressInfo(info);
      }
    };
    fetchAddress();
    return () => {
      active = false;
    };
  }, [targetCoords.lat, targetCoords.lon]);

  const showToast = (msg) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Handlers
  const handleAuthenticated = (payload) => {
    setSession(payload);
    setShowAuthModal(false);
    showToast(`Selamat datang, ${payload.sub}! Lisensi aktif.`);
  };

  const handleLogout = () => {
    localStorage.removeItem('locspoof_license_key');
    setSession(null);
    setShowAuthModal(true);
    showToast("Anda telah keluar. Masukkan lisensi baru.");
  };

  const handleLocationSelect = ({ lat, lon, name }) => {
    setTargetCoords({ lat, lon });
    if (name) {
      setAddressInfo((prev) => ({ ...prev, displayName: name }));
    }
  };

  const handleSelectPreset = (preset) => {
    setTargetCoords({ lat: preset.lat, lon: preset.lon });
    setAddressInfo({
      displayName: `${preset.name}, ${preset.country}`,
      city: preset.name,
      country: preset.country
    });
    showToast(`Dipusatkan ke: ${preset.name}`);
  };

  const handleTeleport = () => {
    setIsSpoofing(true);
    setSpoofedCoords(targetCoords);
    showToast(`🚀 Berhasil teleport ke: ${targetCoords.lat.toFixed(5)}, ${targetCoords.lon.toFixed(5)}!`);
  };

  const handleReset = () => {
    setIsSpoofing(false);
    setSpoofedCoords(null);
    showToast("Lokasi telah di-reset ke kondisi normal.");
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#ecf0f1]">
      
      {/* Top Navbar */}
      <Navbar
        session={session}
        isSpoofing={isSpoofing}
        spoofedCoords={spoofedCoords}
        onOpenKeyGen={() => setShowKeyGenModal(true)}
        onLogout={handleLogout}
      />

      {/* Main Container */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
        
        {/* Top Info Banner */}
        <div className="bg-[#ffffff] border-2 border-[#2c3e50] shadow-flat p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className={`w-3.5 h-3.5 border-2 border-[#2c3e50] ${isSpoofing ? 'bg-[#2ecc71] animate-ping' : 'bg-[#95a5a6]'}`} />
            <div>
              <span className="font-extrabold text-xs uppercase tracking-wider text-[#2c3e50]">
                {isSpoofing ? 'STATUS: LOKASI AKTIF DI-SPOOF' : 'STATUS: SIAP MENGUBAH LOKASI'}
              </span>
              <p className="text-xs text-[#7f8c8d] font-semibold mt-0.5">
                {isSpoofing
                  ? `Device kini terkonfigurasi pada koordinat: ${spoofedCoords?.lat.toFixed(6)}, ${spoofedCoords?.lon.toFixed(6)}`
                  : 'Klik di mana saja pada peta atau cari tempat untuk langsung memilih target lokasi baru.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <span className="text-[11px] font-extrabold uppercase px-2 py-1 bg-[#ecf0f1] border border-[#2c3e50] text-[#2c3e50]">
              Mode: Serverless Web
            </span>
          </div>
        </div>

        {/* 2-Column Responsive Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Left Column: Interactive Map (7 Cols on desktop) */}
          <div className="lg:col-span-7 space-y-6">
            <MapViewer
              targetCoords={targetCoords}
              isSpoofing={isSpoofing}
              onLocationSelect={handleLocationSelect}
            />

            {/* Device Integration Component */}
            <DeviceModeSelector
              targetCoords={targetCoords}
              isSpoofing={isSpoofing}
            />
          </div>

          {/* Right Column: Control Panel & Presets (5 Cols on desktop) */}
          <div className="lg:col-span-5 space-y-6">
            <ControlPanel
              targetCoords={targetCoords}
              addressInfo={addressInfo}
              isSpoofing={isSpoofing}
              onTeleport={handleTeleport}
              onReset={handleReset}
              onSelectPreset={handleSelectPreset}
              onManualCoordinateChange={(lat, lon) => setTargetCoords({ lat, lon })}
            />
          </div>

        </div>

      </main>

      {/* Footer */}
      <footer className="bg-white border-t-2 border-[#2c3e50] py-4 mt-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between text-xs font-semibold text-[#7f8c8d] gap-2">
          <div>
            LocSpoof Web &bull; Universal Location Simulation &bull; <strong className="text-[#2c3e50]">Flat Design GUI</strong>
          </div>
          <div className="text-[11px]">
            Zero-Database Cryptographic Verification &bull; Built with React &amp; Tailwind
          </div>
        </div>
      </footer>

      {/* Toast Notification */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 animate-bounce">
          <div className="bg-[#2c3e50] text-white border-2 border-white shadow-flat px-4 py-3 font-bold text-xs sm:text-sm flex items-center gap-2">
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

      {/* Auth Modal */}
      <KeyAuthModal
        isOpen={showAuthModal}
        onAuthenticated={handleAuthenticated}
      />

      {/* Key Generator Modal (Owner Only) */}
      <KeyGeneratorModal
        isOpen={showKeyGenModal}
        onClose={() => setShowKeyGenModal(false)}
      />

    </div>
  );
}
