# Contributing

Thank you for helping improve local home automation.

## Choose the right repository

- Powerline2MQTT functionality, package documentation and app-store icons: [powerline2mqtt](https://github.com/ChristophKomenda/powerline2mqtt).
- Pironman IR receiver functionality, package documentation and app-store icons: [home-assistant-addon](https://github.com/ChristophKomenda/home-assistant-addon).
- Central distribution, synchronization, build validation and catalog artwork: this repository.

Do not directly edit imported app directories or regenerate hashes to hide changes. Import a published upstream release instead.

## Validate changes

Use an isolated Python environment, install `PyYAML==6.0.2`, then run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 scripts/sync_upstream.py --check
```

Run the Build app packages workflow for the proposed commit. For bot-created PRs, manually dispatch on the update branch if necessary. Review the upstream diff, permissions, dependencies and licenses. Do not merge solely because a build passed.

For hardware reports include model, chipset if known, architecture, HAOS version, app version, reproduction steps and sanitized logs. Remove credentials, tokens, MAC addresses and private network details. Distinguish build, runtime and hardware validation.
