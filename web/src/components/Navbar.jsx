import React from 'react';
import { MapPin, Shield, Key, LogOut, CheckCircle2, AlertCircle } from 'lucide-react';

export function Navbar({ session, isSpoofing, spoofedCoords, onOpenKeyGen, onLogout }) {
  const isOwner = session?.role === 'OWNER';

  return (
    <header className="bg-white border-b-2 border-[#2c3e50] shadow-sm sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        
        {/* Brand */}
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#1abc9c] border-2 border-[#2c3e50] shadow-flat-sm flex items-center justify-center text-white font-extrabold text-xl">
            <MapPin className="w-6 h-6 text-white stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="font-extrabold text-xl tracking-tight text-[#2c3e50]">
                LOC<span className="text-[#1abc9c]">SPOOF</span>
              </span>
              <span className="bg-[#2c3e50] text-white text-[10px] font-bold px-1.5 py-0.5 uppercase tracking-widest">
                GUI v2.0
              </span>
            </div>
            <p className="text-[11px] font-semibold text-[#7f8c8d] uppercase tracking-wider hidden sm:block">
              Universal Location Spoofer • Flat Design
            </p>
          </div>
        </div>

        {/* Live Status Indicators */}
        <div className="hidden md:flex items-center gap-3">
          <div className={`flex items-center gap-2 px-3 py-1.5 border-2 border-[#2c3e50] font-bold text-xs uppercase ${
            isSpoofing ? 'bg-[#2ecc71] text-white shadow-flat-sm' : 'bg-[#ecf0f1] text-[#7f8c8d]'
          }`}>
            <span className={`w-2.5 h-2.5 rounded-full ${isSpoofing ? 'bg-white animate-pulse' : 'bg-[#95a5a6]'}`}></span>
            {isSpoofing ? 'SPOOF ACTIVE' : 'STANDBY'}
          </div>

          {isSpoofing && spoofedCoords && (
            <div className="bg-[#34495e] text-white text-xs font-mono px-3 py-1.5 border-2 border-[#2c3e50] flex items-center gap-2">
              <span className="text-[#1abc9c]">LAT:</span> {spoofedCoords.lat.toFixed(5)}
              <span className="text-[#3498db] ml-1">LON:</span> {spoofedCoords.lon.toFixed(5)}
            </div>
          )}
        </div>

        {/* User Badge & Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Key Role Badge */}
          <div className={`flex items-center gap-1.5 px-2.5 py-1 border-2 border-[#2c3e50] text-xs font-extrabold uppercase ${
            isOwner 
              ? 'bg-[#f1c40f] text-[#2c3e50] shadow-flat-sm' 
              : 'bg-[#3498db] text-white shadow-flat-sm'
          }`}>
            <Shield className="w-3.5 h-3.5" />
            <span>{session?.sub || 'Authorized'}</span>
            <span className="text-[10px] opacity-75">({session?.role})</span>
          </div>

          {/* Owner-only Key Generator */}
          {isOwner && (
            <button
              onClick={onOpenKeyGen}
              className="flat-btn-primary !py-1 !px-2.5 text-xs flex items-center gap-1.5"
              title="Serverless Key Generator (Owner Exclusive)"
            >
              <Key className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">Key Gen</span>
            </button>
          )}

          {/* Logout / Switch Key */}
          <button
            onClick={onLogout}
            className="flat-btn-danger !py-1 !px-2 text-xs"
            title="Ganti Lisensi / Logout"
          >
            <LogOut className="w-3.5 h-3.5" />
          </button>
        </div>

      </div>
    </header>
  );
}
