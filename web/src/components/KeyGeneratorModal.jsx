import React, { useState } from 'react';
import { Key, Copy, Check, X, Shield, Calendar, User, Sparkles } from 'lucide-react';
import { generateLicenseKey } from '../services/cryptoKey';

export function KeyGeneratorModal({ isOpen, onClose }) {
  const [username, setUsername] = useState('');
  const [role, setRole] = useState('USER');
  const [duration, setDuration] = useState('30'); // '7', '30', '90', '365', '0' (lifetime)
  const [generatedKey, setGeneratedKey] = useState('');
  const [copied, setCopied] = useState(false);

  if (!isOpen) return null;

  const handleGenerate = (e) => {
    e.preventDefault();
    if (!username.trim()) return;

    const days = duration === '0' ? null : parseInt(duration, 10);
    const key = generateLicenseKey({
      username: username.trim(),
      role: role,
      durationDays: days,
      features: role === 'VIP' ? ['*'] : ['map', 'spoof', 'browser', 'wireless']
    });

    setGeneratedKey(key);
    setCopied(false);
  };

  const handleCopyKey = () => {
    navigator.clipboard.writeText(generatedKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2c3e50]/80 backdrop-blur-sm animate-fade-in">
      <div className="flat-card w-full max-w-lg p-6 bg-white border-2 border-[#2c3e50] shadow-flat-lg relative">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 text-[#7f8c8d] hover:text-[#2c3e50] p-1"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <div className="flex items-center gap-3 border-b-2 border-[#2c3e50] pb-3 mb-5">
          <div className="w-10 h-10 bg-[#f1c40f] border-2 border-[#2c3e50] shadow-flat-sm flex items-center justify-center text-[#2c3e50]">
            <Key className="w-6 h-6 stroke-[2.5]" />
          </div>
          <div>
            <h3 className="font-extrabold text-lg text-[#2c3e50] uppercase tracking-tight">
              Serverless Key Generator
            </h3>
            <span className="text-xs font-bold text-[#e67e22] uppercase tracking-wider">
              Khusus Akun Owner (Zero Database)
            </span>
          </div>
        </div>

        {/* Generator Form */}
        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-[11px] font-extrabold uppercase text-[#2c3e50] mb-1">
              Nama Pengguna / Klien
            </label>
            <div className="relative">
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="cth: budi_santoso atau client_vip"
                className="flat-input w-full text-xs py-2 pl-3"
                required
              />
              <User className="w-4 h-4 text-[#95a5a6] absolute right-3 top-2.5 pointer-events-none" />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-[11px] font-extrabold uppercase text-[#2c3e50] mb-1">
                Role Akses
              </label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="flat-input w-full text-xs py-2"
              >
                <option value="USER">Standard User</option>
                <option value="VIP">VIP Access (Full)</option>
              </select>
            </div>

            <div>
              <label className="block text-[11px] font-extrabold uppercase text-[#2c3e50] mb-1">
                Masa Berlaku
              </label>
              <select
                value={duration}
                onChange={(e) => setDuration(e.target.value)}
                className="flat-input w-full text-xs py-2"
              >
                <option value="7">7 Hari (Trial)</option>
                <option value="30">30 Hari (1 Bulan)</option>
                <option value="90">90 Hari (3 Bulan)</option>
                <option value="365">1 Tahun</option>
                <option value="0">Lifetime (Selamanya)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            className="flat-btn-primary w-full !py-2.5 text-xs uppercase tracking-wider flex items-center justify-center gap-2"
          >
            <Sparkles className="w-4 h-4" />
            <span>Generate License Key Baru</span>
          </button>
        </form>

        {/* Generated Key Result */}
        {generatedKey && (
          <div className="mt-5 pt-4 border-t-2 border-[#2c3e50] space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-extrabold uppercase text-[#27ae60] flex items-center gap-1">
                ✓ License Key Berhasil Digenerate
              </span>
              <button
                type="button"
                onClick={handleCopyKey}
                className="flat-btn-blue !py-1 !px-2.5 text-xs flex items-center gap-1.5"
              >
                {copied ? <Check className="w-3.5 h-3.5" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Tersalin!' : 'Salin Key'}</span>
              </button>
            </div>

            <div className="bg-[#f8fafc] border-2 border-[#2c3e50] p-2.5 font-mono text-[11px] break-all text-[#2c3e50] select-all shadow-flat-sm">
              {generatedKey}
            </div>

            <div className="text-[10px] text-[#7f8c8d]">
              Kirimkan string key di atas kepada klien Anda. User cukup memasukkan key tersebut di halaman awal website.
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
