#!/bin/bash
set -uo pipefail
sudo mpremote mkdir :/sd/apps/salz
set -e
sudo mpremote cp src/flow3r.toml :/sd/apps/salz/flow3r.toml
sudo mpremote cp src/__init__.py :/sd/apps/salz/__init__.py
sudo mpremote cp src/constants.py :/sd/apps/salz/constants.py
