<p align="center">
  <img src="app\static\favicon.png" alt="Deadhand Protocol Logo" width="200">
</p>

<h1 align="center">Deadhand Protocol</h1>

<p align="center">
  <b>Trustless dead man's switch for crypto inheritance.</b>
</p>

<p align="center">
  <a href="https://deadhandprotocol.com">Website</a> •
  <a href="https://deadhandprotocol.com/docs">Docs</a> •
  <a href="#quick-install">Install</a> •
  <a href="https://twitter.com/DeadhandProto">Twitter</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Audited-2ea44f?style=for-the-badge" alt="Status">
  <img src="https://img.shields.io/badge/Privacy-Zero_Knowledge-blue?style=for-the-badge" alt="Privacy">
  <img src="https://img.shields.io/badge/Encryption-Shamir's_SSS-orange?style=for-the-badge" alt="Crypto">
  <img src="https://img.shields.io/github/stars/pyoneerC/deadhand?style=for-the-badge" alt="Stars">
</p>

---

## What is this?

**You die. Your family gets $0.** 

Deadhand solves crypto inheritance without trusting a lawyer, a bank, or even us.

It uses **Shamir's Secret Sharing** to split your seed phrase into 3 "shards". 
- **Shard A**: You keep.
- **Shard B**: You give to your beneficiary.
- **Shard C**: We hold (encrypted).

If you don't check in for **90 days**, we send Shard C to your beneficiary. They combine B + C to recover your funds. 

Until then, **nobody**, not even the FBI, can access your money.

## Why use Deadhand?

| Feature | Deadhand | Traditional Wills | Exchange Custody |
| :--- | :---: | :---: | :---: |
| **Trustless** | ✅ Yes | ❌ No (Trust Lawyer) | ❌ No (Trust CEO) |
| **Cost** | **$0** | $500 - $5,000 | 0% - 1% fees |
| **Privacy** | **Client-Side** | Public Probate | KYC / Gov ID |
| **Setup Time** | **2 Mins** | Weeks | Days |
| **Censorship** | **Impossible** | Possible | Likely |

## Features

- 🛡️ **Zero Knowledge Architecture**: We never see your seed phrase. Encryption happens in *your* browser.
- ⏳ **Automated Heartbeat**: 30-day email check-ins. 90-day trigger.
- 🦀 **Rust Core Power**: High-performance Wasm crypto engine for maximum security and speed.
- 🧩 **Shamir's Secret Sharing**: Mathematically proven 2-of-3 threshold scheme.
- 🔊 **Steganography Tools**: Hide your shards inside audio files or images for plausible deniability.

## Quick Install

Want to run the protocol yourself?

```bash
# 1. Clone the repo
git clone https://github.com/pyoneerC/deadhand.git

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the server
python -m uvicorn app.main:app --reload
```

> **Note**: For production use, we strongly recommend using our hosted version at [deadhandprotocol.com](https://deadhandprotocol.com) to ensure heartbeat reliability.

## Documentation

Full documentation is available at [deadhandprotocol.com/docs](https://deadhandprotocol.com/docs).

- [Security Model](https://github.com/pyoneerC/deadhand/blob/main/docs/security.md)
- [Recovery Guide](https://deadhandprotocol.com/recover)
- [Technical Whitepaper](https://deadhandprotocol.com/blog)

## Recognition

> "Un outil open source pour léguer vos cryptos en cas de décès (sans tiers de confiance)." — **[Korben.info](https://korben.info/deadhand-protocole-heritage-crypto.html)**

> "Опенсорс-протокол для передачи крипто-наследства." — **[Habr.com](https://habr.com/ru/news/988348/)**

## Contributing

We love contributors! 

1. Fork the repo.
2. Create a new branch.
3. Make your changes (and add tests!).
4. Submit a PR.

**Current Priorities:**
- Hardware wallet integration (Ledger/Trezor)
- Mobile app wrapper (React Native)
- More steganography formats (Video/PDF)

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPL-3.0)**. 
- ✅ **Free** for personal, commercial, and educational use.
- ✅ **Open** to audit, research, and contribution.
- ⚖️ **Copyleft**: Derivative works must also be licensed under AGPL-3.0.

---

## Ownership

Deadhand is a proprietary protocol developed, owned, and maintained by **half radiation LLC**.

<p align="center">
  <b>Built for sovereignty.</b><br>
  Developed and maintained by half radiation LLC.
</p>
