# -*- coding: utf-8 -*-

__doc__ = 'Interface to select which wrapper to run'

from PyQt4.QtGui import QApplication, QTableWidget, QTableWidgetItem, QHeaderView, QFont, QPushButton, QShortcut, QKeySequence
import wrappers



class WrapperTable(QTableWidget):
    """Display details about the available wrappers from their meta data and select one to execute
    """
    def __init__(self):
        super(WrapperTable, self).__init__()
        QShortcut(QKeySequence.Close, self, self.close)
        QShortcut(QKeySequence.Quit, self, self.close)
        self.wrapper = None

        header = 'Website', 'HTTP method', 'Response format', 'Category', 'Notes', 'Run'
        self.setFont(QFont('Times New Roman', 16))
        self.setColumnCount(len(header))
        self.setHorizontalHeaderLabels(header)
        self.setVerticalHeaderLabels([])
        for wrapper_name in dir(wrappers):
            if not wrapper_name.startswith('_'):
                wrapper = getattr(wrappers, wrapper_name)()
                num_rows = self.rowCount()
                self.insertRow(num_rows)
                self.setItem(num_rows, 0, QTableWidgetItem(wrapper_name.replace('_', ' ').title()))
                for i, attr in enumerate(['http_method', 'response_format', 'category', 'notes']):
                    try:
                        value = getattr(wrapper, attr)
                    except AttributeError:
                        pass
                    else:
                        self.setItem(num_rows, i + 1, QTableWidgetItem(value))
                # add button to activate wrapper
                button = QPushButton('Go')
                button.clicked.connect(self.select_wrapper(wrapper))
                self.setCellWidget(num_rows, len(header) - 1, button)
                self.setVerticalHeaderItem(num_rows, QTableWidgetItem(''))
        self.horizontalHeader().setResizeMode(QHeaderView.ResizeToContents)
        self.showMaximized()
        self.raise_()

    def select_wrapper(self, wrapper):
        def _select_wrapper():
            self.wrapper = wrapper
            self.close()
        return _select_wrapper
