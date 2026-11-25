<div align="center">

<img src="assets/community-logo.svg" width="440" alt="Community Apps — Local-first home automation">

# Home Assistant Community Apps

**Local-first hardware monitoring and automation. One repository, multiple apps.**

[![Validation](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/validate.yml/badge.svg)](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/validate.yml)
[![Build checks](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/build-apps.yml/badge.svg)](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/build-apps.yml)
[![Release sync](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/sync-upstream.yml/badge.svg)](https://github.com/ChristophKomenda/home-assistant-apps/actions/workflows/sync-upstream.yml)

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FChristophKomenda%2Fhome-assistant-apps)

[Apps](#available-apps) · [Installation](#installation) · [Updates](#updates-and-validation) · [Support](#support)

</div>

## Available apps

| App | What it does | Validation |
| --- | --- | --- |
| <img src="assets/powerline2mqtt.svg" width="40" alt=""> **[Powerline2MQTT](powerline2mqtt)** | Local HomePlug monitoring via MQTT | ARM64 Docker tested; HAOS experimental |
| <img src="assets/pironman-ir-receiver.svg" width="40" alt=""> **[Pironman IR Receiver](pironman-ir-receiver)** | Local infrared reception on Pironman 5 Max | Independently tested in original HAOS repository; central distribution not runtime tested |

### Powerline2MQTT

Monitor compatible Powerline adapters without cloud services or adapter IP addresses. Automatically discover Home Assistant devices, physical link rates, connectivity and bridge diagnostics. RC.2 was tested with three adapters and 31 available entities on one ARM64 installation. G.hn is not supported.

[Setup and options](powerline2mqtt/DOCS.md) · [Source project](https://github.com/ChristophKomenda/powerline2mqtt) · [Changelog](powerline2mqtt/CHANGELOG.md)

### Pironman IR Receiver

Use the Pironman 5 Max infrared receiver locally with HAIR and the existing Pironman 5 HACS integration. The host must expose the appropriate LIRC device. The HACS-linked mode is optional and has been independently tested upstream. Receive-only.

[Setup and requirements](pironman-ir-receiver/README.md) · [Source project](https://github.com/ChristophKomenda/home-assistant-addon) · [HACS integration](https://github.com/ChristophKomenda/pironman5-homeassistant-container)

## Installation

1. Use the installation button above, or add `https://github.com/ChristophKomenda/home-assistant-apps` to the Home Assistant OS app store repositories.
2. Select an app and read its requirements before installing.
3. Configure it, start it and inspect its logs. Powerline2MQTT requires a reachable MQTT broker and the correct physical Ethernet interface. IR requires compatible hardware and host configuration.

> [!IMPORTANT]
> This is an independent community repository, not an official Home Assistant or SunFounder app store. Both packages still require installation/runtime validation from this central repository. Existing installations in another repository have different Supervisor IDs. Back up configuration, stop the old app before starting its replacement, and do not run duplicate MQTT collectors with the same node ID.

## Updates and validation

Published upstream releases are checked daily and on manual workflow dispatch. Updates generate reviewable pull requests and never merge automatically. Powerline2MQTT accepts newer prereleases until a stable version is installed; the IR receiver accepts stable `pironman-ir-v*` releases only.

- [Pinned upstream sources](SOURCES.md) and [`sources.lock.json`](sources.lock.json) record exact versions, commits and content hashes.
- Static CI validates package syntax and provenance; separate native ARM64/AMD64 Docker build checks cover declared architectures. These are build checks, not hardware or HAOS runtime tests.
- For automated update PRs, manually dispatch the build workflow on the update branch if no CI runs appear. Review results, permissions, license obligations and runtime compatibility before merging.
- App directories are upstream-owned: make app fixes and in-store icon changes in the source projects. Repository presentation artwork is kept outside imported app folders to preserve their hashes.
- No prebuilt images are published by this repository. Dependency redistribution obligations must be reviewed before image publication.

## Support

Report app-specific issues in the linked source project; report distribution or synchronization issues [here](https://github.com/ChristophKomenda/home-assistant-apps/issues). See [contributing](CONTRIBUTING.md) and [security](SECURITY.md).

**Planned:** Bitcoin Node Monitor (not available for installation).

## Licensing

Each app retains its original license and copyright notices. See its directory. Repository artwork is original to this project; see [asset license](assets/LICENSE.md).

Maintained by [Christoph Komenda](https://github.com/ChristophKomenda).
