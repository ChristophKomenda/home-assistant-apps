#!/usr/bin/env python3
"""Build only; never run or publish an app image."""
import platform
import subprocess
import sys
from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
COVERAGE = {"infrastructure-ha-monitor": {"amd64", "aarch64"},
            "bitcoin-node-monitor": {"amd64", "aarch64"},
            "powerline2mqtt": {"amd64", "aarch64"},
            "pironman-ir-receiver": {"aarch64"}}

def main():
    app, arch = sys.argv[1:]
    for slug, expected in COVERAGE.items():
        cfg = yaml.safe_load((ROOT / slug / "config.yaml").read_text())
        if set(cfg["arch"]) != expected:
            raise SystemExit(f"Architecture coverage changed for {slug}; review CI matrix")
        if cfg.get("image"):
            raise SystemExit(f"{slug} references a published image; review distribution policy")
    if arch not in COVERAGE.get(app, set()):
        raise SystemExit("Unsupported app/architecture")
    native = {"x86_64": "amd64", "aarch64": "aarch64", "arm64": "aarch64"}.get(platform.machine())
    if native != arch:
        raise SystemExit(f"Expected native {arch}, got {native}")
    folder = ROOT / app
    args = ["docker", "build", "--tag", f"local/{app}:ci-{arch}"]
    if (folder / "build.yaml").exists():
        cfg = yaml.safe_load((folder / "build.yaml").read_text())
        if set(cfg) != {"build_from"}:
            raise SystemExit("Additional build.yaml fields need review")
        args += ["--build-arg", f"BUILD_FROM={cfg['build_from'][arch]}"]
    subprocess.run(args + [str(folder)], check=True)

if __name__ == "__main__":
    main()
