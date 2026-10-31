# Quad9 Secure DNS-over-HTTPS in Firefox

Configure Firefox to use **Quad9's recommended secure DNS service** over DNS-over-HTTPS (DoH).

Quad9 offers several resolver configurations. This setup uses its **recommended secure option**, which provides:

- DNS-over-HTTPS encryption
- Malicious-domain blocking
- DNSSEC validation
- No EDNS Client Subnet (ECS), avoiding the additional client-location information that ECS exposes

See Quad9's official [Service Addresses & Features](https://quad9.net/service/service-addresses-and-features/) page for the available configurations.

## Setup

In Firefox:

1. Open **Settings → Privacy & Security**.
2. Scroll to **DNS over HTTPS**.
3. Open **Advanced settings**.
4. Select **Custom Protection**.
5. Choose the custom provider option and enter:

```text
https://dns.quad9.net/dns-query
```

For strict fail-closed behavior, enable **Always warn me if secure DNS isn't available**. Otherwise, Firefox may fall back to another resolver when Quad9 can't be reached.

## Why Quad9?

- **Encrypted DNS** — DNS requests between Firefox and Quad9 are sent over HTTPS instead of ordinary plaintext DNS.
- **Threat blocking** — Quad9 blocks domains identified as malicious by its threat-intelligence sources.
- **DNSSEC validation** — helps protect against forged or manipulated DNS responses.
- **Privacy** — Quad9 states that it doesn't collect or record end-user IP addresses.
- **No ECS by default** — the recommended secure service doesn't send EDNS Client Subnet information to authoritative DNS servers.
- **Independent resolver** — Firefox doesn't simply use the DNS resolver supplied by the current ISP or network.

## What This Does Not Do

DNS-over-HTTPS isn't a VPN or anonymity system. It protects DNS traffic between Firefox and Quad9, but doesn't conceal your IP address from websites or encrypt other traffic that isn't already protected separately.

## Verify

Visit:

```text
https://on.quad9.net/
```

Quad9 should report that its resolver is being used.
