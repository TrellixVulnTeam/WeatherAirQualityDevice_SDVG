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
import abc

from typing import Callable
from threading import Thread
from PyQt5 import QtCore

from waqd.base.logger import Logger
from waqd.base.components import ComponentRegistry


class WorkerObject(QtCore.QObject):

    def __init__(self, target: Callable, parent = None):
        super(self.__class__, self).__init__(parent)
        self.target = target
        
    def run(self):
        self.target()

class SubUi(metaclass=abc.ABCMeta):
    """
    Common class for all ui modules, which have a different update time.
    """
    UPDATE_TIME = 1000  # microseconds

    def __init__(self, main_ui: QtCore.QObject, settings):
        self._main_ui = main_ui
        self._ui = main_ui.ui
        self._comps: ComponentRegistry = main_ui._comps
        self._logger = Logger()
        self._settings = settings

        # set up update thread
        self._update_timer = QtCore.QTimer(main_ui)
        self._update_timer.timeout.connect(self._cyclic_update)
        self._update_timer.start(self.UPDATE_TIME)

    def init_with_cyclic_update(self):
        self._first_thread = QtCore.QThread()
        self.worker = WorkerObject(target=self._cyclic_update)
        self.worker.moveToThread(self._first_thread)
        self._first_thread.started.connect(self.worker.run)
        self._first_thread.finished.connect(self._first_thread.deleteLater)
        self._first_thread.start()
  
    @abc.abstractmethod
    def _cyclic_update(self):
        """ implement ui update callback here """
        raise NotImplementedError('Users must define _cyclic_update to use this base class')

    def stop(self):
        """ Stop the update loop. """
        self._update_timer.stop()
