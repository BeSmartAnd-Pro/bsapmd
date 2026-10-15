SHELL := /bin/bash

# Zmieniaj w razie potrzeby (3.13 mieści się w twoim constraint <3.14)
PY_VER ?= 3.13

.PHONY: help
help:
	@echo "Targets:"
	@echo "  make build-macos        - build na macOS (lokalnie, z binarką)"
	@echo "  make build-linux-amd64  - build w Dockerze (linux/amd64)"
	@echo "  make build-linux-i386   - build w Dockerze (linux/i386)"
	@echo "  make build-all          - wszystkie trzy"
	@echo "  make clean              - czyści artefakty (dist/, build/, spec, .venv)"

# ---------- macOS (lokalnie) ----------
.PHONY: build-macos
build-macos:
	@set -e
	# 1) Jeśli plugin nie jest dostępny, doinstaluj go do 'poetry self' (bez ruszania Pythona)
	if ! poetry self show plugins | grep -q "poetry-pyinstaller-plugin"; then \
		poetry self add poetry-pyinstaller-plugin; \
	fi
	# 2) Zależności (dev też, bo masz pyinstaller w [tool.poetry.group.dev.dependencies])
	poetry install --with dev --no-root
	# 3) Build (plugin dorzuci binarkę do dist/)
	poetry build
	@echo "✅ macOS: artefakty w dist/ (wheel, sdist i binarka)"

# ---------- Linux x86_64 ----------
.PHONY: build-linux-amd64
build-linux-amd64:
	@set -euo pipefail; \
	IMAGE="python:$(PY_VER)-slim-bookworm"; \
	docker run --rm -t --platform linux/amd64 -v "$$(pwd)":/src -w /src $$IMAGE /bin/bash -lc '\
	  set -euo pipefail; \
	  apt-get update && apt-get install -y --no-install-recommends gcc g++ make patchelf file git && rm -rf /var/lib/apt/lists/*; \
	  python -m pip install -U pip setuptools wheel; \
	  pip install "poetry==1.8.3"; \
	  poetry self add poetry-pyinstaller-plugin >/dev/null 2>&1 || true; \
	  poetry install --with dev --no-root; \
	  poetry build; \
	  echo "✅ Linux amd64: artefakty w dist/ (w kontenerze -> zbind-mountowane w hostowym dist/)" \
	'

# ---------- Linux i386 ----------
.PHONY: build-linux-i386
build-linux-i386:
	@docker run --rm -t \
	  --platform linux/386 \
	  -v "$(PWD)":/src \
	  -w /src \
	  i386/python:3.11-slim-bullseye /bin/bash -lc 'set -euo pipefail; \
	    apt-get update && apt-get install -y --no-install-recommends gcc g++ make patchelf file && rm -rf /var/lib/apt/lists/*; \
	    python -m pip install -U pip setuptools wheel; \
	    pip install "requests==2.32.3" "PyYAML==6.0.2" "pyinstaller==6.16.0"; \
	    pyinstaller --onefile --clean -n bsapmd-linux-i386 bsapmd/main.py'
	@echo "✅ Linux i386: dist/$(APP_NAME)-linux-i386"

# ---------- All ----------
.PHONY: build-all
build-all: build-macos build-linux-amd64 build-linux-i386
	@echo "🏁 gotowe: sprawdź katalog dist/"

# ---------- Clean ----------
.PHONY: clean
clean:
	@rm -rf dist build .venv *.spec
	@echo "🧹 wyczyszczone"