#
# Copyright (c) 2019-2021 Péter Gosztolya & Contributors.
#
# This file is part of WAQD
# (see https://github.com/goszpeti/WeatherAirQualityDevice).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
import os
import shutil
import tarfile
import urllib.request
from distutils.version import StrictVersion as Version
from pathlib import Path
from time import sleep

from github import Github, Repository

import waqd.config as config
from waqd import __version__ as WAQD_VERSION
from waqd.base.components import ComponentRegistry, CyclicComponent
from waqd.settings import (AUTO_UPDATER_ENABLED, UPDATER_KEY,
                           UPDATER_USER_BETA_CHANNEL)


class OnlineUpdater(CyclicComponent):
    """
    Auto updater class, which checks for new releases on GitHub with an access token
    If a newer version is detected, it downloads it and calls "script/installer/start_installer.sh"
    This entry point should not be changed!
    """
    UPDATE_TIME = 600  # 10 minutes in seconds
    INIT_WAIT_TIME = 10  # don't start updating until the station is ready
    STOP_TIMEOUT = 2  # override because of long update time

    def __init__(self, components: ComponentRegistry, settings):
        super().__init__(components, settings)

        self._base_path = config.base_path  # save for multiprocessing
        self._repository: Repository.Repository

        if not self._settings.get(AUTO_UPDATER_ENABLED):
            self._disabled = True
            return

        self._new_version_path = Path.home() / ".waqd" / "updater"

        # delete downloaded version to clean up
        if self._new_version_path.exists():
            try:
                shutil.rmtree(self._new_version_path)
            except PermissionError:
                os.system(f"sudo rm -rf {str(self._new_version_path)}")

        self._start_update_loop(self._updater_sequence, self._updater_sequence)

    def _updater_sequence(self):
        """ Check, that runs continously and start the installation if a new version is available. """
        try:
            self._connect_to_repository(self._settings.get(UPDATER_KEY))
        except:
            self._logger.error("Updater: Cannot to updater Server.")
            return

        latest_tag = self._get_latest_version_tag()
        if not latest_tag:
            return
        update_available = self._check_should_update(latest_tag)
        if update_available:
            self._logger.info("Updater: Found newer version %s", latest_tag)
            self._comps.tts.say_internal("new_version", [latest_tag])
            self._install_update(latest_tag)

    def _connect_to_repository(self, updater_key):
        """ Get Github repo object """
        github = Github(updater_key)
        self._repository = github.get_user().get_repo(config.GITHUB_REPO_NAME)

    def _get_latest_version_tag(self) -> str:
        """ Check, if an update is found and return it's version. """
        releases = self._repository.get_releases()
        if releases.totalCount == 0:
            self._logger.info("Updater: No releases found.")
            return ""

        latest_release = releases[0]
        if not latest_release.tag_name:  # latest release is not tagged - probably an alpha version
            if releases.totalCount > 1:
                latest_release = releases[1]  # next release - there should not be 2 untagged releases
        return latest_release.tag_name

    def _check_should_update(self, latest_release_version: str):
        if len(latest_release_version.split("v")) > 1:  # remove v for comparing
            latest_release_version = latest_release_version.split("v")[1]
        self._logger.debug(f"Updater: Latest version is {latest_release_version}")

        latest_version = Version(latest_release_version)
        current_version = Version(WAQD_VERSION)

        # only check, that the main version is not lower
        if latest_version <= current_version:
            # alpha and beta release handling
            if latest_version.prerelease:
                # alpha - only with debug mode on - switch is possible from b3 to a4
                if latest_version.prerelease[0] == "a" and config.DEBUG_LEVEL > 0 and self._settings.get(UPDATER_USER_BETA_CHANNEL):
                    if latest_version.prerelease[1] > current_version.prerelease[1]:
                        return True
            else:
                if latest_version.version <= current_version.version:
                    self._logger.debug("Updater: No new update found.")
                    return False

            self._logger.debug("Updater: No new update found.")
            return False

        if latest_version.prerelease:
            if not self._settings.get(UPDATER_USER_BETA_CHANNEL):
                self._logger.info("Updater: Skip newer pre-release %s", latest_version)
                return False
        return True

    def _install_update(self, tag_name):
        """
        Start the installer at the defined entry point:
        script/installer/start_installer.sh
        """
        # TODO do a popup later with deferring option?

        # download as tar because direct support
        self._logger.info("Updater: Downloading new release")
        [update_file, _] = urllib.request.urlretrieve(
            self._repository.get_archive_link("tarball", tag_name))
        tar = tarfile.open(update_file)
        os.makedirs(self._new_version_path, exist_ok=True)
        tar.extractall(path=self._new_version_path)

        # the repo will be in a randomly named dir, so we must scan for it
        update_dir = [f.path for f in os.scandir(self._new_version_path) if f.is_dir()]
        if len(update_dir) != 1:
            self._logger.error("Updater: Multiple update repos found")
            return
        update_dir = Path(update_dir[0])

        # Wait for previous peach to finish berfore this app intance is killed
        self._comps.tts.wait_for_tts()

        # start updater script - location hardcoded
        if self._runtime_system.is_target_system:
            self._logger.info("Updater: Starting update.")
            installer_script = update_dir / "script" / "installer" / "start_installer.sh"
            if installer_script.exists():
                try:
                    # shutdown other components gracefully
                    config.comp_ctrl.unload_all(updating=True)
                    while not config.comp_ctrl.all_unloaded:
                        sleep(1)
                    self._logger.info("Updater: Starting updater")
                    os.system("chmod +x " + str(installer_script))
                    # this kills this program
                    os.system(str(installer_script))
                except RuntimeError as error:
                    self._logger.error(
                        "Updater: Error while executing updater: \n%s", str(error))