# -*- coding: utf-8 -*-

__doc__ = 'Interface to select which wrapper to run'

import importlib
from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QFont, QPushButton, QShortcut, QKeySequence
import wrappers


def get_wrappers():
    """Return the names of available wrappers
    """
    return wrappers.__all__

def load_wrapper(name):
    """Load the wrapper with this name
    """
    return importlib.import_module('wrappers.{}'.format(name)).Wrapper()



class WrapperTable(QTableWidget):
    """Display details about the available wrappers from their meta data and select one to execute
    """
    def __init__(self):
        super(WrapperTable, self).__init__()
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        self.wrapper_name = None

        header = 'Website', 'HTTP method', 'Response format', 'Category', 'Notes', 'Run'
        font = QFont('Times New Roman', 16)
        self.setFont(font)
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        font.setBold(True)
        self.horizontalHeader().setFont(font)
        self.setVerticalHeaderLabels([])

        for wrapper_name in get_wrappers():
            wrapper = load_wrapper(wrapper_name)
            try:
                if not wrapper.enabled:
                    continue # ignore this disabled wrapper
            except AttributeError:
                pass

            num_rows = self.rowCount()
            self.insertRow(num_rows)
            self.setItem(num_rows, 0, QTableWidgetItem(wrapper_name.replace('_', ' ').title()))
            for i, attr in enumerate(['http_method', 'response_format', 'category', 'notes']):
                try:
                    value = getattr(wrapper, attr)
                except AttributeError:
                    pass
                else:
                    if attr == 'notes':
                        # add line breaks
                        value = value.replace('.', '.\n')
                    self.setItem(num_rows, i + 1, QTableWidgetItem(value))
            # add button to activate wrapper
            button = QPushButton('Go')
            button.clicked.connect(self.select_wrapper(wrapper_name))
            self.setCellWidget(num_rows, len(header) - 1, button)
            self.setVerticalHeaderItem(num_rows, QTableWidgetItem(''))
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.showMaximized()
        self.setSortingEnabled(True)
        self.sortItems(0)
        self.raise_()

    def select_wrapper(self, wrapper_name):
        def _select_wrapper():
            self.wrapper_name = wrapper_name
            self.close()
        return _select_wrapper
