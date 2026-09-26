#!/bin/sh
# Wrap app.html (the Claude artifact source) into a standalone index.html for GitHub Pages.
cd "$(dirname "$0")/.."
{ printf '<!doctype html>\n<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head><body>\n'; cat app.html; printf '\n</body></html>\n'; } > index.html
