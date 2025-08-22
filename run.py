#!/usr/bin/env python3

import sys
import os

# Add the project root to the python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from proofcheck.src.cli import cli

if __name__ == '__main__':
    cli()