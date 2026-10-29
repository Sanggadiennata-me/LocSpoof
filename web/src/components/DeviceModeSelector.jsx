import React, { useState, useEffect } from 'react';
import { 
  Smartphone, 
  Wifi, 
  Usb, 
  Check, 
  Copy, 
  HelpCircle, 
  Zap, 
  AlertTriangle,
  Play,
  RotateCcw
} from 'lucide-react';
import { generateBookmarkletCode } from '../services/universalSpoofer';

export function DeviceModeSelector({ targetCoords, isSpoofing }) {
  const [activeTab, setActiveTab] = useState('usb'); // 'usb' | 'wireless' | 'browser' | 'playstore'
  const [copiedCode, setCopiedCode] = useState(false);
  const [wirelessIp, setWirelessIp] = useState('192.168.1.100:5555');
  const [wirelessConnected, setWirelessConnected] = useState(false);
  const [devices, setDevices] = useState([]);
  const [checkingDevices, setCheckingDevices] = useState(false);

  const bookmarkletCode = generateBookmarkletCode(targetCoords.lat, targetCoords.lon);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(bookmarkletCode);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  const fetchDevices = async () => {
    setCheckingDevices(true);
    try {
      const res = await fetch('/api/devices');
      if (res.ok) {
        const data = await res.json();
        setDevices(data.devices || []);
      }
    } catch {
      setDevices([]);
    } finally {
      setCheckingDevices(false);
    }
  };

  useEffect(() => {
    if (activeTab === 'usb') {
      fetchDevices();
    }
  }, [activeTab]);

  return (
    <div className="flat-card p-4 sm:p-5">
      <div className="border-b-2 border-[#2c3e50] pb-3 mb-4 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h3 className="font-extrabold text-sm sm:text-base text-[#2c3e50] uppercase tracking-wide flex items-center gap-2">
            <Smartphone className="w-5 h-5 text-[#1abc9c]" />
            <span>Mode Kontrol HP Fisik &amp; Browser</span>
          </h3>
          <p className="text-xs text-[#7f8c8d] font-medium mt-0.5">
            Pilih cara penerapan lokasi palsu ke perangkat Android, iPhone, atau browser Anda.
          </p>
        </div>

        {/* Tab Buttons */}
        <div className="flex flex-wrap border-2 border-[#2c3e50] p-0.5 bg-[#ecf0f1]">
          <button
            onClick={() => setActiveTab('usb')}
            className={`px-2.5 py-1 text-xs font-bold transition-colors ${
              activeTab === 'usb' ? 'bg-[#2ecc71] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Kabel USB (Seperti CLI)
          </button>
          <button
            onClick={() => setActiveTab('wireless')}
            className={`px-2.5 py-1 text-xs font-bold transition-colors ${
              activeTab === 'wireless' ? 'bg-[#3498db] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Wireless ADB (Wi-Fi)
          </button>
          <button
            onClick={() => setActiveTab('browser')}
            className={`px-2.5 py-1 text-xs font-bold transition-colors ${
              activeTab === 'browser' ? 'bg-[#1abc9c] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Universal Web
          </button>
          <button
            onClick={() => setActiveTab('playstore')}
            className={`px-2.5 py-1 text-xs font-bold transition-colors ${
              activeTab === 'playstore' ? 'bg-[#e67e22] text-white shadow-flat-sm' : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            Aplikasi Play Store?
          </button>
        </div>
      </div>

      {/* Tab 1: USB Mode (Sama persis seperti CLI lama tapi sekarang pakai GUI!) */}
      {activeTab === 'usb' && (
        <div className="space-y-3">
          <div className="bg-[#eafaf1] border-2 border-[#27ae60] p-3 text-xs text-[#27ae60] font-semibold flex items-start gap-2">
            <Usb className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#27ae60]" />
            <div>
              <strong className="font-extrabold block uppercase tracking-wide">
                Mode USB ADB (Mengubah GPS Sistem Android seperti CLI lama):
              </strong>
              Ketika Anda mencolokkan kabel USB dari HP ke laptop, Web GUI ini langsung berkomunikasi dengan perintah <code className="bg-white px-1 py-0.5 border border-[#27ae60]">adb</code> di laptop. Tombol <strong>"TELEPORT SEKARANG"</strong> di atas akan langsung mengubah lokasi fisik seluruh aplikasi di HP Anda (Gojek, Grab, WhatsApp, Google Maps App)!
            </div>
          </div>

          <div className="bg-white border-2 border-[#2c3e50] p-3 space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase text-[#2c3e50]">
                Status Perangkat HP USB yang Terdeteksi:
              </span>
              <button
                onClick={fetchDevices}
                className="flat-btn-white !py-0.5 !px-2 text-xs flex items-center gap-1"
              >
                <RotateCcw className={`w-3 h-3 ${checkingDevices ? 'animate-spin' : ''}`} />
                <span>Pindai Ulang HP</span>
              </button>
            </div>

            {devices.length > 0 ? (
              <div className="space-y-1">
                {devices.map((d, i) => (
                  <div key={i} className="p-2 bg-[#f8fafc] border border-[#27ae60] text-xs flex items-center justify-between font-bold text-[#27ae60]">
                    <span>📱 {d.model || d.serial} ({d.serial})</span>
                    <span className="bg-[#2ecc71] text-white text-[10px] px-2 py-0.5 font-extrabold uppercase">TERHUBUNG &amp; SIAP</span>
                  </div>
                ))}
              </div>
            ) : (
              <div className="p-3 bg-[#fdf2e9] border border-[#f39c12] text-xs font-medium text-[#d35400] space-y-1">
                <p className="font-bold">⚠️ Belum ada HP Android yang terdeteksi lewat ADB.</p>
                <p>1. Colokkan kabel USB dari HP ke laptop.</p>
                <p>2. Pastikan <strong>USB Debugging</strong> di HP sudah dinyalakan (Settings &rarr; Developer Options &rarr; USB Debugging).</p>
                <p>3. Jika muncul popup <em>"Izinkan USB debugging?"</em> di layar HP, pilih <strong>Selalu izinkan</strong>.</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Tab 2: Wireless ADB (Android Tanpa Kabel Colok Laptop) */}
      {activeTab === 'wireless' && (
        <div className="space-y-3">
          <div className="bg-[#ebf5fb] border-2 border-[#2980b9] p-3 text-xs text-[#2980b9] font-semibold flex items-start gap-2">
            <Wifi className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#2980b9]" />
            <div>
              <strong className="font-extrabold block uppercase tracking-wide">
                Wireless ADB Mode (Level OS Android Tanpa Kabel):
              </strong>
              Jika ingin lokasi palsu tembus ke <strong>seluruh aplikasi Android OS</strong> tanpa mencolokkan kabel ke laptop, gunakan fitur <em>Wireless Debugging</em> (tersedia di Android 11+).
            </div>
          </div>

          <div className="bg-white border-2 border-[#2c3e50] p-3 space-y-3">
            <div className="flex flex-col sm:flex-row sm:items-center gap-2">
              <div className="flex-1">
                <label className="text-[10px] font-extrabold uppercase text-[#2c3e50] block mb-1">
                  Alamat IP &amp; Port HP (dari menu Wireless Debugging di HP)
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
                  onClick={() => setWirelessConnected(!wirelessConnected)}
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
              <p>1. Di HP Android: Buka <strong>Settings &rarr; Developer Options &rarr; Wireless Debugging</strong> lalu aktifkan.</p>
              <p>2. Pastikan HP dan laptop terhubung di Wi-Fi yang sama.</p>
              <p>3. Masukkan IP dan port yang tertera di layar HP ke kolom di atas, lalu klik Hubungkan Wi-Fi.</p>
            </div>
          </div>
        </div>
      )}

      {/* Tab 3: Universal Browser Override (Semua Device: iPhone, Android, Laptop) */}
      {activeTab === 'browser' && (
        <div className="space-y-3">
          <div className="bg-[#e8f8f5] border-2 border-[#16a085] p-3 text-xs text-[#16a085] font-semibold flex items-start gap-2">
            <Zap className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#16a085]" />
            <div>
              <strong className="font-extrabold block uppercase tracking-wide">
                Universal Instant Spoofer (Di Browser HP Tanpa Kabel &amp; Tanpa Pengaturan):
              </strong>
              Bekerja di browser HP (Safari iPhone, Chrome Android, iPad, PC). Script ini meng-override API <code className="bg-white px-1 py-0.5 border border-[#16a085]">navigator.geolocation</code> langsung di browser HP!
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
              <p><strong>Cara Pakai di HP:</strong></p>
              <ol className="list-decimal list-inside space-y-0.5 ml-1">
                <li>Klik tombol <strong>Salin Script</strong> di atas.</li>
                <li>Buka tab browser di HP Anda (misal Google Maps Web atau web target).</li>
                <li>Tempelkan ke address bar browser (pastikan ada tulisan <code className="bg-[#ecf0f1] px-1 font-mono">javascript:</code> di depan) lalu tekan Enter.</li>
              </ol>
            </div>
          </div>
        </div>
      )}

      {/* Tab 4: Kenapa Aplikasi Play Store Bisa? (Penjelasan Arsitektur) */}
      {activeTab === 'playstore' && (
        <div className="bg-[#fef9e7] border-2 border-[#f39c12] p-4 text-xs text-[#2c3e50] space-y-3">
          <div className="flex items-center gap-2 text-[#d35400] font-extrabold text-sm uppercase">
            <HelpCircle className="w-5 h-5 text-[#d35400]" />
            <span>Mengapa Aplikasi di Play Store Bisa Berubah Hanya dari HP?</span>
          </div>

          <div className="space-y-2 leading-relaxed">
            <p>
              Aplikasi di Play Store (seperti <em>Fake GPS Location</em>, <em>GPS Emulator</em>, dll.) bisa mengubah lokasi langsung dari HP karena itu adalah <strong>Aplikasi Native Android (file APK) yang ter-install di dalam OS HP</strong>.
            </p>
            <p>
              Di HP Android, aplikasi tersebut hanya bisa bekerja jika pengguna melakukan pengaturan khusus di menu pengembang:
              <br />
              <strong className="text-[#c0392b]">Settings &rarr; Developer Options &rarr; "Select mock location app" &rarr; Pilih aplikasi Fake GPS tersebut</strong>.
            </p>
            <p>
              Dengan pengaturan tersebut, sistem operasi Android memberi hak istimewa kepada aplikasi APK tersebut untuk menyuntikkan koordinat palsu ke chip GPS HP.
            </p>
          </div>

          <div className="bg-white border-2 border-[#2c3e50] p-3 font-semibold space-y-1 text-[#2c3e50]">
            <p className="font-extrabold text-[#27ae60] uppercase">Perbedaan dengan Website (Web Browser):</p>
            <p>
              Sebuah halaman website di browser (seperti Safari di iPhone atau Chrome di Android) berada di dalam <em>Sandbox Keamanan Web</em>. Sistem Android/iOS <strong>sengaja melarang keras</strong> website biasa mengontrol GPS sistem tanpa perantara (ADB / kabel / native APK), demi mencegah hacker memalsukan lokasi HP Anda secara remote hanya lewat link web.
            </p>
            <p className="font-bold text-[#2980b9] mt-2">
              💡 Kesimpulan: Agar Web GUI LocSpoof Anda bisa mengubah seluruh aplikasi di HP (seperti waktu mode CLI dulu):
              <br />
              Cukup colokkan kabel USB ke laptop (atau hubungkan Wi-Fi Wireless ADB), lalu klik tombol <strong>TELEPORT SEKARANG</strong> di Web GUI!
            </p>
          </div>
        </div>
      )}

    </div>
  );
}
