# Pironman 5 Max IR Receiver for Home Assistant OS

> **Community-maintained — independently validated on Home Assistant OS, including the new HACS-linked mode.** This independently maintained community add-on was proposed upstream in
> [SunFounder PR #26](https://github.com/sunfounder/home-assistant-addon/pull/26),
> but SunFounder declined adding it to their maintained add-ons. The
> default standalone mode does not require the Pironman 5 HACS integration;
> the optional `pironman5` mode uses that integration directly.

This optional add-on reads the Pironman 5 Max's **built-in IR receiver on GPIO13**
through the Linux LIRC MODE2 character device `/dev/lirc0`, and forwards raw
pulse/space frames using the Home Assistant Supervisor token. In `pironman5`
mode, the existing HACS integration exposes the native `InfraredReceiverEntity`;
in `standalone` mode, the separately installed `sunfounder_ir` companion does so.

This is **receive-only**. It does not turn the IR receiver into a transmitter.

## Find your setup path

- **New HAOS installation:** Use the [recommended Pironman 5 HACS-linked path](#recommended-use-the-existing-pironman-5-hacs-integration-no-manual-copying).
- **Existing standalone user:** Keep your current setup, or follow [legacy instructions](#legacy-standalone-installation).
- **Only need monitoring, fan, RGB or OLED controls?** Install the [Pironman 5 HACS integration](https://github.com/ChristophKomenda/pironman5-homeassistant-container); this IR add-on is optional.

## Requirements

- Raspberry Pi 5 with Pironman 5 Max; Home Assistant OS on aarch64.
- Home Assistant Core **2026.6+**, with the native infrared receiver platform.
- Kernel configured with `dtoverlay=gpio-ir,gpio_pin=13` and `/dev/lirc0`
  available on the host. Exact HAOS boot-overlay procedure must be verified for
  the user's installation; do not change boot partitions blindly.
- HAIR installed if learning remotes is desired.

## Recommended: use the existing Pironman 5 HACS integration (no manual copying)

For new installations, use the `pironman5` output mode with the maintained
[Pironman 5 integration](https://github.com/ChristophKomenda/pironman5-homeassistant-container).
This avoids installing the standalone `sunfounder_ir` custom component.

1. Install **Pironman 5** from HACS and restart Home Assistant.
2. Add/configure the Pironman 5 device using its reachable REST API (normally port `34001`).
3. Under the Pironman 5 integration options enable the experimental IR receiver, and
   set its **IR bridge device ID** to exactly the add-on `receiver_id`.
4. In Home Assistant's **Add-on Store → ⋮ → Repositories**, add
   `https://github.com/ChristophKomenda/home-assistant-addon`, then
   install **Pironman IR Receiver v0.2.0+** with:

   ```yaml
   receiver_id: pironman5-max
   event_mode: pironman5
   debug: false
   ```

5. Ensure the Pi's `gpio-ir` overlay is enabled and `/dev/lirc0` exists. Start the add-on.
6. If upgrading from `sunfounder_ir`, disable the old integration to avoid duplicate receivers.
7. **Reload the Pironman 5 integration** after updating the add-on or changing IR mode.
8. Select the **Pironman 5** IR receiver in HAIR > Sniffer.

**Compatibility:** `event_mode: standalone` remains the default for users of the
older `sunfounder_ir` companion. Do not enable both custom IR receiver
integrations for the same physical device. The built-in IR receiver is currently
validated on **Pironman 5 Max** only. HAOS's GPIO overlay is still a host-level
prerequisite; the add-on cannot automatically guarantee this step.

**Independent HAOS validation (23 November 2026):**
[@eugenioparise](https://github.com/eugenioparise) reported successful use
of the `pironman5` event mode with the Pironman 5 HACS integration and HAIR.
The previous `sunfounder_ir` integration was disabled, and **reloading the
Pironman 5 integration** was necessary before HAIR worked. Only the Pironman
5 integration's receiver appeared in HAIR. The tester also reported successful
HAIR send functionality; **this GPIO receiver remains receive-only** and
transmission requires separate compatible hardware.

This is one successful independent installation; compatibility on other
HAOS versions and hardware revisions remains to be tested.

## Legacy standalone installation

**Existing users only:** This alternate route uses a separately installed `sunfounder_ir` custom component. For a fresh installation, prefer the [HACS-linked mode](#recommended-use-the-existing-pironman-5-hacs-integration-no-manual-copying). Version 0.2.0 retains backwards compatibility with this mode.

### Installation

1. Open the Home Assistant Add-on Store.
2. Add this repository:

   `https://github.com/ChristophKomenda/home-assistant-addon`

3. Refresh the repository.
4. Install **Pironman IR Receiver v0.2.0 or newer**.
5. Configure the add-on:

   ```yaml
   receiver_id: pironman5-max
   event_mode: standalone
   debug: true
   ```

6. Start the add-on and check its logs.
7. Copy the companion integration from
   `pironman-ir-receiver/ha_custom_component/sunfounder_ir/`
   into `/config/custom_components/sunfounder_ir/`.
8. Restart Home Assistant and configure the integration
   with the same `receiver_id`.
9. Open **HAIR > Sniffer** and select
   **SunFounder IR Receiver**.

If upgrading from an earlier experimental version,
refresh the repository and verify the installed version.
Back up the add-on options before reinstalling if necessary.

### Validation summary

The full infrared signal path has now been successfully
tested on both Home Assistant Container and Home Assistant OS.

- **Debian / Home Assistant Container:** Successful live
  IR capture using real Pironman 5 Max hardware.
- **Home Assistant OS 18.5 / Core 2026.11.2:**
  Successful independent community test.
- **HAIR:** Infrared codes were successfully captured.
- **Real-world verification:** Captured IR codes were
  successfully used to control a television.

Further testing across additional hardware variants and
Home Assistant OS versions is welcome.

---

## Installation checklist for this community repository

For the **recommended `pironman5` mode**, use the [guided steps above](#recommended-use-the-existing-pironman-5-hacs-integration-no-manual-copying) or the [short main README](../Readme.MD#quick-start-recommended-setup).

- Add the repository `https://github.com/ChristophKomenda/home-assistant-addon` to the HAOS Add-on Store.
- Confirm the receiver is exposed as `/dev/lirc0` **before** starting the add-on.
- Select `event_mode: pironman5`, and match `receiver_id` to the HACS Pironman 5 **IR bridge device ID**.
- Start the add-on, **reload the Pironman 5 integration**, then select its receiver in **HAIR → Sniffer**.

**Only for `event_mode: standalone`:** The older manual `sunfounder_ir` copy is still required. See [legacy standalone installation](#legacy-standalone-installation). Do not install it for the recommended mode.

## Security / behavior

- Uses `homeassistant_api: true` and the app-injected `SUPERVISOR_TOKEN`;
  users do not need to create a long-lived Home Assistant token.
- No cloud, public port, MQTT or privileged container access.
- Device access is restricted to `/dev/lirc0` instead of `full_access`.
- Signal carrier frequency is unknown on basic GPIO receivers; modulation
  is `None`. RC-5 toggle remains encoded in raw timings; no application-level
  press/release state is synthesized.
- Loss of connectivity to Home Assistant may drop frames; the bridge does not
  provide guaranteed buffering or retransmission.
- When the receiver device is absent, Supervisor may refuse to start the app
  due to the explicit device mapping; this is expected.
- Linux `/dev/lircN` enumeration can differ between systems; this first
  version intentionally supports `/dev/lirc0` only.

## Independent Home Assistant OS Validation

**Status: Successful community end-to-end test**

**Date:** 21 November 2026

**Tester:** [@eugenioparise](https://github.com/eugenioparise)

### Environment

- SunFounder Pironman 5 Max
- Home Assistant OS 18.5
- Home Assistant Core 2026.11.2
- Built-in infrared receiver exposed via `/dev/lirc0`
- Pironman IR Receiver development add-on
- Companion `sunfounder_ir` custom integration
- HAIR integration

### Test procedure

The community tester independently:

1. Added the development repository to Home Assistant.
2. Installed the standalone Pironman IR Receiver add-on.
3. Updated the `sunfounder_ir` companion integration.
4. Configured matching receiver IDs.
5. Disabled the IR option in the existing Pironman integration.
6. Disconnected the external ESP32 infrared receiver.
7. Captured infrared codes using HAIR Sniffer.
8. Successfully tested recorded codes on a television.

### Result

**The standalone infrared receiver implementation successfully
worked on the reported Home Assistant OS installation.**

This confirms the complete signal path:

**IR remote → GPIO13 → LIRC → standalone add-on →
Supervisor API → Home Assistant → native IR entity → HAIR**

The captured IR codes could also be used in a real-world
television control test.

This is an independently reported successful community test,
not a guarantee of compatibility with every HAOS version
or Pironman hardware revision.

Special thanks to @eugenioparise for suggesting this feature
and helping validate it on real Home Assistant OS hardware.

[Read the community discussion](https://github.com/ChristophKomenda/pironman5-homeassistant-container/discussions/16).

---

## Development tests

```bash
python3 -m unittest discover -s pironman-ir-receiver/tests -v
```

### Live end-to-end validation on Home Assistant Container (21 November 2026)

**Confirmed successful on real hardware:** Raspberry Pi 5 / Pironman 5 Max,
Debian host, and Home Assistant Container. A real IR remote was received through
GPIO13 and `/dev/lirc0`, processed by the standalone SunFounder Docker bridge,
forwarded to Home Assistant, handled by the native `InfraredReceiverEntity`,
and **displayed in the HAIR Sniffer**.

The Home Assistant custom integration was independently verified using a valid
REST API event: the receiver ID matched, 18 sample timings passed validation,
and `_handle_received_signal()` returned without error. Earlier manual events
contained empty data (`{}`), which explained their rejection; this was not
a confirmed defect in the integration.

The Debian-based Home Assistant Container tests were performed
locally. A separate community test has since successfully
validated the complete infrared-to-HAIR path on Home Assistant OS.

## Known limitations

Home Assistant Container and Home Assistant OS have both been
successfully tested using real Pironman 5 Max hardware.

The Home Assistant OS test was independently performed by a
community member. Additional OS versions, hardware revisions,
and long-term reliability remain to be validated.

SunFounder declined upstream maintenance in PR #26 and proposed a
community listing in PR #27. This add-on remains experimental and
independently maintained in this repository.


## Diagnostics: optional debug logging

Set `debug: true` in the **Pironman IR Receiver** app options and restart the
app. The logs will include `Captured IR frame (N timings)` when the hardware
produces a complete frame and `IR event delivered (HTTP 200, ...)` when the
Supervisor event endpoint accepts it. Avoid posting unredacted logs containing
private details or access tokens. Normal operation defaults to `debug: false`.

If HAIR detects the receiver entity but does not display signals:

1. Check that the **Pironman IR Receiver** app is running (not just the custom
   integration). The custom integration alone cannot read `/dev/lirc0`.
2. With `debug: true`, press an IR remote button. If no captured frames are
   logged, check the GPIO13 overlay, `/dev/lirc0` mapping and whether another
   process is consuming the LIRC stream.
3. If captured frames appear but no delivery messages follow, check for
   Supervisor HTTP errors and confirm `homeassistant_api: true`.
4. In **Developer Tools → Events**, listen for the event matching your mode:
   `pironman5_ir_raw_received` in **`pironman5` mode**, or
   `sunfounder_ir_received` in **`standalone` mode**. Verify the event's
   `device_id` (Pironman mode) or `receiver_id` (standalone mode) matches the
   corresponding integration configuration.
5. If events arrive, select the correct receiver in **HAIR → Sniffer**:
   **Pironman 5** in `pironman5` mode, **SunFounder IR Receiver** in
   standalone mode. After switching modes, reload the Pironman 5 integration.

The Dockerfile uses `with-contenv` when launching Python because Home Assistant
base images run s6-overlay and environment variables injected into the app
(including `SUPERVISOR_TOKEN`) need to be restored for that process.

### Independent local smoke test (not a substitute for HAOS hardware testing)

Build with the configured `BUILD_FROM` argument and use a mock Supervisor HTTP
endpoint to validate event requests. Successful HTTP 200 responses from a mock
server prove request delivery only; they do **not** prove Supervisor
permissions or native HAIR decoding on actual Home Assistant OS.

## Project status and links

- [SunFounder PR #26 — upstream submission declined](https://github.com/sunfounder/home-assistant-addon/pull/26)
- [SunFounder PR #27 — community listing proposal](https://github.com/sunfounder/home-assistant-addon/pull/27)
- [Development repository](https://github.com/ChristophKomenda/home-assistant-addon)
- [Community testing discussion](https://github.com/ChristophKomenda/pironman5-homeassistant-container/discussions/16)
- [HAIR](https://github.com/Anirudh-G/HAIR)

**Status:** Successfully tested on Home Assistant Container
and independently validated on Home Assistant OS.
SunFounder is not maintaining this add-on; see community listing PR #27.

## License and attribution

Original contributions by Christoph Komenda in this add-on are available under
the [MIT License](LICENSE), to the extent of his rights. Reuse is permitted,
including by SunFounder, provided the applicable copyright and license notices
are retained. See [copyright and license scope](COPYRIGHT.md) for exclusions,
third-party rights, and the distinction from the upstream SunFounder fork.
