"""Check current HA imports without the legacy suite's module mocks."""
from importlib.metadata import version
from pathlib import Path
import subprocess
import sys

from awesomeversion import AwesomeVersion
import pytest


@pytest.mark.skipif(
    AwesomeVersion(version("homeassistant")) < AwesomeVersion("2026.11.0"),
    reason="Unmocked runtime import audit targets HA 2026.11 and newer",
)
def test_all_runtime_modules_import_without_mocks():
    """Import every integration module in a fresh interpreter with real HA."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from importlib import import_module; "
            "from pathlib import Path; "
            "from homeassistant.const import UnitOfTemperature; "
            "package = 'custom_components.proflame_connect_wifi'; "
            "modules = [import_module(package + '.' + path.stem) "
            "for path in sorted(Path(package.replace('.', '/')).glob('*.py'))]; "
            "assert import_module(package + '.client').UnitOfTemperature "
            "is UnitOfTemperature; "
            "assert import_module(package + '.climate').UnitOfTemperature "
            "is UnitOfTemperature",
        ],
        cwd=Path(__file__).resolve().parents[1],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
