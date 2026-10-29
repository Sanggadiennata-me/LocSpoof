/**
 * Android Native Mock Location Bridge
 * Communicates with native Android Java layer when running inside LocSpoof APK.
 */

export const isNativeAndroidApp = () => {
  return typeof window !== 'undefined' && Boolean(window.LocSpoofAndroid);
};

export const applyNativeMockLocation = (lat, lon, altitude = 15.0, accuracy = 3.0) => {
  if (isNativeAndroidApp()) {
    try {
      window.LocSpoofAndroid.setMockLocation(lat, lon, altitude, accuracy);
      return { success: true, message: "Lokasi berhasil diinjeksi via Android Mock Provider." };
    } catch (err) {
      return { success: false, message: "Gagal memanggil native Android bridge: " + err.message };
    }
  }
  return { success: false, message: "Bukan aplikasi native APK." };
};

export const stopNativeMockLocation = () => {
  if (isNativeAndroidApp()) {
    try {
      window.LocSpoofAndroid.stopMockLocation();
      return { success: true, message: "Mock location dihentikan." };
    } catch (err) {
      return { success: false, message: "Gagal menghentikan mock: " + err.message };
    }
  }
  return { success: false, message: "Bukan aplikasi native APK." };
};
