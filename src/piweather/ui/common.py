""" Contains helper methods usually to display some text or image with formatting."""

import locale
import logging
import platform
import time
import xml.dom.minidom as dom
from pathlib import Path

from PyQt5 import QtCore, QtGui, QtSvg, QtWidgets

import piweather.config as config
from piweather.config import FONT_NAME, PROG_NAME
from piweather.resources import get_rsc_file
from piweather.settings import LANG, LANG_ENGLISH, LANG_GERMAN, LANG_HUNGARIAN

logger = logging.getLogger(PROG_NAME)

# define Qt so it can be used like the namespace in C++
Qt = QtCore.Qt


def set_ui_language(qt_app: "QtWidgets.QApplication", settings: "Settings"):
    """ Set the ui language. Retranslate must be called afterwards."""
    qt_app.removeTranslator(config.translator)
    if settings.get(LANG) == LANG_GERMAN:  # default case, ui is written in german
        return

    if not config.translator:
        config.translator = QtCore.QTranslator(qt_app)

    tr_file = Path("NULL")
    if settings.get(LANG) == LANG_ENGLISH:
        tr_file = config.base_path / "piweather/ui/qt/english.qm"
    if settings.get(LANG) == LANG_HUNGARIAN:
        tr_file = config.base_path / "piweather/ui/qt/hungarian.qm"
    if not tr_file.exists():
        logger.error("Cannot find %s translation file.", str(english_tr_file))

    config.translator.load(str(tr_file))
    qt_app.installTranslator(config.translator)


def draw_svg(pyqt_obj: QtWidgets.QWidget, svg_path: Path, color="white", shadow=True, scale=1):
    """
    Sets an svg in the desired color for a QtWidget.
    param color: the disired color as a string in html compatible name
    param shadow: draws a drop shadow
    param scale: multiplicator for scaling the image
    """

    # read svg as xml and get the drawing
    with open(svg_path) as svg:
        svg_content = "".join(svg.readlines())
        svg_content = svg_content.replace("\t", "")
    svg_dom = dom.parseString("".join(svg_content))
    svg_drawing = svg_dom.getElementsByTagName("path")

    # set color in the dom element
    svg_drawing[0].setAttribute("fill", color)

    # create temporary svg and read into pyqt svg graphics object
    svg_graphics: QtSvg.QGraphicsSvgItem = None
    with open(svg_path.parent / Path(svg_path.stem + "_white" + svg_path.suffix), "w+") as new_svg:
        new_svg.write(svg_dom.toxml())
        new_svg.close()
        svg_graphics = QtSvg.QGraphicsSvgItem(new_svg.name)  # new_svg.name

    # the gui needs a picture/painter to render the svg into
    pic = QtGui.QPicture()
    painter = QtGui.QPainter(pic)
    painter.scale(scale, scale)
    # now render and set picture
    svg_graphics.renderer().render(painter)
    pyqt_obj.setPicture(pic)

    # apply shadow, if needed
    if shadow:
        shadow = QtWidgets.QGraphicsDropShadowEffect()
        shadow.setBlurRadius(5)
        shadow.setXOffset(3)
        shadow.setYOffset(3)
        pyqt_obj.setGraphicsEffect(shadow)

    painter.end()


def scale_gui_elements(qt_root_obj: QtWidgets.QMainWindow, font_scaling: float,
                       previous_scaling: float = 1, extra_scaling=1):
    """
    Applies font resize for all QLabel, QPushButton and QTabWidget children of the qt_root_obj.
    param font_scaling: new multiplicator
    param previous_scaling: old multiplicator
    param extra_scaling: for platform specific font size
    """
    # scale all fonts by font_scaling setting
    for qt_list in (
            qt_root_obj.findChildren(QtWidgets.QLabel),
            qt_root_obj.findChildren(QtWidgets.QPushButton),
            qt_root_obj.findChildren(QtWidgets.QTabWidget)):
        for qt_obj in qt_list:
            font = qt_obj.font()
            font.setFamily(FONT_NAME)
            font.setPointSize(int(qt_obj.fontInfo().pointSize() * font_scaling * extra_scaling /
                                  previous_scaling))
            qt_obj.setFont(font)


def get_temperature_icon(temp_value: float) -> Path:
    """
    Return the path of the image resource for the appropriate temperature input.
    t < 0: empty
    t < 10: low
    t < 22: half
    t < 30 high
    t > 30: full
    """
    rsc_folder = "gui_base"
    # set dummy as default
    icon_path = get_rsc_file(rsc_folder, "dummy")

    # return dummy for invalid value
    if not temp_value:
        return icon_path

    # set up ranges for the 5 icons
    if temp_value <= 0:
        icon_path = get_rsc_file(rsc_folder, "thermometer_empty")
    elif temp_value < 10:
        icon_path = get_rsc_file(
            rsc_folder, "thermometer_almost_empty")
    elif temp_value < 22:
        icon_path = get_rsc_file(rsc_folder, "thermometer_half")
    elif temp_value < 30:
        icon_path = get_rsc_file(
            rsc_folder, "thermometer_almost_full")
    else:
        icon_path = get_rsc_file(rsc_folder, "thermometer_full")
    return icon_path

