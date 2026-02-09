#!/usr/bin/env python3
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
# Licensed to the Apache Software Foundation (ASF) under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
#
# Post-process Sphinx-generated API Markdown: wrap function/method and class
# signatures in fenced code blocks so they are easier to read in Docusaurus.
#
# Sphinx's HTML builder styles signatures natively; sphinx-markdown-builder does not
# expose an option to emit signatures as code blocks. Hence this post-process step.
# Run after sphinx-build -b markdown (e.g. from make docs-python).
#
from __future__ import annotations

import re
import sys
from pathlib import Path


def wrap_method_signature(line: str) -> tuple[str, str] | None:
    """If line is '#### method_name(...)' or '#### `method_name(...)`', return (heading, code_block)."""
    line = line.rstrip()
    # Match: #### name(...) or #### `name(...)`
    m = re.match(r"^####\s+`?(\w+)\(([^)]*)\)`?\s*$", line)
    if not m:
        return None
    name, args = m.group(1), m.group(2)
    signature = f"{name}({args})"
    heading = f"#### {name}"
    code_block = f"```python\n{signature}\n```"
    return (heading, code_block)


def wrap_class_signature(line: str) -> tuple[str, str] | None:
    """If line is '### *class* module.ClassName(...)', return (heading, code_block)."""
    line = line.rstrip()
    # Match: ### *class* full.name(args) or ### *exception* ...
    m = re.match(r"^###\s+\*(class|exception)\*\s+(.+)\s*$", line)
    if not m:
        return None
    kind, full_sig = m.group(1), m.group(2).strip()
    # Short name: last component before parenthesis (e.g. module.ClassName -> ClassName)
    short = full_sig.split("(")[0].strip().split(".")[-1]
    if kind == "class":
        paren_part = full_sig[full_sig.find("(") :] if "(" in full_sig else ""
        code_sig = f"class {short}{paren_part}:"
    else:
        code_sig = full_sig
    code_block = f"```python\n{code_sig}\n```"
    heading = f"### {full_sig}"
    return (heading, code_block)


def process_file(path: Path) -> bool:
    """Rewrite file with signatures wrapped in code blocks. Returns True if changed."""
    content = path.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    changed = False
    while i < len(lines):
        line = lines[i]
        # Try method signature (#### name(args))
        wrapped = wrap_method_signature(line)
        if wrapped:
            heading, code_block = wrapped
            out.append(heading + "\n")
            out.append("\n")
            out.append(code_block + "\n")
            out.append("\n")
            changed = True
            i += 1
            continue
        # Try class/exception signature (### *class* ...)
        wrapped = wrap_class_signature(line)
        if wrapped:
            heading, code_block = wrapped
            out.append(heading + "\n")
            out.append("\n")
            out.append(code_block + "\n")
            out.append("\n")
            changed = True
            i += 1
            continue
        out.append(line)
        i += 1
    if changed:
        path.write_text("".join(out), encoding="utf-8")
    return changed


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    api_dir = repo_root / "docs" / "api" / "python"
    if not api_dir.is_dir():
        return 0
    count = 0
    for path in sorted(api_dir.glob("*.md")):
        if process_file(path):
            count += 1
            print(f"Wrapped signatures: {path.name}")
    if count:
        print(f"Updated {count} file(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
