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
# The ASF licenses this file to You under the Apache License, Version 2.0.
#
"""Discover public qumat submodules and sync docs/sphinx/source/*.rst and toctree.

Run before sphinx-build so new modules get an API page and index.rst stays in sync.
"""

from __future__ import annotations

import sys
import types
from pathlib import Path


def discover_api_modules() -> list[str]:
    """Return sorted list of module names to document: qumat + qumat.* from __all__ only."""
    repo_root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(repo_root))
    try:
        import qumat
    except ImportError as e:
        print(f"Warning: could not import qumat: {e}", file=sys.stderr)
        return ["qumat", "qumat.qdp"]

    modules = ["qumat"]
    for name in getattr(qumat, "__all__", []):
        obj = getattr(qumat, name, None)
        if isinstance(obj, types.ModuleType):
            modules.append(f"qumat.{name}")
    return sorted(set(modules))


def ensure_rst(module: str, source_dir: Path) -> None:
    """Create or leave unchanged the .rst file for this module."""
    rst_name = module + ".rst"  # qumat.qdp -> qumat.qdp.rst
    rst_path = source_dir / rst_name
    if rst_path.exists():
        return
    title = module.split(".")[-1].replace("_", " ").title()
    if "." in module:
        title = module
    content = f"""{title}
{"=" * len(title)}

.. automodule:: {module}
   :members:
   :undoc-members:
   :show-inheritance:
"""
    rst_path.write_text(content, encoding="utf-8")
    print(f"Created {rst_path.name}")


def write_index_rst(modules: list[str], source_dir: Path) -> None:
    """Write index.rst with toctree listing all modules."""
    toctree_lines = ["   " + m for m in modules]
    content = f""".. qumat Python API

qumat Python API
================

.. toctree::
   :maxdepth: 2

{chr(10).join(toctree_lines)}
"""
    (source_dir / "index.rst").write_text(content, encoding="utf-8")


def main() -> int:
    repo_root = Path(__file__).resolve().parent.parent
    source_dir = repo_root / "docs" / "sphinx" / "source"
    source_dir.mkdir(parents=True, exist_ok=True)

    modules = discover_api_modules()
    for mod in modules:
        ensure_rst(mod, source_dir)
    write_index_rst(modules, source_dir)
    # List for optional use by website/sidebars or CI (api/python/<module> doc ids)
    list_path = source_dir / "api_module_list.txt"
    list_path.write_text(
        "\n".join(["api/python/" + m for m in modules]), encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
