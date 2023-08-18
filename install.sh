#!/bin/bash
set -uo pipefail
mpremote mkdir :/flash/sys/apps/salzamt-badge
set -e
mpremote cp src/flow3r.toml :/flash/sys/apps/salzamt-badge/flow3r.toml
mpremote cp src/__init__.py :/flash/sys/apps/salzamt-badge/__init__.py
