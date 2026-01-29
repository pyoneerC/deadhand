<p align="center">
  <a href="https://www.youtube.com/watch?v=Q4e-JX1sfjo">
    <img src="https://img.youtube.com/vi/Q4e-JX1sfjo/maxresdefault.jpg" alt="Watch: What happens to your crypto when you die?" width="100%">
  </a>
  <br>
  <em>▶️ Watch: What happens to your crypto when you die?</em>
</p>

# Deadhand

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/License-BSL_1.1-yellow?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Crypto-Shamir's_SSS-orange?style=for-the-badge" alt="Crypto">
  <br><br>
  <a href="https://deepwiki.com/pyoneerC/Deadhand"><img src="https://deepwiki.com/badge.svg" alt="Ask DeepWiki"></a>
  <a href="https://www.shipit.buzz/products/dead?ref=badge" target="_blank"><img src="https://www.shipit.buzz/api/products/dead/badge?theme=dark" alt="Featured on Shipit" width="170" height="54"></a>
  <a href="https://www.producthunt.com/products/shardium?utm_source=badge-featured&utm_medium=badge&utm_campaign=badge-shardium" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1051329&theme=light" alt="Shardium - Product Hunt" width="250" height="54"></a>
</p>

### Trustless dead man's switch for crypto inheritance using Shamir's Secret Sharing

---

## The Problem

You die. Your crypto dies with you. Your family has no idea how to access it.

Traditional solutions require trusting someone with your seed phrase. That's not acceptable.

## The Solution

Deadhand uses **Shamir's Secret Sharing** to split your seed phrase into 3 shards. No single entity (including us) has the full key.

> *Inspired by [@PixOnChain](https://x.com/PixOnChain/status/2000589935980458262)*

## Features

- **Client-Side Encryption** - Your seed phrase never leaves your browser unencrypted
- **Shamir's Secret Sharing** - Mathematically proven 2-of-3 threshold scheme
- **Automated Dead Man's Switch** - 30-day heartbeat checks, triggers after 90 days
- **PDF Export** - Print shards for physical backup
- **Beneficiary System** - Seamless crypto inheritance
- **Zero Trust Architecture** - Even we can't access your keys
- **Source-Available** - Inspect the full code, but commercial use requires a subscription


## How It Works

### Shard Distribution

```mermaid
flowchart LR
    subgraph Browser["Client Browser"]
        SEED["Seed Phrase"]
        SPLIT["Shamir Split (2-of-3)"]
    end
    
    SEED --> SPLIT
    SPLIT --> A["Shard A<br/>User Keeps"]
    SPLIT --> B["Shard B<br/>Beneficiary"]
    SPLIT --> C["Shard C<br/>Server"]
    
    style SEED fill:#f59e0b,color:#000
    style A fill:#14b8a6,color:#000
    style B fill:#eab308,color:#000
    style C fill:#8b5cf6,color:#fff
```

### Dead Man's Switch Flow

```mermaid
sequenceDiagram
    participant U as User
    participant S as Deadhand Server
    participant B as Beneficiary

    Note over U,S: Every 30 days
    S->>U: "Are you alive?" Email
    
    alt User Responds
        U->>S: Click heartbeat link
        S->>S: Reset 30-day timer
    else User Missing (90 days)
        S->>B: Email Shard C
        Note over B: Combines Shard B + C
        B->>B: Recovers Seed Phrase
    end
```

### Recovery Combinations

```mermaid
flowchart TB
    subgraph Valid["Valid Recovery (Any 2 Shards)"]
        AB["A + B"] --> RECOVER1["Seed Recovered"]
        AC["A + C"] --> RECOVER2["Seed Recovered"]
        BC["B + C"] --> RECOVER3["Seed Recovered"]
    end
    
    subgraph Invalid["Invalid (Single Shard = Zero Info)"]
        A1["A alone"] --> FAIL1["Nothing"]
        B1["B alone"] --> FAIL2["Nothing"]
        C1["C alone"] --> FAIL3["Nothing"]
    end
    
    style RECOVER1 fill:#22c55e,color:#000
    style RECOVER2 fill:#22c55e,color:#000
    style RECOVER3 fill:#22c55e,color:#000
    style FAIL1 fill:#ef4444,color:#fff
    style FAIL2 fill:#ef4444,color:#fff
    style FAIL3 fill:#ef4444,color:#fff
```

### Trust Model

| Scenario | Outcome |
|----------|---------|
| Server hacked | Attacker has only Shard C → **Useless** |
| Beneficiary is malicious | They have only Shard B → **Useless** |
| You lose Shard A | Combine B + C → **Still recoverable** |
| You die | Server sends C to beneficiary → **B + C = Recovery** |

---

### Tech Stack

*   **Backend**: FastAPI, PostgreSQL, SQLAlchemy
*   **Frontend**: HTML, TailwindCSS, HTMX
*   **Cryptography**: `secrets.js` (Shamir's Secret Sharing) running in browser
*   **Hosting**: Vercel

### How to Run

1.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

2.  Run the server:
    ```bash
    python -m uvicorn app.main:app --reload --port 8000
    ```

3.  Visit `http://localhost:8000`

---

## Contributing

Contributions are welcome! Here's how you can help:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### Areas We Need Help With:
- [ ] Production-grade email integration
- [ ] Multi-language support
- [ ] Mobile app wrapper
- [ ] Hardware wallet integration
- [ ] Additional threshold schemes (3-of-5, etc.)

---

## License

This project is licensed under the **Business Source License 1.1 (BSL 1.1)**.

### What This Means

| Use Case | Allowed? |
|----------|----------|
| Personal use | ✅ Free |
| Security auditing | ✅ Free |
| Educational/research | ✅ Free |
| Non-commercial self-hosting | ✅ Free |
| Commercial/production use | ❌ Requires Commercial License |

### Change Date

On **January 28, 2030**, this code automatically converts to **AGPL v3.0** (fully open source).

### Why BSL?

We believe security software should be transparent. You should be able to verify that your seed phrase is safe by reading the code yourself. But building and maintaining security infrastructure is expensive. BSL ensures:

1. **Trust**: Anyone can audit the code
2. **Sustainability**: The project can be maintained long-term
3. **Eventual Freedom**: Code becomes open source after 4 years

For commercial licensing: **max@deadhandprotocol.com**

See [LICENSE](./LICENSE) for full terms.

---

<p align="center">
  <img src="app/static/guardian.jpg" alt="Guardian" width="600">
</p>

<p align="center">
  <b>Star this repo if you find it useful!</b>
</p>
