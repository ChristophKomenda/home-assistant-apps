# Security policy

This independent community repository distributes upstream app sources. Experimental and prerelease packages are not guaranteed to be production-ready. No formal response-time or long-term support guarantee is offered.

## Reporting a vulnerability

Use the GitHub repository Security tab and private vulnerability reporting if enabled. Otherwise contact the maintainer privately via the contact options on [the maintainer profile](https://github.com/ChristophKomenda). Do not publish exploit details, credentials or private network information in public issues. Include the affected app and version, impact and safe reproduction details.

## Operational guidance

- Use a dedicated, scoped MQTT account and a trusted local network; do not expose MQTT publicly.
- Use dedicated, server-side restricted Bitcoin RPC credentials and verified TLS. Never expose RPC publicly.
- Keep Home Assistant and dependencies updated, and review requested device/network capabilities before installation.
- Do not run duplicate instances against the same hardware or MQTT identity.
- Upstream import checks verify recorded content integrity; they are not an independent signature or security audit.
- Review upstream code, dependency licenses and permissions before merging updates. Build checks do not prove runtime security.
