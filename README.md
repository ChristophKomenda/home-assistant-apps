# Home Assistant Community Apps

**Local-first. Independent. Open Source.**

A collection of community-maintained apps for Home Assistant OS,
focused on hardware integration, local monitoring and automation.

## Installation

[![Add repository to Home Assistant](https://my.home-assistant.io/badges/supervisor_add_addon_repository.svg)](https://my.home-assistant.io/redirect/supervisor_add_addon_repository/?repository_url=https%3A%2F%2Fgithub.com%2FChristophKomenda%2Fhome-assistant-apps)

Alternatively, add this repository through Settings > Apps.

## Available apps

| App | Release channel | Validation |
| --- | --- | --- |
| [Powerline2MQTT](powerline2mqtt) | Experimental / release candidate | Docker ARM64 validated; HAOS experimental |
| [Pironman IR Receiver](pironman-ir-receiver) | Stable upstream releases | Independent HAOS testing in original repository |

### Powerline2MQTT

Monitor compatible HomePlug adapters locally through MQTT.

- Automatic Home Assistant MQTT discovery
- 31 entities validated on one ARM64 installation
- Read-only Ethernet management queries
- No cloud services required
- Experimental HAOS support

[Source project](https://github.com/ChristophKomenda/powerline2mqtt)

### Pironman IR Receiver

Receive infrared signals using the Pironman 5 Max hardware.

- Local infrared reception
- HACS integration interoperability
- HAIR support
- Event-based communication

[Source project](https://github.com/ChristophKomenda/home-assistant-addon)

## Planned apps

- Bitcoin Node Monitor

## Migration

Apps installed from another repository have different Supervisor IDs.
Back up the existing configuration before migration.
Stop the old app before starting its replacement.
Do not run duplicate collectors with the same MQTT node ID.

This distribution repository requires its own installation
and runtime validation.

## Licensing

Each app retains its original license and copyright notices.
See the corresponding app directories.

## Maintainer

[Christoph Komenda](https://github.com/ChristophKomenda)

Independent community projects, not official Home Assistant apps.

## Release synchronization

Published upstream releases are checked daily and on manual workflow dispatch. Updates open a pull request, never merge automatically. Powerline2MQTT accepts newer prereleases until a stable version is installed; the IR receiver accepts stable `pironman-ir-v*` releases only. See [pinned sources](SOURCES.md) and `sources.lock.json` for exact versions and commits. App directories are upstream-owned; make fixes and branding changes in the source projects. Static checks do not replace HAOS runtime tests or dependency license review. Existing app installations from other repositories are not migrated automatically.
