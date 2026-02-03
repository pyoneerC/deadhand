# Self-Hosting Guide

For institutions, family offices, or high-conviction sovereign individuals, Deadhand can be run as a private, isolated instance.

## Prerequisites

-   Docker & Docker Compose
-   SMTP Server (for heartbeat alerts)
-   PostgreSQL
-   SSL Certificate (Recommended)

## Quick Start

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/pyoneerC/deadhand.git
    cd deadhand
    ```

2.  **Configure Environment**
    Copy `.env.example` to `.env` and fill in your database credentials and SMTP settings.

3.  **Launch with Docker**
    ```bash
    docker-compose up -d
    ```

## Security Recommendations

-   **Database Encryption**: Use LUKS or AWS KMS to encrypt your PostgreSQL volumes at rest.
-   **Hardware HSM**: For enterprise instances, we support hooking the `encrypt_shard` function into a Hardware Security Module.
-   **Isolated Network**: Run the watchdog service on a VPC with restricted egress rules.

---

## Maintenance

The Deadhand service is lightweight and requires minimal maintenance. We recommend setting up a secondary monitoring tool (like UptimeRobot) to ensure your self-hosted watchdog is always online.
