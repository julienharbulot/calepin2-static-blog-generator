#!/bin/bash
set -euo pipefail

isort --profile black calepin
black calepin
mypy calepin

