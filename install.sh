#!/bin/bash

INSTALL_DIR="/usr/local/bin"

chmod +x main.py

ln -s "$(pwd)/main.py" "$INSTALL_DIR/pybonsai"