# Security Model

## Overview

deadhand is designed with a **zero-trust architecture**. This document explains our security model and threat analysis.

## Core Security Principles

### 1. Client-Side Splitting

Your seed phrase is **never transmitted** to our servers in its original form:

```
Browser: seed phrase → Shamir split → 3 shards
Server: only receives Shard C (1 of 3)
```

### 2. Information-Theoretic Security

Shamir's Secret Sharing provides **perfect secrecy**:

- 1 shard = 0 bits of information about the secret
- This is mathematically proven, not just "hard to break"
- No future computing advances (quantum, etc.) can change this

### 3. Minimal Trust Requirements

| Component | Trust Level | Why |
|-----------|-------------|-----|
| Your browser | Must trust | All crypto happens here |
| Our server | Minimal | Only stores 1 shard |
| Beneficiary | Minimal | Only has 1 shard |
| Network | None | Shards are useless individually |

## Threat Analysis

### Threat: Server Compromise

**Scenario**: Attacker gains full access to deadhand database.

**Impact**: They obtain all encrypted Shard C values.

**Mitigation**: Shard C alone is useless. They cannot recover any seed phrase without Shard B (held by beneficiaries physically).

**Risk Level**: ✅ Low

---

### Threat: Malicious Beneficiary

**Scenario**: Beneficiary wants to steal funds before you die.

**Impact**: They have Shard B.

**Mitigation**: Shard B alone is useless. They need Shard C, which is only released when the dead man's switch triggers.

**Risk Level**: ✅ Low

---

### Threat: Malicious deadhand Employee

**Scenario**: Insider tries to steal user funds.

**Impact**: They have access to encrypted Shard C.

**Mitigation**: Same as server compromise—Shard C alone is useless.

**Risk Level**: ✅ Low

---

### Threat: Man-in-the-Middle Attack

**Scenario**: Attacker intercepts traffic between user and server.

**Impact**: They could capture Shard C during transmission.

**Mitigation**: 
1. Use HTTPS (TLS encryption)
2. Shard C alone is still useless

**Risk Level**: ✅ Low (with HTTPS)

---

### Threat: Compromised Browser/Device

**Scenario**: User's device has malware.

**Impact**: Malware could capture the seed phrase before splitting.

**Mitigation**: 
1. Recommend splitting while offline
2. Use a clean/dedicated device
3. This is a user responsibility issue

**Risk Level**: ⚠️ Medium (user responsibility)

---

### Threat: Beneficiary + Server Collusion

**Scenario**: Beneficiary and deadhand employee work together.

**Impact**: They could combine Shard B + Shard C.

**Mitigation**: 
1. Users should trust their beneficiary (they're inheriting anyway)
2. deadhand has no way to identify which Shard C belongs to which beneficiary
3. Legal consequences for deadhand

**Risk Level**: ⚠️ Medium (requires careful beneficiary selection)

## Security Best Practices

### For Users

1. **Split offline**: Disconnect internet before entering seed phrase
2. **Verify the code**: Check that you're running official deadhand
3. **Multiple backups**: Store Shard A in multiple secure locations
4. **Physical Shard B**: Print Shard B, don't send digitally
5. **Dedicated email**: Use a separate email for heartbeat notifications
6. **Test recovery**: Verify you can recover with test data first

### For Self-Hosters

1. **HTTPS only**: Never run without TLS
2. **Database encryption**: Encrypt at rest
3. **Access controls**: Limit who can access the database
4. **Audit logs**: Log all access to shard data
5. **Regular backups**: Encrypted, off-site backups

## Audit Status

⚠️ **This software has not been professionally audited, yet.**

Before using in production:
1. Conduct a third-party security audit
2. Review the `secrets.js` library
3. Penetration test the application

## Responsible Disclosure

Found a vulnerability? Please email security@deadhandprotocol.com (or open a GitHub issue).

We commit to:
- Acknowledging reports within 48 hours
- Providing updates on fixes
- Crediting researchers (if desired)

<u>deadhand will NEVER ask for your shards, or any other information that could be used to access your crypto.</u>