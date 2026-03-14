"""
ragul/config.py — Loader for ragul.config (TOML format).

All keys are optional. Documented defaults apply when absent.
"""

from __future__ import annotations
import tomllib
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class RagulConfig:
    # [projekt]
    name:        str  = "ragul-project"
    version:     str  = "0.1.0"
    entry:       str  = "main.ragul"

    # [fordito]
    target:      str  = "interpret"     # "interpret" | "bytecode"
    python_min:  str  = "3.11"

    # [modulok]
    search_paths: list[str] = field(default_factory=list)

    # [ellenorzes]
    harmony:     str  = "warn"          # "warn" | "strict" | "off"
    tipus:       str  = "warn"          # "warn" | "strict" | "off"

    # [hibak]
    error_lang:  str  = "en"

    # Runtime — set after loading
    project_dir: Path = field(default_factory=Path)

    @classmethod
    def load(cls, path: Path | str | None = None) -> "RagulConfig":
        """Load config from ragul.config (TOML).  Falls back to all defaults."""
        cfg = cls()

        if path is None:
            # Search upward from cwd
            p = Path.cwd()
            for candidate in [p / "ragul.config", *[p.parent / "ragul.config" for p in p.parents]]:
                if candidate.exists():
                    path = candidate
                    break

        if path is None:
            return cfg

        path = Path(path)
        cfg.project_dir = path.parent

        with open(path, "rb") as f:
            data = tomllib.load(f)

        # [projekt]
        proj = data.get("projekt", {})
        cfg.name    = proj.get("nev",     cfg.name)
        cfg.version = proj.get("verzio",  cfg.version)
        cfg.entry   = proj.get("belepes", cfg.entry)

        # [fordito]
        ford = data.get("fordito", {})
        cfg.target     = ford.get("cel",    cfg.target)
        cfg.python_min = ford.get("python", cfg.python_min)

        # [modulok]
        mod = data.get("modulok", {})
        cfg.search_paths = mod.get("utvonalak", cfg.search_paths)

        # [ellenorzes]
        check = data.get("ellenorzes", {})
        cfg.harmony = check.get("harmonia", cfg.harmony)
        cfg.tipus   = check.get("tipus",    cfg.tipus)

        # [hibak]
        hibak = data.get("hibak", {})
        cfg.error_lang = hibak.get("nyelv", cfg.error_lang)

        return cfg

    def resolve_module_path(self, module_name: str) -> Path | None:
        """Try to locate module_name.ragul in search paths + stdlib placeholder."""
        candidates: list[Path] = []

        # Search paths from config
        for sp in self.search_paths:
            p = self.project_dir / sp / f"{module_name}.ragul"
            candidates.append(p)

        # Same directory as project root
        candidates.insert(0, self.project_dir / f"{module_name}.ragul")

        for c in candidates:
            if c.exists():
                return c

        return None
