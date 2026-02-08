from __future__ import annotations

import importlib
import pkgutil

import napcat


def test_import_all_napcat_submodules() -> None:
    failed_modules: list[str] = []

    for module_info in pkgutil.walk_packages(napcat.__path__, napcat.__name__ + "."):
        try:
            importlib.import_module(module_info.name)
        except Exception as exc:  # pragma: no cover
            failed_modules.append(f"{module_info.name}: {exc}")

    assert not failed_modules, "Some modules failed to import:\n" + "\n".join(failed_modules)
