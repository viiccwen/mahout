#!/usr/bin/env bash
#
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

# Generate Rust API documentation as Markdown using rustdoc-md.
# Packages to document are read from scripts/rust_api_packages.txt (one per line).
# Output: docs/api/rust/<package>.md and docs/api/rust/crates.txt for sidebars.

set -euo pipefail

# Add ~/.cargo/bin and rustup toolchain to PATH if not already there
[[ -d "$HOME/.cargo/bin" ]] && export PATH="$HOME/.cargo/bin:$PATH"
if ! command -v cargo &>/dev/null; then
  RUSTUP_CARGO="$(find "$HOME/.rustup/toolchains" -path '*/bin/cargo' -print -quit 2>/dev/null || true)"
  if [[ -n "$RUSTUP_CARGO" ]]; then
    export PATH="$(dirname "$RUSTUP_CARGO"):$PATH"
  else
    echo "Error: cargo not found. Please install Rust: https://rustup.rs" >&2
    exit 1
  fi
fi

# Ensure rustdoc-md is available (auto-install if missing)
if ! command -v rustdoc-md &>/dev/null; then
  echo "rustdoc-md not found. Installing (cargo install rustdoc-md)..."
  cargo install rustdoc-md
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QDP_DIR="$(dirname "$SCRIPT_DIR")"
REPO_ROOT="$(dirname "$QDP_DIR")"
OUTPUT_DIR="$REPO_ROOT/docs/api/rust"
PACKAGES_FILE="$SCRIPT_DIR/rust_api_packages.txt"

# Read package list: non-empty, non-comment lines; fallback to qdp-core
PACKAGES=()
if [[ -f "$PACKAGES_FILE" ]]; then
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="${line%%#*}"
    line="${line#"${line%%[![:space:]]*}"}"
    line="${line%"${line##*[![:space:]]}"}"
    [[ -n "$line" ]] && PACKAGES+=( "$line" )
  done < "$PACKAGES_FILE"
fi
[[ ${#PACKAGES[@]} -eq 0 ]] && PACKAGES=( "qdp-core" )

echo "Generating Rust API documentation for packages: ${PACKAGES[*]}"
mkdir -p "$OUTPUT_DIR"

# Change to QDP workspace directory
cd "$QDP_DIR"

# Ensure nightly toolchain is available (auto-install if missing)
NIGHTLY_CARGO="$(find "$HOME/.rustup/toolchains/nightly"* -path '*/bin/cargo' -print -quit 2>/dev/null || true)"
if [[ -z "$NIGHTLY_CARGO" ]]; then
  echo "Nightly toolchain not found. Installing (rustup install nightly)..."
  rustup install nightly
  NIGHTLY_CARGO="$(find "$HOME/.rustup/toolchains/nightly"* -path '*/bin/cargo' -print -quit 2>/dev/null || true)"
fi
if [[ -z "$NIGHTLY_CARGO" ]]; then
  echo "Error: nightly toolchain still not found after install attempt." >&2
  exit 1
fi

NIGHTLY_BIN="$(dirname "$NIGHTLY_CARGO")"
echo "Using nightly toolchain at: $NIGHTLY_BIN"

GENERATED_CRATES=()
for pkg in "${PACKAGES[@]}"; do
  # Cargo uses underscores in doc output (qdp-core -> qdp_core.json)
  crate_json="${pkg//-/_}"
  JSON_FILE="$QDP_DIR/target/doc/${crate_json}.json"
  OUTPUT_FILE="$OUTPUT_DIR/${pkg}.md"

  echo "Documenting package: $pkg"
  PATH="$NIGHTLY_BIN:$PATH" RUSTDOCFLAGS="-Z unstable-options --output-format json -Awarnings" \
    cargo doc --no-deps --package "$pkg"

  if [[ ! -f "$JSON_FILE" ]]; then
    echo "Error: expected $JSON_FILE not found after cargo doc" >&2
    exit 1
  fi

  TMP_MD="$(mktemp)"
  rustdoc-md --path "$JSON_FILE" --output "$TMP_MD"

  {
    echo '---'
    echo "title: $pkg"
    echo "sidebar_label: $pkg"
    echo '---'
    echo ''
    cat "$TMP_MD"
  } > "$OUTPUT_FILE"
  rm -f "$TMP_MD"

  sed -E 's/\[([^]]+)\]\([^)]*::[^)]+\)/\1/g' "$OUTPUT_FILE" > "${OUTPUT_FILE}.tmp" && mv "${OUTPUT_FILE}.tmp" "$OUTPUT_FILE"

  echo "  -> $OUTPUT_FILE"
  GENERATED_CRATES+=( "$pkg" )
done

# Write crates list for website sidebars generator
printf '%s\n' "${GENERATED_CRATES[@]}" > "$OUTPUT_DIR/crates.txt"
echo "Wrote $OUTPUT_DIR/crates.txt (${#GENERATED_CRATES[@]} crate(s))"
echo "Rust API documentation generated successfully."