#### Formatting ####


def format_int_meas_text(html_text: str, value: int, color="white"):
    """
    Returns a given html string by switching out the value with the given number.
    param html_text: the html text containing the value. Can only contain one value.
    param value: the value to be set
    """
    # converting of values to formatted display data
    if value is None:
        temp_val = format_text(html_text, "N/A", "string", color=color)
    else:
        temp_val = format_text(html_text, value, "int", color=color)
    return temp_val


def format_float_temp_text(html_text: str, value: float, color="white"):
    """
    Returns a given html string by switching out the value with the given number.
    param html_text: the html text containing the value. Can only contain one value.
    param value: the value to be set
    """
    # converting of values to formatted display data
    if value is None:
        temp_val = format_text(html_text, "N/A", "string", color=color)
    else:
        temp_val = format_text(html_text, value, "float", color=color)
    return temp_val


def format_temp_text_minmax(html_text, min_val, max_val, color="white"):
    """
    Returns a given html string by switching out the min and max value with the given number.
    param html_text: the html text containing the value. Can only contain two values: min and then max.
    param min_val, max_val: the min and max value to be set
    """
    # converting of values to formatted display data
    if min_val is None or max_val is None:
        html_text = format_text(html_text, "N/A", "string", tag_id=0, color=color)
    else:
        min_val = round(min_val)
        max_val = round(max_val)
        html_text = format_text(html_text, min_val, "int", tag_id=0, color=color)
        html_text = format_text(html_text, max_val, "int", tag_id=3, color=color)
    return html_text


def format_text(html_text: str, value,
                disp_type: str, tag_id=0, color="white") -> str:
    """
    Generic hmtl text formatting method.
    param html_text: the html text containing the value.
    param value: the the value to be set
    param disp_type: format for the html for "float", "int" or "string"
    param tag_id: tag containing the value
    param color: apply this html color
    """
    if value is None:
        value = 0.0
    if not html_text:
        return ""
    html_dom = dom.parseString(html_text)
    # set color
    tags = html_dom.getElementsByTagName("span")
    if tags:
        tags[0].setAttribute("style", "color:" + color)

    # type scpecific handling
    if disp_type == "float":
        value = "{:0.1f}".format(value)
        value = value.split(".")
        tags = html_dom.getElementsByTagName("span")
        if len(tags) >= 2:
            tags[tag_id].firstChild.data = str(value[tag_id] + ".")
            tags[tag_id+1].firstChild.data = str(int(value[tag_id+1]))
            return html_dom.toxml()

    if disp_type == "int":
        value = str(int(value))
        if tags:
            tags[tag_id].firstChild.data = value
            return html_dom.toxml()

    if disp_type == "string":
        if tags:
            for tag in tags:
                if tag.firstChild:
                    tag.firstChild.data = ""
            tags[tag_id].firstChild.data = value
            return html_dom.toxml()
    return None


def get_localized_date(date_time: "datetime.datetime", settings: "settings.Settings") -> str:
    """
    Returns a formatted date of a day conforming to the actual locale.
    Contains weekday name, month and day.
    """
    # switch locale to selected language - needs reboot on linux
    if settings.get(LANG) != LANG_ENGLISH:
        locale_name = ""
        try:
            if platform.system() == "Windows":
                if settings.get(LANG) == LANG_GERMAN:
                    locale_name = "de_DE"
                elif settings.get(LANG) == LANG_HUNGARIAN:
                    locale_name = "hu-HU"
            elif platform.system() == "Linux":
                if settings.get(LANG) == LANG_GERMAN:
                    locale_name = "de_DE.UTF8"
                elif settings.get(LANG) == LANG_HUNGARIAN:
                    locale_name = "hu_HU.UTF8"
            locale.setlocale(locale.LC_ALL, locale_name)
        except Exception as error:
            logger.error(f"Cannot set language to {settings.get(LANG)}: {str(error)}")
            # TODO "sudo apt-get install language-pack-id" is needed...
            # or sudo locale-gen
    else:
        locale.setlocale(locale.LC_ALL, 'C')

    local_date = time.strftime("%a, %x", date_time.timetuple())
    # remove year - twice once with following . and once for none
    local_date = local_date.replace(str(date_time.year) + ".", "")
    local_date = local_date.replace(str(date_time.year), "")
    return local_date
