#!/bin/bash
set -euo pipefail
mpremote mkdir :/flash/sys/apps/salzamt-badge
mpremote cp src/flow3r.toml :/flash/sys/apps/salzamt-badge/flow3r.toml
mpremote cp src/__init__.py :/flash/sys/apps/salzamt-badge/__init__.py
