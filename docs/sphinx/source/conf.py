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
# Sphinx config for qumat Python API. Output: Markdown (sphinx-markdown-builder)
# for Docusaurus to render.
#
import os
import sys

repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
sys.path.insert(0, repo_root)

project = "qumat"
copyright = "The Apache Software Foundation"
author = "Apache Mahout"
release = "0.6.0"
version = "0.6"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.napoleon",
    "sphinx_autodoc_typehints",
    "sphinx_markdown_builder",
]
autosummary_generate = True
napoleon_use_param = True
napoleon_google_docstring = True

autodoc_mock_imports = [
    "_qdp",
    "qiskit",
    "qiskit_aer",
    "cirq",
    "amazon",
    "braket",
    "sympy",
]

templates_path = ["_templates"]
exclude_patterns: list[str] = []
source_suffix = ".rst"
master_doc = "index"
