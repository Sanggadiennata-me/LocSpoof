/**
 * LocSpoof Serverless Cryptographic License Key Engine
 * ----------------------------------------------------
 * Pure zero-database cryptographic signature system using standard HMAC-SHA256.
 * Completely offline and serverless: verification is 100% mathematical.
 * Keys cannot be forged or tampered with without the Master Secret.
 */

import CryptoJS from 'crypto-js';

export const MASTER_SIGNING_SECRET = "LOCSPOOF_SEC_KEY_9d8f3b2a1c7e4a6f9012345678abcdef0123456789abcdef";

// Base64URL helpers (safe for copy/pasting in URLs, keys, textboxes)
function toBase64Url(str) {
  return btoa(unescape(encodeURIComponent(str)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=+$/, '');
}

function fromBase64Url(b64) {
  b64 = b64.replace(/-/g, '+').replace(/_/g, '/');
  while (b64.length % 4) {
    b64 += '=';
  }
  return decodeURIComponent(escape(atob(b64)));
}

/**
 * Generate a Cryptographic License Key for a user (Serverless / No DB)
 * @param {Object} options
 * @param {string} options.username - The name or identifier for the user
 * @param {string} options.role - "OWNER" | "VIP" | "USER"
 * @param {number|null} options.durationDays - Days valid, or null/0 for lifetime
 * @param {Array<string>} [options.features] - Enabled features
 * @returns {string} The formatted license key
 */
export function generateLicenseKey({
  username,
  role = "USER",
  durationDays = null,
  features = ["map", "spoof", "browser", "wireless"]
}) {
  const now = Math.floor(Date.now() / 1000);
  const exp = durationDays ? now + durationDays * 86400 : 0; // 0 = Lifetime

  const payload = {
    sub: username.trim().toLowerCase(),
    role: role.toUpperCase(),
    iat: now,
    exp: exp,
    feat: features
  };

  const payloadJson = JSON.stringify(payload);
  const payloadB64 = toBase64Url(payloadJson);
  const signature = CryptoJS.HmacSHA256(payloadB64, MASTER_SIGNING_SECRET).toString(CryptoJS.enc.Hex).slice(0, 32);

  // Format: LOCSPOOF-<ROLE>-<PAYLOAD_B64>-<SIG>
  return `LOCSPOOF-${payload.role}-${payloadB64}-${signature}`;
}

/**
 * Verify and parse a License Key
 * @param {string} rawKey - The license key entered by the user
 * @returns {{ valid: boolean, payload: Object|null, error: string|null }}
 */
export function verifyLicenseKey(rawKey) {
  if (!rawKey || typeof rawKey !== 'string') {
    return { valid: false, payload: null, error: "Key cannot be empty." };
  }

  const cleaned = rawKey.trim();
  const parts = cleaned.split('-');

  if (parts.length < 4 || parts[0] !== "LOCSPOOF") {
    return { valid: false, payload: null, error: "Format key tidak valid. Harus dimulai dengan LOCSPOOF-" };
  }

  const role = parts[1];
  const payloadB64 = parts[2];
  const signature = parts[3];

  // Verify HMAC signature
  const expectedSig = CryptoJS.HmacSHA256(payloadB64, MASTER_SIGNING_SECRET).toString(CryptoJS.enc.Hex).slice(0, 32);
  if (signature.toLowerCase() !== expectedSig.toLowerCase()) {
    return { valid: false, payload: null, error: "Signature tidak cocok! Key ini palsu atau telah dimodifikasi." };
  }

  // Parse payload
  try {
    const payloadJson = fromBase64Url(payloadB64);
    const payload = JSON.parse(payloadJson);

    // Check expiration
    if (payload.exp && payload.exp > 0) {
      const now = Math.floor(Date.now() / 1000);
      if (now > payload.exp) {
        const expiredDate = new Date(payload.exp * 1000).toLocaleDateString();
        return { valid: false, payload, error: `Key ini sudah kedaluwarsa pada ${expiredDate}.` };
      }
    }

    return {
      valid: true,
      payload,
      error: null
    };
  } catch (err) {
    return { valid: false, payload: null, error: "Gagal membaca data key: " + err.message };
  }
}

// Master Key for Owner (r3x)
// Created with Owner Role, Lifetime Access, Unlimited Feats
export const MASTER_OWNER_KEY = "LOCSPOOF-OWNER-eyJzdWIiOiJyM3gtZm91bmRlci1tYXN0ZXIiLCJyb2xlIjoiT1dORVIiLCJpYXQiOjE3OTMyNjUyODAsImV4cCI6MCwiZmVhdCI6WyIqIl19-bb998ab22ac851fcaffff8deacff9918";
