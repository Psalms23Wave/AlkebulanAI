# Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC
# SPDX-License-Identifier: Apache-2.0
"""ABLT: a grammar-first tokenizer for Luganda and other Bantu languages."""

from .segmenter import cut, show_cuts, split_word
from .tokenizer import ABLT

__version__ = "2.0.0"
__author__ = "Mathew Sekanjako"
__copyright__ = "Copyright 2025-2026 Mathew Sekanjako and Psalms23Wave LLC"
__license__ = "Apache-2.0"
__url__ = "https://www.sekanjakomathew.com"
__all__ = ["ABLT", "cut", "show_cuts", "split_word"]
