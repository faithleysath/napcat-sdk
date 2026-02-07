# tests/smoke_test.py
import importlib
import pkgutil
import sys

import napcat


def smoke_test_all_modules():
    print(f"📦 Inspecting package: {napcat.__name__} (path: {napcat.__path__})")

    # 递归查找所有子模块
    found_errors = False
    for module_info in pkgutil.walk_packages(napcat.__path__, napcat.__name__ + "."):
        try:
            print(f"  Checking {module_info.name} ... ", end="")
            importlib.import_module(module_info.name)
            print("✅ OK")
        except Exception as e:
            print(f"❌ FAILED: {e}")
            found_errors = True

    if found_errors:
        print("💥 Smoke test failed with import errors!")
        sys.exit(1)
    else:
        print("✨ All modules imported successfully!")

if __name__ == "__main__":
    smoke_test_all_modules()
