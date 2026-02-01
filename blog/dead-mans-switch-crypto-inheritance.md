---
title: "Dead Man's Switch: How to Automate Crypto Inheritance"
slug: "dead-mans-switch-crypto-inheritance"
description: "A dead man's switch automatically triggers an action when you stop responding. Learn how this mechanism enables trustless cryptocurrency inheritance."
author: "pyoneerC"
date: "2025-12-15"
tags: "dead mans switch, automation, inheritance, trustless"
image: "/static/blog/dead-mans-switch.jpg"
---


**TL;DR**: A dead man's switch is a mechanism that triggers automatically when you stop responding. Combined with Shamir's Secret Sharing, it enables trustless crypto inheritance without giving anyone premature access.

## What Is a Dead Man's Switch?

The term comes from early train locomotives. Drivers had to keep a pedal pressed. If the driver fell asleep or died, the pedal would release and automatically stop the train.

In the digital world, a dead man's switch is any system that requires periodic confirmation that you are still active. If you stop confirming, it assumes something happened and takes action.

## Why Crypto Needs This

The challenge with crypto inheritance is timing:
- **Too early**: Someone could steal your funds while you are alive.
- **Too late**: Your heirs can't find or access the keys.
- **Just right**: Access transfers exactly when needed.

A dead man's switch solves the timing problem automatically.

## How deadhand's Switch Works

### The Timeline

- **Day 0**: You create a vault and activate the switch.
- **Day 1 to 29**: Nothing happens (you are presumably active).
- **Day 30**: We send you an email: "Are you still there?"
- **Day 30 to 59**: If you click the link, your timer resets to Day 0.
- **Day 60**: Final warning email.
- **Day 90**: If no response, Shard C is sent to your beneficiary.

### Why 90 Days?

We chose 90 days as the default because:
- It is long enough to handle vacations or hospital stays.
- It is short enough that heirs do not have to wait years.
- Multiple reminders prevent accidental triggers.

Note: We are working on customizable timers (30 days to 1 year) for pro users.

## The Trust Model

deadhand is designed to be trustless.

### What deadhand Has
- Your email address.
- Your beneficiary's email address.
- Shard C (encrypted and useless alone).

### What deadhand Does Not Have
- Your seed phrase.
- Shard A (you keep this).
- Shard B (your beneficiary keeps this).
- Any ability to access your funds.

Even if deadhand were compromised, Shard C alone reveals zero information about your seed phrase.

## Security Considerations

### What if deadhand is hacked?

Hackers would get a database of encrypted Shard C values. Without the matching Shard A or Shard B, these are worthless. It is like having one piece of a complex puzzle: no picture emerges.

### What if the email goes to spam?

We send from a verified domain with proper SPF/DKIM records. We also send multiple reminders over a 60-day period. We recommend:
1. Adding our email to your contacts.
2. Checking your spam folder once a month.
3. Setting a personal calendar reminder.

### What if the switch triggers prematurely?

If you forget to check in and Shard C is sent to your beneficiary, they still cannot access your funds unless they have Shard B. If they have Shard B, you should only give it to someone you trust.

### Alternative Approaches

For a deep technical audit of how these methods compare to institutional solutions like Casa or Unchained, read our [2026 Crypto Inheritance guide](/blog/crypto-inheritance-comparison-guide).

### Google Inactive Account Manager
Google offers a similar feature for Google accounts. After several months of inactivity, it can share data with contacts. But it only works for data within Google's ecosystem.

### Lawyers and Wills
Traditional estate planning can include crypto instructions. But lawyers are often slow, expensive, and may not understand how to protect a seed phrase securely.

### Metal Plates in a Safe
Some people stamp their seed phrase on metal and put it in a safe deposit box. This works, but it requires your heirs to find the box and have the legal right to access it.

## The deadhand Advantage

We combine the best parts of these approaches:

- **Automated**: No manual action needed when you disappear.
- **Trustless**: We cannot access your funds.
- **Simple**: No technical knowledge required.
- **Secure**: Shamir's math protects against theft.
- **Reversible**: You can recover with Shard A and B at any time.

## Real-World Scenarios

### Scenario 1: You Pass Away
- Day 30: Email sent (no response).
- Day 60: Final warning (no response).
- Day 90: Shard C sent to beneficiary.
- Day 91: Beneficiary combines B+C, recovers seed, accesses funds.

### Scenario 2: You are Hospitalized
- Day 30: Email sent to your inbox.
- Day 45: You recover and click the link.
- Timer resets. No shards are sent.

### Scenario 3: You Forget
- Day 30: Email sent (you miss it).
- Day 60: Final warning (you notice).
- Day 61: You click the link.
- Timer resets. Crisis averted.

## Getting Started

Setting up your dead man's switch takes 5 minutes:

1. Go to [deadhandprotocol.com](https://deadhandprotocol.com)
2. Enter your seed phrase (client-side only).
3. Download or print Shard A and B.
4. Enter your email and beneficiary's email.
5. Activate the switch.

**Cost**: $0 for the first 50 early bird users. We are in public beta and building trust.

---

*Questions? Check our [FAQ](/docs/faq) or [contact us](mailto:hello@deadhandprotocol.com).*
