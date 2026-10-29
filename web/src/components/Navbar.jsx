import React from 'react';
import { MapPin, Shield, Key, LogOut, Smartphone, Navigation } from 'lucide-react';

export function Navbar({ 
  session, 
  currentTab, 
  onSelectTab, 
  isSpoofing, 
  spoofedCoords, 
  onOpenKeyGen, 
  onLogout 
}) {
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
                v2.0
              </span>
            </div>
            <p className="text-[11px] font-semibold text-[#7f8c8d] uppercase tracking-wider hidden sm:block">
              Universal Location Spoofer • Flat Design
            </p>
          </div>
        </div>

        {/* Center Nav: Tab Switcher (APK Guide vs Map Controller) */}
        <div className="flex items-center border-2 border-[#2c3e50] bg-[#ecf0f1] p-0.5">
          <button
            onClick={() => onSelectTab('guide')}
            className={`px-3 py-1.5 text-xs font-extrabold uppercase flex items-center gap-1.5 transition-colors ${
              currentTab === 'guide' 
                ? 'bg-[#1abc9c] text-white shadow-flat-sm' 
                : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            <Smartphone className="w-3.5 h-3.5" />
            <span>Download APK &amp; Panduan</span>
          </button>
          
          <button
            onClick={() => onSelectTab('map')}
            className={`px-3 py-1.5 text-xs font-extrabold uppercase flex items-center gap-1.5 transition-colors ${
              currentTab === 'map' 
                ? 'bg-[#3498db] text-white shadow-flat-sm' 
                : 'text-[#2c3e50] hover:bg-white'
            }`}
          >
            <Navigation className="w-3.5 h-3.5" />
            <span>Peta Interaktif</span>
          </button>
        </div>

        {/* User Badge & Actions */}
        <div className="flex items-center gap-2 sm:gap-3">
          {/* Key Role Badge */}
          <div className={`hidden sm:flex items-center gap-1.5 px-2.5 py-1 border-2 border-[#2c3e50] text-xs font-extrabold uppercase ${
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
