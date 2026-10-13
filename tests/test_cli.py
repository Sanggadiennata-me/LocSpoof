import pytest
from typer.testing import CliRunner

from locspoof.cli.main import app
from locspoof.core.models import Coordinates
from locspoof.providers.android.adb_client import AndroidDevice

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "locspoof version" in result.stdout


def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Location Spoofer" in result.stdout


def test_cli_devices():
    result = runner.invoke(app, ["devices"])
    assert result.exit_code == 0
    assert "ATTACHED ANDROID DEVICES" in result.stdout


def test_cli_status():
    result = runner.invoke(app, ["status"])
    assert result.exit_code == 0
    assert "ANDROID LOCATION STATUS" in result.stdout


def test_cli_status_json():
    result = runner.invoke(app, ["status", "--json"])
    assert result.exit_code == 0
    assert '"mock_provider_status"' in result.stdout


def test_cli_stop():
    result = runner.invoke(app, ["stop"])
    assert result.exit_code == 0
    assert "Location Spoofing Stopped" in result.stdout


def test_cli_reset():
    result = runner.invoke(app, ["reset"])
    assert result.exit_code == 0
    assert "Cleanup & Reset Completed" in result.stdout


def test_cli_spoof_with_mocked_emulator(mocker):
    # Mock AdbClient so it simulates a connected emulator
    mocker.patch(
        "locspoof.providers.android.adb_client.AdbClient.is_available",
        return_value=True,
    )
    mocker.patch(
        "locspoof.providers.android.adb_client.AdbClient.list_devices",
        return_value=[
            AndroidDevice(
                serial="emulator-5554",
                state="device",
                is_emulator=True,
                model="Pixel_8",
                android_version="15",
                sdk_version=35,
                mock_location_status="available",
            )
        ],
    )
    mocker.patch(
        "locspoof.providers.android.adb_client.AdbClient.set_emulator_geo_fix",
        return_value=None,
    )
    mocker.patch(
        "locspoof.providers.android.adb_client.AdbClient.get_reported_location",
        return_value=Coordinates(latitude=55.554250, longitude=55.765611),
    )

    # 1. Test spoofing with DMS coordinate
    result = runner.invoke(app, ["start", "55°33'15.3\"N", "55°45'56.2\"E"])
    assert result.exit_code == 0
    assert "Location Spoofing Active" in result.stdout
    assert "55.554250, 55.765611" in result.stdout
    assert "emulator-5554" in result.stdout
    assert "ACTIVE" in result.stdout

    # 2. Test status command after spoofing
    stat_result = runner.invoke(app, ["status"])
    assert stat_result.exit_code == 0
    assert "55.554250, 55.765611" in stat_result.stdout
    assert "ACTIVE" in stat_result.stdout
    assert "VERIFIED" in stat_result.stdout
