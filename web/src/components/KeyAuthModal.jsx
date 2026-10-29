import React, { useState } from 'react';
import { Key, ShieldCheck, AlertCircle, ArrowRight, Lock, CheckCircle2 } from 'lucide-react';
import { verifyLicenseKey, MASTER_OWNER_KEY } from '../services/cryptoKey';

export function KeyAuthModal({ isOpen, onAuthenticated }) {
  const [inputKey, setInputKey] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [isValidating, setIsValidating] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    setErrorMsg('');
    setIsValidating(true);

    setTimeout(() => {
      const result = verifyLicenseKey(inputKey);
      setIsValidating(false);

      if (result.valid) {
        // Save to localStorage
        localStorage.setItem('locspoof_license_key', inputKey.trim());
        onAuthenticated(result.payload, inputKey.trim());
      } else {
        setErrorMsg(result.error || "Lisensi tidak valid.");
      }
    }, 200);
  };

  const handleUseMasterKey = () => {
    setInputKey(MASTER_OWNER_KEY);
    setErrorMsg('');
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#2c3e50]/80 backdrop-blur-sm animate-fade-in">
      <div className="flat-card w-full max-w-md p-6 bg-white border-2 border-[#2c3e50] shadow-flat-lg relative">
        
        {/* Header */}
        <div className="text-center mb-6">
          <div className="w-14 h-14 bg-[#1abc9c] border-2 border-[#2c3e50] shadow-flat-sm mx-auto flex items-center justify-center mb-3">
            <Lock className="w-7 h-7 text-white stroke-[2.5]" />
          </div>
          <h2 className="text-xl sm:text-2xl font-extrabold text-[#2c3e50] uppercase tracking-tight">
            Aktivasi Lisensi
          </h2>
          <p className="text-xs font-semibold text-[#7f8c8d] mt-1">
            Aplikasi ini terproteksi. Masukkan License Key resmi Anda untuk mengakses GUI LocSpoof.
          </p>
        </div>

        {/* Error Alert */}
        {errorMsg && (
          <div className="mb-4 p-3 bg-[#fdf2e9] border-2 border-[#e74c3c] text-xs font-bold text-[#c0392b] flex items-start gap-2 shadow-flat-sm">
            <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0 text-[#e74c3c]" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-[11px] font-extrabold uppercase text-[#2c3e50] mb-1.5 tracking-wider">
              Masukkan License Key
            </label>
            <div className="relative">
              <input
                type="text"
                value={inputKey}
                onChange={(e) => {
                  setInputKey(e.target.value);
                  setErrorMsg('');
                }}
                placeholder="LOCSPOOF-USER-..."
                className="flat-input w-full text-xs font-mono py-2.5 pl-3 pr-9 shadow-flat-sm"
                required
                autoFocus
              />
              <Key className="w-4 h-4 text-[#95a5a6] absolute right-3 top-3 pointer-events-none" />
            </div>
            <p className="text-[10px] text-[#7f8c8d] mt-1">
              Sistem verifikasi serverless kriptografis matematis tanpa database.
            </p>
          </div>

          <button
            type="submit"
            disabled={isValidating || !inputKey.trim()}
            className="flat-btn-primary w-full !py-3 text-sm uppercase tracking-wider flex items-center justify-center gap-2"
          >
            <ShieldCheck className="w-4 h-4" />
            <span>{isValidating ? 'Memvalidasi...' : 'Verifikasi & Buka Akses'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        {/* Owner Quick Test Shortcut */}
        <div className="mt-5 pt-4 border-t-2 border-[#ecf0f1] text-center">
          <button
            type="button"
            onClick={handleUseMasterKey}
            className="text-[11px] font-bold text-[#3498db] hover:text-[#2980b9] hover:underline"
          >
            👑 Masuk dengan Master Key Pemilik (r3x)
          </button>
        </div>

      </div>
    </div>
  );
}
