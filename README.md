# LocSpoof

> **Android Device-Level Location Spoofer via CLI (Fake GPS Framework).**  
> Control Android mock locations, emulate hardware GNSS fixes, and verify device-reported coordinates from the command line.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://python.org)
[![Platform](https://img.shields.io/badge/Target-Android%20(Emulator%20%26%20Device)-brightgreen.svg)]()
[![Security](https://img.shields.io/badge/Security-Hardened%20Subprocess-brightgreen.svg)]()
[![Tests](https://img.shields.io/badge/Tests-29%20Passed%20(100%25)-success.svg)]()
[![License](https://img.shields.io/badge/License-MIT-green.svg)]()

---

## 1. Overview & Core Mission

`locspoof` is a **command-line Fake GPS / Location Spoofer** for Android devices and emulators.

Instead of navigating graphical fake GPS interfaces, `locspoof` allows security researchers, penetration testers, and mobile QA engineers to inject mock coordinates directly into the Android OS location layer via terminal commands.

### The Desired Workflow
```
User runs:
locspoof 55°33'15.3"N 55°45'56.2"E

        ↓ (Coordinate Parser converts DMS / Decimal)

Latitude:  55.554250
Longitude: 55.765611

        ↓ (Android Provider interacts with ADB / LocationManager)

Target Device reports spoofed location to Android OS

        ↓ (Google Maps or Target App requests device location)

Google Maps receives 55.554250, 55.765611 as current GPS position!
```

---

## 2. Core Behavior & Android Mechanisms

### Android Location Layer Integration
`locspoof` does not merely save coordinates to a local config file. It directly manipulates the Android device's reported location through official AOSP interfaces:

1. **Android Emulator (QEMU / AVD)**:
   * Communicates via ADB to the emulator's virtual GNSS console: `adb emu geo fix <longitude> <latitude> [altitude]`.
   * The emulator's hardware abstraction layer (`gps.goldfish.so`) feeds these coordinates into Android's `LocationManagerService` as authentic satellite fixes (`LocationProvider.GPS_PROVIDER`).
   * When Google Maps or any application calls `FusedLocationProviderClient` or `LocationListener`, Android returns the target coordinates.
2. **Physical Android Devices**:
   * Uses Android 12+ (API 31+) test provider interfaces: `cmd location set-test-provider-location`.
   * For older Android versions (6.0 to 11), coordinates are routed to the designated Mock Location App configured in **Developer Options** (`Settings -> Developer options -> Select mock location app`).
3. **Verification of Device-Reported Location**:
   * After applying coordinates, `locspoof` queries `dumpsys location` or `cmd location get-last-location` to verify what the Android device is **actually reporting**.
   * If the device still reports its original coordinates or ignores the fix, `locspoof` honestly reports the status rather than claiming a false success.

---

## 3. Installation & Setup

### Prerequisites
* **Python**: Python 3.10+
* **Android Debug Bridge (ADB)**: Part of Android SDK Platform-Tools.
  * Linux: `sudo apt install adb`
  * macOS: `brew install android-platform-tools`
  * Windows: Download Android SDK Platform-Tools and add to `PATH`.

### Quick Installation
```bash
git clone https://github.com/Sanggadiennata-me/LocSpoof.git
cd locspoof

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Verify environment
locspoof doctor
```

---

## 4. Quick Start & CLI Usage

### 1. Spoof Device Location (Shorthand Syntax)
You can provide coordinates directly as the primary argument in **DMS** or **Decimal Degrees**:

```bash
# Decimal Degrees
locspoof 55.554250 55.765611

# DMS with Degree/Minute/Second symbols
locspoof 55°33'15.3"N 55°45'56.2"E

# DMS with negative / Southern hemisphere
locspoof "6°12'10.2"S 106°49'35.8"E"

# Space-separated DMS
locspoof "55 33 15.3 N 55 45 56.2 E"
```

*Output:*
```
╭────────────────────────────────── LocSpoof ──────────────────────────────────╮
│ Location Spoofing Active                                                     │
│                                                                              │
│ Target:                                                                      │
│ 55.554250, 55.765611                                                         │
│                                                                              │
│ Device:                                                                      │
│ emulator-5554 (Pixel_8)                                                      │
│                                                                              │
│ Provider:                                                                    │
│ Android Mock Location                                                        │
│                                                                              │
│ Device Reported:                                                             │
│ 55.554250, 55.765611                                                         │
│                                                                              │
│ Status:                                                                      │
│ ACTIVE                                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
```

---

### 2. Inspect Connected Android Devices (`locspoof devices`)
List all connected emulators and physical phones, showing their Android version, model, and mock location readiness:

```bash
locspoof devices
```

*Output:*
```
─────────────────────────── ATTACHED ANDROID DEVICES ───────────────────────────

┏━━━━━━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Device Serial ┃ Type     ┃ Model   ┃ Android OS         ┃ ADB State ┃ Mock Location Support ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━┩
│ emulator-5554 │ Emulator │ Pixel_8 │ Android 15 (API 35)│ connected │ available             │
└───────────────┴──────────┴─────────┴────────────────────┴───────────┴───────────────────────┘
```

If multiple devices are connected, target a specific one with `--device` or `-d`:
```bash
locspoof --device emulator-5554 55.554250 55.765611
```

---

### 3. Check Active Spoofing Status (`locspoof status`)
Inspect active mock location, device connection, and real-time reported coordinates:

```bash
locspoof status
```

*Output:*
```
─────────────────────────── ANDROID LOCATION STATUS ────────────────────────────

╭──────────────────────────────── Device State ────────────────────────────────╮
│  Real/Physical Location    UNKNOWN / unavailable                             │
│  Spoofed Target Location   55.554250, 55.765611                              │
│  Device Reported Location  55.554250, 55.765611                              │
│  Mock Provider             ACTIVE                                            │
│  Device                    connected (emulator-5554) [Pixel_8]               │
│  Provider                  Android Mock Location / Emulator GNSS             │
╰──────────────────────────────────────────────────────────────────────────────╯

✓ VERIFIED: Device location successfully matches target coordinates.
```

For automation or scripting:
```bash
locspoof status --json
```

---

### 4. Stop Spoofing (`locspoof stop`)
Stops active location injection and restores the device back to normal GPS operation:

```bash
locspoof stop
```

---

### 5. Full State Reset & Cleanup (`locspoof reset`)
Cleans up mock providers and wipes stored coordinate configurations:

```bash
locspoof reset
```

---

## 5. Acceptance Test Cases

### Test Case 1: Google Maps on Android
1. Launch Android Virtual Device (AVD) emulator or connect a test phone with USB Debugging enabled.
2. Run `locspoof 55.554250 55.765611`.
3. Open **Google Maps** inside the Android device.
4. Tap the blue GPS target icon (**"My location"**).
5. **Expected Result**: Google Maps centers and locks the blue location dot directly on the coordinates ($55.554250, 55.765611$), NOT the host machine's physical location.

### Test Case 2: Location Sharing in Messaging / Dating / Transport Apps
1. Ensure `locspoof "6°12'10.2"S 106°49'35.8"E"` is active.
2. Open an application supporting *"Share current location"* (e.g. WhatsApp, Telegram, ride-hailing app in test mode).
3. Select *"Send your current location"*.
4. **Expected Result**: The app reads Android's `LocationManager` and shares Jakarta coordinates ($-6.202833, 106.826611$).

---

## 6. Supported Coordinate Formats

The built-in parser automatically converts any of the following formats:

| Format Name | Example Input | Parsed Latitude | Parsed Longitude |
| :--- | :--- | :--- | :--- |
| **Decimal Degrees** | `55.554250 55.765611` | `55.554250` | `55.765611` |
| **Signed Decimal** | `-6.2088, 106.8456` | `-6.208800` | `106.845600` |
| **DMS Standard** | `55°33'15.3"N 55°45'56.2"E` | `55.554250` | `55.765611` |
| **DMS Quoted** | `"55°33'15.3"N 55°45'56.2"E"` | `55.554250` | `55.765611` |
| **DMS South / West** | `"6°12'10.2"S 106°49'35.8"E"` | `-6.202833` | `106.826611` |
| **DMS Space-Separated** | `55 33 15.3 N 55 45 56.2 E` | `55.554250` | `55.765611` |

---

## 7. Security & Engineering Principles

* **Zero Shell Concatenation**: ADB arguments are executed via strictly typed parameter arrays (`safe_run([...], shell=False)`). Malloc/eval/shell injection attacks via coordinates are physically impossible.
* **Non-Destructive Testing**: `locspoof` modifies location only through official Android debug/test channels. It does not modify application APK binaries or tamper with host system root files.
* **Credential Protection**: File configuration permissions are locked to `0600` (Unix user-only permissions).

---

## 8. Anti-Spoofing & Technical Limitations

`locspoof` prioritizes technical honesty. Be aware of the following Android security realities:

* **Hardware-Backed Raw GNSS Measurements**: Applications that query raw GNSS satellite clock measurements (`GnssMeasurementsEvent`) or evaluate NMEA carrier-to-noise ratios directly from hardware baseband chips may detect that coordinates originate from mock injection.
* **Carrier / Cell Tower Triangulation**: Cellular network location (`TelephonyManager.getAllCellInfo()`) is derived from connected base station cell IDs (MCC/MNC/LAC/CID) and cannot be spoofed by modifying Android's GPS provider alone.
* **SafetyNet / Play Integrity API**: Apps verifying `BasicIntegrity` or `StrongIntegrity` may flag devices if Developer Options or USB Debugging are active.

---

## 9. Automated Testing

Run the automated test suite with `pytest`:
```bash
source .venv/bin/activate
pytest -v
```
Includes 29 tests covering coordinate parsing (DMS/decimal), boundary constraints, mock device ADB execution, and process security.

---

## 10. License

Distributed under the **MIT License**. See [`LICENSE`](file:///home/r3x/Documents/LocSpoof/LICENSE) for details.
