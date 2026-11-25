#!/usr/bin/env python3
"""Independent MODE2 LIRC to Home Assistant event bridge for HAOS.

Home Assistant Core is reached through the Supervisor proxy with the app's
SUPERVISOR_TOKEN. No third-party Pironman bridge or HACS integration required.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
import queue
import select
import signal
import stat
import struct
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

EVENT = "sunfounder_ir_received"
API_URL = "http://supervisor/core/api/events/" + EVENT
EVENT_NAMES = {"standalone": "sunfounder_ir_received", "pironman5": "pironman5_ir_raw_received"}
WORD = struct.Struct("=I")
TYPE_MASK = 0xFF000000
LENGTH_MASK = 0x00FFFFFF
SPACE = 0x00000000
PULSE = 0x01000000
TIMEOUT = 0x03000000
OVERFLOW = 0x04000000
LOG = logging.getLogger("sunfounder_ir")
STOP = threading.Event()


class FrameAssembler:
    """Group alternating IR pulses and spaces into complete raw frames."""

    def __init__(self, gap_us: int = 12000) -> None:
        self.gap_us = gap_us
        self.parts: list[int] = []

    def finish(self) -> list[int] | None:
        parts, self.parts = self.parts, []
        if 8 <= len(parts) <= 512 and parts[0] > 0 and any(p < 0 for p in parts):
            return parts
        return None

    def feed(self, word: int) -> list[int] | None:
        kind = word & TYPE_MASK
        length = word & LENGTH_MASK
        if kind == OVERFLOW:
            self.parts = []
            return None
        if kind == TIMEOUT:
            return self.finish()
        if kind not in (SPACE, PULSE) or length == 0:
            return None
        if kind == SPACE and length >= self.gap_us:
            return self.finish()
        duration = length if kind == PULSE else -length
        if not self.parts and duration < 0:
            return None
        if self.parts and (self.parts[-1] > 0) == (duration > 0):
            self.parts[-1] += duration
        else:
            self.parts.append(duration)
        if len(self.parts) > 512:
            self.parts = []
        return None


def send_frames(token: str, pending: queue.Queue) -> None:
    while not STOP.is_set() or not pending.empty():
        try:
            payload = pending.get(timeout=0.25)
        except queue.Empty:
            continue
        try:
            req = Request(
                API_URL,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=4) as response:
                response.read()
                LOG.debug("IR event delivered (HTTP %s, receiver %s, %d timings)",
                          response.status, payload.get("receiver_id"),
                          len(payload.get("timings", [])))
        except (HTTPError, URLError, OSError, TimeoutError) as exc:
            LOG.warning("Unable to deliver IR frame: %s", exc)
        finally:
            pending.task_done()


def make_event_payload(receiver_id: str, timings: list[int], event_mode: str) -> dict:
    """Build the payload expected by the chosen Home Assistant integration."""
    if event_mode not in EVENT_NAMES:
        raise ValueError(f"Unsupported event mode: {event_mode}")
    id_key = "device_id" if event_mode == "pironman5" else "receiver_id"
    return {id_key: receiver_id, "timings": timings, "modulation": None}


def event_url(event_mode: str) -> str:
    """Resolve the Supervisor Core event endpoint for an IR receiver mode."""
    return "http://supervisor/core/api/events/" + EVENT_NAMES[event_mode]


def listen(device: str, receiver_id: str, pending: queue.Queue, event_mode: str = "standalone") -> None:
    assembler = FrameAssembler()
    fd = os.open(device, os.O_RDONLY | os.O_NONBLOCK)
    buffer = b""
    LOG.info("Listening for IR frames on %s", device)
    try:
        while not STOP.is_set():
            readable, _, _ = select.select([fd], [], [], 0.5)
            if not readable:
                continue
            try:
                chunk = os.read(fd, 4096)
            except BlockingIOError:
                continue
            if not chunk:
                raise OSError("LIRC receiver disconnected")
            buffer += chunk
            while len(buffer) >= WORD.size:
                value = WORD.unpack_from(buffer)[0]
                buffer = buffer[WORD.size:]
                timings = assembler.feed(value)
                if timings:
                    LOG.debug("Captured IR frame (%d timings)", len(timings))
                    payload = make_event_payload(receiver_id, timings, event_mode)
                    try:
                        pending.put_nowait(payload)
                    except queue.Full:
                        LOG.warning("IR send queue full; dropped frame")
    finally:
        os.close(fd)


def main() -> int:
    global API_URL
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    options_path = Path("/data/options.json")
    options = json.loads(options_path.read_text(encoding="utf-8"))
    receiver_id = str(options.get("receiver_id", "")).strip()
    debug = options.get("debug", False)
    event_mode = options.get("event_mode", "standalone")
    if event_mode not in EVENT_NAMES:
        raise SystemExit("event_mode must be standalone or pironman5")
    API_URL = event_url(event_mode)
    if type(debug) is not bool:
        raise SystemExit("debug option must be a boolean")
    if debug:
        LOG.setLevel(logging.DEBUG)
    LOG.info("IR receiver: %s (event_mode=%s, debug=%s)", receiver_id, event_mode, debug)
    if not receiver_id or len(receiver_id) > 64 or any(ch.isspace() for ch in receiver_id):
        raise SystemExit("Configure a receiver_id containing 1-64 non-space characters")
    token = os.environ.get("SUPERVISOR_TOKEN", "")
    if not token:
        raise SystemExit("Missing SUPERVISOR_TOKEN: homeassistant_api must be enabled")
    path = "/dev/lirc0"
    if not Path(path).exists() or not stat.S_ISCHR(os.stat(path).st_mode):
        raise SystemExit("/dev/lirc0 is unavailable. Enable gpio-ir on GPIO13 and reboot HAOS")
    signal.signal(signal.SIGTERM, lambda *_: STOP.set())
    signal.signal(signal.SIGINT, lambda *_: STOP.set())
    pending: queue.Queue = queue.Queue(maxsize=100)
    threading.Thread(target=send_frames, args=(token, pending), daemon=True).start()
    while not STOP.is_set():
        try:
            listen(path, receiver_id, pending, event_mode)
        except OSError as exc:
            if not STOP.is_set():
                LOG.warning("LIRC receiver unavailable: %s", exc)
        STOP.wait(3)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
