import React, { useState } from 'react';
import { 
  Download, 
  Smartphone, 
  Settings, 
  Key, 
  Rocket, 
  Check, 
  Copy, 
  ShieldCheck, 
  HelpCircle, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink,
  MapPin,
  Sparkles
} from 'lucide-react';
import { MASTER_OWNER_KEY } from '../services/cryptoKey';

export function ApkGuideView({ onSwitchToMap }) {
  const [copiedKey, setCopiedKey] = useState(false);
  const [activeFaq, setActiveFaq] = useState(null);

  const handleCopyKey = () => {
    navigator.clipboard.writeText(MASTER_OWNER_KEY);
    setCopiedKey(true);
    setTimeout(() => setCopiedKey(false), 2500);
  };

  const toggleFaq = (idx) => {
    setActiveFaq(activeFaq === idx ? null : idx);
  };

  // Direct download links
  const releaseDownloadUrl = "https://github.com/Sanggadiennata-me/LocSpoof/releases/latest/download/LocSpoof-v2.0.apk";
  const actionsUrl = "https://github.com/Sanggadiennata-me/LocSpoof/actions";

  const faqs = [
    {
      q: "Bagaimana cara menyalakan 'Developer Options' di HP saya?",
      a: "Buka Pengaturan HP (Settings) &rarr; Tentang Ponsel (About Phone) &rarr; cari 'Nomor Versi' atau 'Build Number' &rarr; ketuk (tap) 7 kali berturut-turut hingga muncul pesan 'Anda sekarang adalah seorang pengembang'. Setelah itu menu Developer Options akan muncul di Pengaturan Tambahan / Sistem."
    },
    {
      q: "Apakah HP saya harus di-root?",
      a: "SAMA SEKALI TIDAK! LocSpoof bekerja menggunakan jalur resmi AOSP Android Mock Location Provider. Tidak memerlukan root, tidak merusak garansi HP, dan sangat aman."
    },
    {
      q: "Apakah lokasi palsu ini tembus ke semua aplikasi di HP?",
      a: "YA! Begitu LocSpoof aktif sebagai Mock Location App di Developer Options, seluruh aplikasi di HP Anda (Google Maps, WhatsApp Live Location, Gojek, Grab, aplikasi absensi, dating apps) akan membaca koordinat dari LocSpoof."
    },
    {
      q: "Bagaimana cara mengembalikan GPS HP ke lokasi normal?",
      a: "Cukup buka aplikasi LocSpoof di HP Anda, lalu tap tombol 'RESET LOKASI NORMAL' berwarna merah. GPS HP Anda seketika kembali mendeteksi satelit asli."
    }
  ];

  return (
    <div className="max-w-4xl mx-auto space-y-6">

      {/* Top Banner Hero */}
      <div className="flat-card p-6 sm:p-8 bg-white border-2 border-[#2c3e50] shadow-flat relative overflow-hidden">
        <div className="relative z-10 space-y-4">
          <div className="flex flex-wrap items-center gap-2">
            <span className="flat-badge bg-[#1abc9c] text-white">
              <Smartphone className="w-3.5 h-3.5" />
              <span>Android Native APK</span>
            </span>
            <span className="flat-badge bg-[#f1c40f] text-[#2c3e50]">
              <Sparkles className="w-3.5 h-3.5" />
              <span>Murni di HP • Tanpa Laptop</span>
            </span>
            <span className="flat-badge bg-[#34495e] text-white">
              v2.0 Official
            </span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold text-[#2c3e50] tracking-tight uppercase leading-tight">
            LocSpoof Mobile APK
          </h1>

          <p className="text-sm sm:text-base text-[#7f8c8d] font-semibold max-w-2xl leading-relaxed">
            Aplikasi pengubah lokasi GPS mandiri untuk HP Android Anda. Mengubah GPS seluruh aplikasi di HP tanpa colok kabel ke laptop dan tanpa aplikasi pihak ketiga!
          </p>

          {/* Primary Download Button */}
          <div className="pt-2 flex flex-col sm:flex-row items-stretch sm:items-center gap-3">
            <a
              href={releaseDownloadUrl}
              target="_blank"
              rel="noreferrer"
              className="flat-btn-primary !py-3.5 !px-6 text-sm uppercase tracking-wider flex items-center justify-center gap-2.5 shadow-flat group"
            >
              <Download className="w-5 h-5 stroke-[2.5] group-hover:animate-bounce" />
              <span>DOWNLOAD LOCSPOOF.APK</span>
            </a>

            <a
              href={actionsUrl}
              target="_blank"
              rel="noreferrer"
              className="flat-btn-white !py-3.5 !px-4 text-xs uppercase font-extrabold flex items-center justify-center gap-1.5"
            >
              <ExternalLink className="w-4 h-4 text-[#3498db]" />
              <span>Mirror Download (GitHub Actions)</span>
            </a>

            <button
              onClick={onSwitchToMap}
              className="flat-btn-blue !py-3.5 !px-4 text-xs uppercase font-extrabold flex items-center justify-center gap-1.5"
            >
              <MapPin className="w-4 h-4 text-white" />
              <span>Buka Peta Web Simulator</span>
            </button>
          </div>
          
          <div className="text-[11px] font-bold text-[#7f8c8d] flex items-center gap-2">
            <span className="w-2 h-2 bg-[#2ecc71] inline-block"></span>
            <span>Kompatibel: Android 7.0 s/d Android 15 • Bebas Iklan • Serverless</span>
          </div>
        </div>
      </div>

      {/* Step by Step Visual Guide */}
      <div className="space-y-4">
        <div className="border-b-2 border-[#2c3e50] pb-2 flex items-center justify-between">
          <h2 className="text-lg font-extrabold uppercase text-[#2c3e50] tracking-wide flex items-center gap-2">
            <span>📋 Panduan Cara Memasang &amp; Menggunakan di HP</span>
          </h2>
          <span className="text-xs font-bold text-[#1abc9c] uppercase">4 Langkah Mudah</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">

          {/* Step 1 */}
          <div className="flat-card p-5 bg-white border-2 border-[#2c3e50] shadow-flat flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-[#1abc9c] text-white border-2 border-[#2c3e50] font-extrabold flex items-center justify-center text-sm shadow-flat-sm">
                  1
                </div>
                <h3 className="font-extrabold text-sm uppercase text-[#2c3e50]">
                  Download &amp; Pasang APK
                </h3>
              </div>
              <p className="text-xs text-[#7f8c8d] font-semibold leading-relaxed">
                Klik tombol <strong>Download LocSpoof.apk</strong> di atas. Setelah selesai di-download di HP Anda, buka file tersebut lalu pilih <strong>Install</strong>.
              </p>
            </div>
            <div className="mt-3 p-2 bg-[#ecf0f1] border border-[#2c3e50] text-[10px] font-bold text-[#2c3e50]">
              💡 <em>Jika HP memunculkan peringatan "Sumber tidak dikenal", pilih Izinkan / Tetap Install.</em>
            </div>
          </div>

          {/* Step 2 */}
          <div className="flat-card p-5 bg-white border-2 border-[#2c3e50] shadow-flat flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-[#f1c40f] text-[#2c3e50] border-2 border-[#2c3e50] font-extrabold flex items-center justify-center text-sm shadow-flat-sm">
                  2
                </div>
                <h3 className="font-extrabold text-sm uppercase text-[#2c3e50]">
                  Pilih Mock Location App
                </h3>
              </div>
              <p className="text-xs text-[#7f8c8d] font-semibold leading-relaxed">
                Buka <strong>Pengaturan HP &rarr; Opsi Pengembang (Developer Options)</strong> &rarr; cari menu <strong>"Pilih aplikasi lokasi palsu" (Select mock location app)</strong> &rarr; pilih <strong>LocSpoof</strong>.
              </p>
            </div>
            <div className="mt-3 p-2 bg-[#fef9e7] border border-[#f39c12] text-[10px] font-bold text-[#d35400]">
              ⚙️ <em>Langkah ini hanya perlu dilakukan 1 kali saja saat pertama kali install!</em>
            </div>
          </div>

          {/* Step 3 */}
          <div className="flat-card p-5 bg-white border-2 border-[#2c3e50] shadow-flat flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-[#3498db] text-white border-2 border-[#2c3e50] font-extrabold flex items-center justify-center text-sm shadow-flat-sm">
                  3
                </div>
                <h3 className="font-extrabold text-sm uppercase text-[#2c3e50]">
                  Buka App &amp; Masukkan Key
                </h3>
              </div>
              <p className="text-xs text-[#7f8c8d] font-semibold leading-relaxed">
                Buka aplikasi LocSpoof di HP Anda. Masukkan <strong>Master License Key</strong> pemilik Anda untuk membuka akses selamanya.
              </p>
            </div>
            <div className="mt-3">
              <button
                onClick={handleCopyKey}
                className="flat-btn-primary w-full !py-1.5 text-xs uppercase font-extrabold flex items-center justify-center gap-1.5"
              >
                {copiedKey ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedKey ? 'Key Tersalin ke Clipboard!' : 'Salin Master Key Pemilik'}</span>
              </button>
            </div>
          </div>

          {/* Step 4 */}
          <div className="flat-card p-5 bg-white border-2 border-[#2c3e50] shadow-flat flex flex-col justify-between">
            <div>
              <div className="flex items-center gap-3 mb-3">
                <div className="w-8 h-8 bg-[#2ecc71] text-white border-2 border-[#2c3e50] font-extrabold flex items-center justify-center text-sm shadow-flat-sm">
                  4
                </div>
                <h3 className="font-extrabold text-sm uppercase text-[#2c3e50]">
                  Pilih Lokasi &amp; Teleport!
                </h3>
              </div>
              <p className="text-xs text-[#7f8c8d] font-semibold leading-relaxed">
                Geser peta Google Maps bawaan di aplikasi LocSpoof atau cari nama tempat, lalu tap tombol <strong>"TELEPORT SEKARANG"</strong>.
              </p>
            </div>
            <div className="mt-3 p-2 bg-[#eafaf1] border border-[#27ae60] text-[10px] font-bold text-[#27ae60]">
              🚀 <em>Buka Google Maps, WhatsApp, atau Gojek di HP Anda, lokasi sudah berubah!</em>
            </div>
          </div>

        </div>
      </div>

      {/* Master Key Card */}
      <div className="flat-card p-5 bg-[#ffffff] border-2 border-[#2c3e50] shadow-flat">
        <div className="flex items-center justify-between border-b-2 border-[#2c3e50] pb-2 mb-3">
          <div className="flex items-center gap-2">
            <Key className="w-4 h-4 text-[#f1c40f]" />
            <span className="font-extrabold text-xs uppercase text-[#2c3e50] tracking-wider">
              Master License Key Anda (Salin Sekali Sentuh)
            </span>
          </div>
          <button
            onClick={handleCopyKey}
            className="text-xs font-bold text-[#3498db] hover:underline flex items-center gap-1"
          >
            {copiedKey ? <Check className="w-3.5 h-3.5 text-[#27ae60]" /> : <Copy className="w-3.5 h-3.5" />}
            <span>{copiedKey ? 'Tersalin' : 'Salin Key'}</span>
          </button>
        </div>

        <div className="bg-[#f8fafc] border-2 border-[#2c3e50] p-3 font-mono text-xs break-all text-[#2c3e50] select-all">
          {MASTER_OWNER_KEY}
        </div>
        <p className="text-[10px] font-semibold text-[#7f8c8d] mt-2">
          Key ini berstatus <strong>LIFETIME OWNER</strong> tanpa batas waktu. Berlaku di web maupun aplikasi APK.
        </p>
      </div>

      {/* FAQ & Troubleshooting Accordion */}
      <div className="flat-card p-5 bg-white border-2 border-[#2c3e50] shadow-flat space-y-3">
        <div className="flex items-center gap-2 border-b-2 border-[#2c3e50] pb-2">
          <HelpCircle className="w-4 h-4 text-[#e67e22]" />
          <h3 className="font-extrabold text-xs uppercase text-[#2c3e50] tracking-wider">
            Pertanyaan yang Sering Diajukan (FAQ)
          </h3>
        </div>

        <div className="space-y-2">
          {faqs.map((faq, idx) => (
            <div key={idx} className="border border-[#2c3e50] bg-[#f8fafc]">
              <button
                type="button"
                onClick={() => toggleFaq(idx)}
                className="w-full text-left px-3 py-2.5 text-xs font-bold text-[#2c3e50] flex items-center justify-between hover:bg-[#ecf0f1] transition-colors"
              >
                <span>{faq.q}</span>
                {activeFaq === idx ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
              {activeFaq === idx && (
                <div 
                  className="px-3 pb-3 text-xs text-[#7f8c8d] font-semibold border-t border-[#ecf0f1] pt-2 leading-relaxed"
                  dangerouslySetInnerHTML={{ __html: faq.a }}
                />
              )}
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
