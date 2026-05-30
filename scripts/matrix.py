#!/usr/bin/env python3
import json
import sys
import yaml

RUNNER_MAP = {
    "linux/amd64": "ubuntu-24.04",
    "linux/arm64": "ubuntu-24.04-arm",
}

def main():
    with open("config.yaml") as f:
        cfg = yaml.safe_load(f)

    target_repo  = cfg["target_repo"]
    runtime_base = f"{cfg['runtime']['image']}:{cfg['runtime']['tag']}"
    push_enabled = str(cfg.get("push_enabled", False)).lower()

    builds = []
    manifests_map = {}

    for build in cfg["builds"]:
        os_name     = build["os"]
        os_upstream = f"{cfg['upstream']['image']}:{cfg['upstream']['tag']}-{os_name}"
        os_runtime  = f"{runtime_base}-{os_name}"
        for go_version in cfg["go_versions"]:
            for arch in build["archs"]:
                runner = RUNNER_MAP.get(arch)
                if runner is None:
                    print(f"ERROR: no runner mapping for arch '{arch}'", file=sys.stderr)
                    sys.exit(1)
                arch_short = arch.split("/")[1]
                builds.append({
                    "index":        len(builds),
                    "os":           os_name,
                    "arch":         arch,
                    "arch_short":   arch_short,
                    "go_version":   go_version,
                    "runner":       runner,
                    "upstream_ref": os_upstream,
                    "runtime_ref":  os_runtime,
                    "target_repo":  target_repo,
                    "push_enabled": push_enabled,
                })
                key = (go_version, os_name)
                if key not in manifests_map:
                    manifests_map[key] = {
                        "go_version":   go_version,
                        "os":           os_name,
                        "target_repo":  target_repo,
                        "push_enabled": push_enabled,
                        "arch_shorts":  [],
                    }
                manifests_map[key]["arch_shorts"].append(arch_short)

    manifests = list(manifests_map.values())

    mode = sys.argv[1] if len(sys.argv) > 1 else "builds"
    if mode == "manifests":
        print(json.dumps(manifests))
    else:
        print(json.dumps(builds))

if __name__ == "__main__":
    main()
