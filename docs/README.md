# Deadhand Technical Documentation

> **The Sovereign Protocol for Cryptographic Inheritance.**

Deadhand is a trustless dead man's switch designed to solve the "hit-by-a-bus" problem for the Web3 generation. It ensures that your private keys, seed phrases, and critical digital secrets aren't lost to the void if you go silent, while maintaining zero-knowledge privacy and full sovereignty.

## ⚡ The Deadhand Core Philosophy

1.  **Zero Trust Architecture**: We never see your seed phrase. We never see your full key. The math happens on your machine.
2.  **Autonomous Watchdog**: Our system only releases a shard when your user-defined "heartbeat" fails.
3.  **No Single Point of Failure**: Shards are geographically and technically distributed between you, your beneficiaries, and the Deadhand vault.
4.  **Open Source & Verifiable**: Don't trust us. Verify the math.

---

## 📚 Documentation Index

### 1. [Getting Started](getting-started.md)
A high-level guide for first-time users. Protocol setup, shard distribution strategy, and best practices for naming beneficiaries.

### 2. [How It Works](how-it-works.md)
The technical deep-dive into Shamir's Secret Sharing (SSS), the 2-of-3 threshold model, and the autonomous heartbeat mechanism.

### 3. [Security Model](security.md)
Threat modeling, encryption-at-rest strategies, and the cryptographic proof of why even a compromised Deadhand database cannot reveal your keys.

### 4. [API Reference](api-reference.md)
Integrate Deadhand heartbeat triggers into your own hardware wallets, CLIs, or custom infrastructure.

### 5. [Self-Hosting](self-hosting.md)
Instructions for sovereign individuals and institutions wanting to run their own private instance of the Deadhand Protocol.

### 6. [FAQ](faq.md)
The most common questions about inheritance laws, lost tokens, and emergency recovery.

---

## 🚀 Quick Technical Overview

Deadhand utilizes a **2-of-3 Threshold Secret Sharing** scheme:

*   **Shard A**: Stored by you (The Owner).
*   **Shard B**: Managed by your Beneficiary.
*   **Shard C**: Encrypted and held in the Deadhand Vault.

**Scenario - The Switch Triggers:**
If you fail to check in (Heartbeat), Deadhand autonomously releases **Shard C** to your Beneficiary. They combine it with **Shard B**, reconstruct the secret, and secure your legacy.

---

## 🛠️ Contribution & Development

Deadhand is built for the community. We welcome PRs for:
*   New recovery tool integrations.
*   Localized legal guides for digital inheritance.
*   Performance optimizations for the SSS logic.

[GitHub Repository](https://github.com/pyoneerC/deadhand) | [Report a Bug](https://github.com/pyoneerC/deadhand/issues)
