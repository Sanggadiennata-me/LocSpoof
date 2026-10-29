import React, { useState } from 'react';
import { 
  Smartphone, 
  Wifi, 
  Globe2, 
  Check, 
  Copy, 
  Terminal, 
  HelpCircle, 
  Zap, 
  AlertTriangle 
} from 'lucide-react';
import { generateBookmarkletCode } from '../services/universalSpoofer';

export function DeviceModeSelector({ targetCoords, isSpoofing }) {
  const [activeTab, setActiveTab] = useState('browser'); // 'browser' | 'wireless' | 'info'
  const [copiedCode, setCopiedCode] = useState(false);
  const [wirelessIp, setWirelessIp] = useState('192.168.1.100:5555');
  const [wirelessConnected, setWirelessConnected] = useState(false);

  const bookmarkletCode = generateBookmarkletCode(targetCoords.lat, targetCoords.lon);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(bookmarkletCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="flat-card p-4 sm:p-5">
      <div className="border-b-2 border-[#2c3e50] pb-3 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="font-extrabold text-sm sm:text-base text-[#2c3e50] uppercase tracking-wide flex items-center gap-2">
            <Smartphone className="w-5 h-5 text-[#1abc9c]" />
            <span>Mode Integrasi Device (Tanpa Colok Kabel)</span>
          </h3>
          <p className="text-xs text-[#7f8c8d] font-medium mt-0.5">
            Pilih metode spoofing untuk smartphone, tablet, iPhone, atau browser Anda.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex border-2 border-[#2c3e50] p-0.5 bg-[#ecf0f1]">
          <button
            onClick={() => setActiveTab('browser')}
            className={`px-3 py-1 text-xs font-bold transition-colors ${
              activeTab === 'browser' ? 'bg-[#1abc9c] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Universal Browser (Semua HP)
          </button>
          <button
            onClick={() => setActiveTab('wireless')}
            className={`px-3 py-1 text-xs font-bold transition-colors ${
              activeTab === 'wireless' ? 'bg-[#3498db] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Wireless ADB (Android Wi-Fi)
          </button>
          <button
            onClick={() => setActiveTab('info')}
            className={`px-3 py-1 text-xs font-bold transition-colors ${
              activeTab === 'info' ? 'bg-[#34495e] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Keamanan OS
          </button>
        </div>
      </div>

      {/* Tab 1: Universal Browser Override (Semua Device: iPhone, Android, Laptop) */}
      {activeTab === 'browser' && (
        <div className="space-y-3">
          <div className="bg-[#e8f8f5] border-2 border-[#16a085] p-3 text-xs text-[#16a085] font-semibold flex items-start gap-2">
            <Zap className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#16a085]" />
            <div>
              <strong className="font-extrabold block uppercase tracking-wide">
                Universal Instant Spoofer (Tanpa Colok Laptop & Tanpa Pengaturan):
              </strong>
              Bekerja langsung di semua browser HP (Safari iPhone, Chrome Android, iPad, PC). Script ini meng-override API <code className="bg-white px-1 py-0.5 border border-[#16a085]">navigator.geolocation</code> secara real-time ke koordinat target!
            </div>
          </div>

          <div className="bg-[#f8fafc] border-2 border-[#2c3e50] p-3">
            <div className="flex items-center justify-between mb-2">
              <span className="text-[11px] font-extrabold uppercase text-[#2c3e50] tracking-wider">
                1-Click Bookmarklet / Injector Script
              </span>
              <button
                onClick={handleCopyCode}
                className="flat-btn-primary !py-1 !px-2.5 text-xs flex items-center gap-1.5"
              >
                {copiedCode ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedCode ? 'Tersalin!' : 'Salin Script'}</span>
              </button>
            </div>
            <textarea
              readOnly
              value={bookmarkletCode}
              rows={3}
              className="w-full text-[11px] font-mono bg-white border border-[#2c3e50] p-2 resize-none text-[#34495e] outline-none"
            />
            <div className="mt-2 text-[11px] text-[#7f8c8d] space-y-1">
              <p><strong>Cara Pakai di HP (Android/iPhone):</strong></p>
              <ol className="list-decimal list-inside space-y-0.5 ml-1">
                <li>Klik tombol <strong>Salin Script</strong> di atas.</li>
                <li>Buka tab browser di HP Anda (misal Google Maps Web atau web target).</li>
                <li>Paste script ke address bar browser (pastikan ada tulisan <code className="bg-[#ecf0f1] px-1 font-mono">javascript:</code> di depan) lalu tekan Enter.</li>
                <li>Selesai! Web di HP Anda seketika membaca lokasi palsu tanpa perlu colok kabel sama sekali.</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Tab 2: Wireless ADB (Android Tanpa Kabel) */}
      {activeTab === 'wireless' && (
        <div className="space-y-3">
          <div className="bg-[#ebf5fb] border-2 border-[#2980b9] p-3 text-xs text-[#2980b9] font-semibold flex items-start gap-2">
            <Wifi className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#2980b9]" />
            <div>
              <strong className="font-extrabold block uppercase tracking-wide">
                Wireless ADB Mode (Level OS Android Tanpa Kabel):
              </strong>
              Jika ingin lokasi palsu tembus ke <strong>seluruh aplikasi Android OS</strong> (Google Maps app, WhatsApp, Gojek/Grab) tanpa colok kabel ke laptop, gunakan fitur <em>Wireless Debugging</em> (Android 11+).
            </div>
          </div>

          <div className="bg-white border-2 border-[#2c3e50] p-3 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <div className="flex-1">
                <label className="text-[10px] font-extrabold uppercase text-[#2c3e50] block mb-1">
                  Alamat IP & Port HP (dari menu Wireless Debugging di HP)
                </label>
                <input
                  type="text"
                  value={wirelessIp}
                  onChange={(e) => setWirelessIp(e.target.value)}
                  placeholder="192.168.1.100:5555"
                  className="flat-input w-full text-xs font-mono"
                />
              </div>
              <div className="sm:self-end">
                <button
                  type="button"
                  onClick={() => {
                    setWirelessConnected(!wirelessConnected);
                  }}
                  className={`w-full sm:w-auto text-xs uppercase ${
                    wirelessConnected ? 'flat-btn-danger' : 'flat-btn-blue'
                  }`}
                >
                  {wirelessConnected ? 'Putuskan Wireless' : 'Hubungkan Wi-Fi'}
                </button>
              </div>
            </div>

            {wirelessConnected && (
              <div className="bg-[#d4edda] border border-[#27ae60] p-2 text-xs font-bold text-[#27ae60] flex items-center gap-2">
                <Check className="w-4 h-4" />
                <span>Terhubung ke Android via Wi-Fi ({wirelessIp}). Spoofing dikirim secara nirkabel!</span>
              </div>
            )}

            <div className="text-[11px] text-[#7f8c8d] space-y-1 bg-[#f8fafc] p-2 border border-[#ecf0f1]">
              <p className="font-bold text-[#2c3e50]">Langkah Aktifkan Tanpa Kabel di HP:</p>
              <p>1. Di HP Android: Buka <strong>Settings &rarr; Developer Options &rarr; Wireless Debugging</strong> lalu nyalakan.</p>
              <p>2. Pastikan HP dan laptop terhubung di Wi-Fi yang sama.</p>
              <p>3. Masukkan IP dan port yang tertera di layar HP ke input di atas, lalu klik Hubungkan Wi-Fi.</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Security & OS Sandbox Explanation */}
      {activeTab === 'info' && (
        <div className="bg-[#fef9e7] border-2 border-[#f39c12] p-3 text-xs text-[#7f8c8d] space-y-2">
          <div className="flex items-center gap-2 text-[#d35400] font-extrabold uppercase">
            <AlertTriangle className="w-4 h-4" />
            <span>Fakta Teknis: Batasan Keamanan Kernel OS Seluler</span>
          </div>
          <p className="font-medium text-[#2c3e50]">
            Mengapa sebuah website tidak bisa secara ajaib mengubah GPS tingkat sistem (OS-wide) di HP tanpa izin?
          </p>
          <p>
            Baik Apple (iOS WebKit sandbox) maupun Google (Android Linux UID sandbox) sengaja mengisolasi browser dari kernel driver GPS. Jika ada website di internet yang bisa mengubah lokasi GPS fisik HP Anda secara otomatis tanpa izin atau tanpa developer mode, itu adalah celah keamanan paling berbahaya (remote zero-day exploit) yang dapat membahayakan privasi dan perbankan seluruh dunia.
          </p>
          <p className="font-bold text-[#27ae60]">
            Solusi LocSpoof: Kami menyediakan 2 jalur legal dan aman:
            <br />
            1. <strong>Universal Browser Injection</strong>: Tanpa kabel & tanpa pengaturan, langsung manipulasi lokasi web di HP mana pun.
            <br />
            2. <strong>Wireless ADB</strong>: Tanpa kabel, tembus ke level sistem Android melalui Wi-Fi Debugging resmi.
          </p>
        </div>
      )}

    </div>
  );
}
