package com.locspoof.app;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationManager;
import android.location.LocationProvider;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.os.SystemClock;
import android.webkit.GeolocationPermissions;
import android.webkit.JavascriptInterface;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

public class MainActivity extends AppCompatActivity {

    private WebView webView;
    private LocationManager locationManager;
    private Handler mockHandler;
    private Runnable mockRunnable;
    private boolean isMocking = false;

    private double currentLat = 0.0;
    private double currentLon = 0.0;
    private double currentAlt = 15.0;
    private float currentAcc = 3.0f;

    private static final int PERMISSION_REQ_CODE = 1001;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        mockHandler = new Handler(Looper.getMainLooper());

        webView = new WebView(this);
        setContentView(webView);

        configureWebView();
        checkAndRequestPermissions();

        // Load local React Flat Design Web App
        webView.loadUrl("file:///android_asset/www/index.html");
    }

    private void configureWebView() {
        WebSettings settings = webView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setGeolocationEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setAllowFileAccessFromFileURLs(true);
        settings.setAllowUniversalAccessFromFileURLs(true);
        settings.setCacheMode(WebSettings.LOAD_DEFAULT);

        webView.setWebViewClient(new WebViewClient());
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onGeolocationPermissionsShowPrompt(String origin, GeolocationPermissions.Callback callback) {
                callback.invoke(origin, true, false);
            }
        });

        // Register Javascript Bridge for React to call Android LocationManager
        webView.addJavascriptInterface(new WebAppInterface(), "LocSpoofAndroid");
    }

    private void checkAndRequestPermissions() {
        String[] permissions = {
                Manifest.permission.ACCESS_FINE_LOCATION,
                Manifest.permission.ACCESS_COARSE_LOCATION
        };
        boolean allGranted = true;
        for (String perm : permissions) {
            if (ContextCompat.checkSelfPermission(this, perm) != PackageManager.PERMISSION_GRANTED) {
                allGranted = false;
                break;
            }
        }
        if (!allGranted) {
            ActivityCompat.requestPermissions(this, permissions, PERMISSION_REQ_CODE);
        }
    }

    /**
     * JavaScript Bridge Interface exposed to React Web GUI
     */
    public class WebAppInterface {

        @JavascriptInterface
        public void setMockLocation(double lat, double lon, double alt, float acc) {
            currentLat = lat;
            currentLon = lon;
            currentAlt = alt;
            currentAcc = acc;
            isMocking = true;

            runOnUiThread(() -> {
                try {
                    initMockProvider();
                    pushMockFix();
                    startContinuousMocking();
                    Toast.makeText(MainActivity.this, 
                        "🎯 Mock GPS Aktif: " + String.format("%.5f, %.5f", lat, lon), 
                        Toast.LENGTH_SHORT).show();
                } catch (SecurityException se) {
                    Toast.makeText(MainActivity.this, 
                        "⚠️ Aktifkan LocSpoof di 'Select mock location app' di Developer Options!", 
                        Toast.LENGTH_LONG).show();
                } catch (Exception e) {
                    Toast.makeText(MainActivity.this, "Error mock location: " + e.getMessage(), Toast.LENGTH_SHORT).show();
                }
            });
        }

        @JavascriptInterface
        public void stopMockLocation() {
            isMocking = false;
            runOnUiThread(() -> {
                if (mockRunnable != null) {
                    mockHandler.removeCallbacks(mockRunnable);
                }
                try {
                    locationManager.removeTestProvider(LocationManager.GPS_PROVIDER);
                    locationManager.removeTestProvider(LocationManager.NETWORK_PROVIDER);
                } catch (Exception ignored) {}
                Toast.makeText(MainActivity.this, "⏹️ Mock GPS Dinonaktifkan.", Toast.LENGTH_SHORT).show();
            });
        }
    }

    private void initMockProvider() {
        try {
            locationManager.addTestProvider(
                    LocationManager.GPS_PROVIDER,
                    "requiresNetwork" == "",
                    "requiresSatellite" == "",
                    "requiresCell" == "",
                    "hasMonetaryCost" == "",
                    "supportsAltitude" == "",
                    "supportsSpeed" == "",
                    "supportsBearing" == "",
                    Criteria.POWER_LOW,
                    Criteria.ACCURACY_FINE
            );
            locationManager.setTestProviderEnabled(LocationManager.GPS_PROVIDER, true);
        } catch (Exception ignored) {
            // Provider may already exist
        }

        try {
            locationManager.addTestProvider(
                    LocationManager.NETWORK_PROVIDER,
                    false, false, false, false, true, true, true,
                    Criteria.POWER_LOW, Criteria.ACCURACY_COARSE
            );
            locationManager.setTestProviderEnabled(LocationManager.NETWORK_PROVIDER, true);
        } catch (Exception ignored) {}
    }

    private void pushMockFix() {
        if (!isMocking) return;

        Location mockLoc = new Location(LocationManager.GPS_PROVIDER);
        mockLoc.setLatitude(currentLat);
        mockLoc.setLongitude(currentLon);
        mockLoc.setAltitude(currentAlt);
        mockLoc.setTime(System.currentTimeMillis());
        mockLoc.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
        mockLoc.setAccuracy(currentAcc);

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            mockLoc.setBearingAccuracyDegrees(0.1f);
            mockLoc.setVerticalAccuracyMeters(0.1f);
            mockLoc.setSpeedAccuracyMetersPerSecond(0.1f);
        }

        try {
            locationManager.setTestProviderLocation(LocationManager.GPS_PROVIDER, mockLoc);
        } catch (Exception ignored) {}

        Location netLoc = new Location(LocationManager.NETWORK_PROVIDER);
        netLoc.setLatitude(currentLat);
        netLoc.setLongitude(currentLon);
        netLoc.setTime(System.currentTimeMillis());
        netLoc.setElapsedRealtimeNanos(SystemClock.elapsedRealtimeNanos());
        netLoc.setAccuracy(currentAcc);

        try {
            locationManager.setTestProviderLocation(LocationManager.NETWORK_PROVIDER, netLoc);
        } catch (Exception ignored) {}
    }

    private void startContinuousMocking() {
        if (mockRunnable != null) {
            mockHandler.removeCallbacks(mockRunnable);
        }
        mockRunnable = new Runnable() {
            @Override
            public void run() {
                if (isMocking) {
                    pushMockFix();
                    mockHandler.postDelayed(this, 1000); // 1-second pulse
                }
            }
        };
        mockHandler.post(mockRunnable);
    }

    @Override
    public void onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (mockRunnable != null) {
            mockHandler.removeCallbacks(mockRunnable);
        }
        super.onDestroy();
    }
}
