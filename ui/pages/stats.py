from PyQt5.QtCore import Qt

from ..template import GenericPage


class StatsPage(GenericPage):
    def __init__(self):
        super().__init__(title="Stats", icon_path="resources/stats.svg")