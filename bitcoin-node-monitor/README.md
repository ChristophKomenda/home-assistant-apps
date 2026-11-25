# Configuration and security

This app monitors a separate, existing Bitcoin Core node. It does not install or run Bitcoin Core.

## RPC

Only `getblockchaininfo`, `getnetworkinfo`, `getnettotals` and `uptime` are used. The client allowlist is not a server-side security boundary. Create dedicated credentials and restrict their permitted RPC methods on the server (Bitcoin Core `rpcauth` and `rpcwhitelist`, or an authenticated method-filtering proxy). Review `rpcwhitelistdefault` and existing users before modifying a running node; an incorrect global setting can break existing clients. Verify that other methods are denied for the monitor account. Never reuse a wallet/admin credential.

Bitcoin Core's native HTTP RPC does not provide TLS. Use a private HTTPS reverse proxy or protected private transport. The URL must have a root path, no embedded credentials, query or fragment. TLS certificate verification is enabled; use a trusted certificate. Plain HTTP requires `allow_insecure_rpc: true`; only consider it on an appropriately isolated/protected link. Do not forward port 8332 on your router or expose it publicly. No redirects or environment proxies are followed.

For Bitcoin Pi Node, RPC is intentionally not published on the host. This app cannot access that endpoint as-is. The existing host-side MQTT publisher remains the recommended option for that installation until a separately reviewed restricted transport is configured.

## MQTT

Set `mqtt_host`, `mqtt_port`, username and password for your broker. TLS is enabled by default. Plain MQTT requires explicit `allow_insecure_mqtt: true` and `mqtt_tls: false`; limit this to a trusted isolated network. Give the account permission to publish only its own `bitcoin_node_monitor/<node_id>/#` and corresponding discovery topics and subscribe to `<discovery_prefix>/status`. Select a unique `node_id` for each node. Never share screenshots of app credentials.

`poll_interval` defaults to 60 seconds. `stall_minutes` defaults to 30. The app publishes retained discovery, state and availability using QoS 1 and a last will. RPC errors mark the node offline; stale messages have expiry in HA discovery. On reconnect and HA birth, discovery is republished. Stall duration measures continuous observed lack of block-height change during initial download; it resets on monitoring restart or RPC failure, and is not a historical record of node outages.

`size_on_disk` measures blockchain data, not filesystem usage or free space. An unpruned node has no prune height. Synchronization is a heuristic using IBD and known header height; it does not prove that the node is on the best global chain.

## Validation status

Experimental. Unit tests use synthetic RPC data. Validate live RPC, MQTT reconnect, HA restart, node outage and HAOS installation before relying on alerts. ARM64/AMD64 are intended build targets. No privileged mode, host networking or Docker socket required.
