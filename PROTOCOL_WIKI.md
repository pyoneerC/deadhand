# DEADHAND PROTOCOL: TECHNICAL WIKI

**Version:** 1.0.0 (Release Candidate)
**Classification:** PUBLIC
**Architecture:** Zero-Knowledge, Non-Custodial Sovereign Succession

---

## 1. Executive Summary
The Deadhand Protocol is an institutional-grade, mathematically enforced succession system for digital assets. It operates as a cryptographic "dead man's switch," ensuring the seamless, trustless transfer of private keys, seed phrases, or critical data to a designated beneficiary upon the owner's incapacitation or death. 

Unlike traditional custodial services or smart contracts that introduce counterparty risk or on-chain exposure, Deadhand leverages **Information-Theoretic Security** to ensure that no single entity—including Deadhand's own cloud infrastructure—ever possesses the capability to reconstruct the master secret.

---

## 2. Cryptographic Architecture

### 2.1 Information-Theoretic Secret Sharing
At the core of the protocol is a 2-of-3 Secret Sharing algorithm. Rather than relying on polynomial interpolation (standard Shamir's Secret Sharing), Deadhand utilizes an XOR-based threshold cipher. 

1. The Master Secret ($S$) is converted to a byte array.
2. Two keys ($k_1, k_2$) are generated using the OS-level Cryptographically Secure Pseudorandom Number Generator (CSPRNG) via `os.urandom()`.
3. The third key ($k_3$) is computed as $k_3 = S \oplus k_1 \oplus k_2$.
4. The shards are distributed as follows:
   - **Shard A**: Contains $k_1$ and $k_2$
   - **Shard B**: Contains $k_2$ and $k_3$
   - **Shard C**: Contains $k_3$ and $k_1$

**Security Guarantee:** Because the cipher acts effectively as a One-Time Pad, any single shard provides mathematically zero information about the original secret. Reconstruction strictly requires $\ge 2$ unique shards.

### 2.2 Endpoint Security (AES-256-GCM)
To protect against localized threats (infostealers, physical theft), the Deadhand Desktop Client encrypts all local state data.
*   **Key Derivation:** The user's Master Password is run through `PBKDF2HMAC` utilizing SHA-256 with 480,000 iterations and a cryptographically secure random salt.
*   **Encryption Standard:** The local state (`deadhand_obsidian_state.json`), containing Shard A, is encrypted using **AES-256-GCM**.
*   **Outcome:** Shards at rest are mathematically inaccessible without the Master Password, completely neutralizing malware exfiltration vectors.

---

## 3. Operational Lifecycle

### Phase I: Provisioning & The x402 Gateway
Access to the protocol is gated by an institutional pre-hook utilizing the **x402 Payment Protocol**. 
1. The user attempts to initialize a Sovereign Vault.
2. The server middleware intercepts the request, dynamically calculating pricing based on geopolitical routing.
3. The server issues a `402 Payment Required` rejection header.
4. The client wallet settles the transaction (e.g., via Base EVM).
5. Upon settlement, the Deadhand backend cryptographically mints a unique, 24-character **Sovereign Fuse** (license key).

### Phase II: Initialization & Dispersion
Once the Sovereign Fuse is entered into the Desktop Client:
1. The user inputs their Master Secret (e.g., BIP-39 seed phrase).
2. The client locally generates Shards A, B, and C.
3. **Shard A** is encrypted via AES-256-GCM and stored locally on the Desktop.
4. **Shard B** is printed or manually handed to the Beneficiary (Air-gapped).
5. **Shard C**, along with the Beneficiary's email, is transmitted to the Deadhand Cloud via strict TLS. 

### Phase III: The Heartbeat
The Deadhand Desktop Client operates silently in the background, utilizing an Obsidian-style minimalist interface. 
*   It periodically pings the Deadhand server using an anonymized `heartbeat_token`. 
*   As long as the heartbeat is received, the server continually resets the 90-day countdown timer. 
*   No Personally Identifiable Information (PII) is transmitted during the heartbeat.

### Phase IV: The Trigger & Reconstitution
If the user dies, becomes incapacitated, or is incarcerated, the desktop client ceases to send the heartbeat.
1. Once the 90-day (configurable) deadline expires, the Deadhand Cloud executes the Trigger Protocol.
2. The system automatically dispatches an encrypted email to the designated Beneficiary.
3. The email contains **Shard C** and the link to the open-source Reconstitution Tool.
4. The Beneficiary combines **Shard C** (from the server) with **Shard B** (held physically).
5. The Master Secret is reconstructed entirely offline.

---

## 4. Threat Model Mitigation

| Threat Vector | Mitigation Strategy | Status |
| :--- | :--- | :--- |
| **Cloud Compromise** | Deadhand servers only hold Shard C. Without Shard B or A, the data is mathematical noise. | **SECURE** |
| **Local Infostealer** | Local shards are encrypted via AES-256-GCM requiring a memorized Master Password. | **SECURE** |
| **Network Interception** | Strict TLS 1.2+ enforcement ensures Shard C cannot be captured via MITM attacks. | **SECURE** |
| **State Seizure / Probate** | The system is entirely non-custodial. Deadhand LLC does not possess the keys and cannot comply with subpoenas to freeze or surrender assets. | **SECURE** |
| **Insider Threat** | Sovereign Fuses are hashed (SHA-256) before database insertion. Admins cannot mint unauthorized access. | **SECURE** |

---

## 5. Deployment & System Requirements
- **Server:** Python 3.10+, FastAPI, PostgreSQL (Neon), SQLAlchemy.
- **Client:** Windows/macOS/Linux, CustomTkinter, local cryptography modules.
- **Network:** Outbound TCP/443 (HTTPS) required for Heartbeat transmission.
- **Financial:** EVM-compatible wallet required for x402 initialization.

*For enterprise support or architectural auditing, please reference the included SBOM.*
