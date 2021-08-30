import os
import platform
import sys
from pathlib import Path

import pytest
import waqd.base.logger
import waqd.base.system
from PyQt5 import QtCore, QtWidgets
from waqd import config

# enable scaling
QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling)


class PathSetup():
    def __init__(self):
        self.test_path = Path(os.path.dirname(__file__))
        self.base_path = self.test_path.parent
        self.testdata_path = self.test_path / "testdata"


def load_mocks():
    paths = PathSetup()
    mockup_path = paths.test_path / "mock"
    sys.path = [str(mockup_path)] + sys.path
    os.environ["PYTHONPATH"] = str(paths.test_path / "mock")


@pytest.fixture
def target_mockup_fixture():
    load_mocks()

@pytest.fixture
def base_fixture(request):
    # yield "base_fixture"  # return after setup
    paths = PathSetup()
    config.assets_path = paths.base_path / "src" / "waqd" /"assets"

    def teardown():
        # reset singletons
        waqd.base.logger.Logger._instance = None
        waqd.base.system.RuntimeSystem._instance = None
        os.environ["PYTHONPATH"] = ""
    request.addfinalizer(teardown)

    return paths


def mock_run_on_non_target(mocker):
    class Detector():
        class board():
            any_raspberry_pi = False
            id = "NOT_THE_TARGET"
        class chip:
            id = "arch"
    mocker.patch('adafruit_platformdetect.Detector', Detector)

def mock_run_on_target(mocker):
    load_mocks()
    from target_pkgs.adafruit_platformdetect import Detector
    mocker.patch('adafruit_platformdetect.Detector', Detector)
    # need to patch RPi.GPIO - only installs on Linux
    if platform.system() == "Linux":
        mock_rpi_gpio = mocker.Mock()
        from target_pkgs.RPi import GPIO
        mocker.patch("RPi.GPIO", GPIO)
    mock_plaftorm = mocker.Mock()
    mock_plaftorm.return_value = 'Linux'
    mocker.patch('platform.system', mock_plaftorm)
