import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QPushButton, QTabWidget,QWidget, QVBoxLayout, QLabel, QMessageBox, QScrollArea, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy
from PyQt5.QtGui import QFont, QColor, QPainter
from PyQt5.QtCore import Qt, QSizeF
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog

class Components(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: grey; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        self.layout = QVBoxLayout(self)

        # Create a scroll area widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: white;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        self.layout.addWidget(self.scroll_area)
        self.print_button = QPushButton("Print Page")
        self.print_button.clicked.connect(self.print_current_tab)
        self.layout.addWidget(self.print_button)
        self.create_item_tabs()


    def connect(self):
        try:
            conn = sqlite3.connect("restaurant_database.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as error:
            QMessageBox.warning(self, "Warning", str(error))

    @staticmethod
    def create_table(headers):
        table = QTableWidget()
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        table.verticalScrollBar().setStyleSheet("QScrollBar { width: 30px; }")
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setFont(QFont("Arial", 12, QFont.Bold))
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.setStyleSheet("background-color: transparent;")
        return table


    def load_data(self, table, item_id):
        conn, cursor = self.connect()
        if conn and cursor:
            try:
                cursor.execute("SELECT ing.Ingred_name, item.Ingred_amount "
                            "FROM item_ingredients AS item "
                            "JOIN ingredients AS ing ON item.Ingred_id = ing.Ingredients_id "
                            "WHERE item.Item_id = ?",
                            (item_id,))
                components = cursor.fetchall()

                # Set the number of rows in the table widget
                table.setRowCount(len(components))

                for i, component in enumerate(components):
                    ingredient_name = component[0]
                    quantity = component[1]

                    ingredient_item = QTableWidgetItem(ingredient_name)
                    quantity_item = QTableWidgetItem(str(quantity))
                    ingredient_item.setBackground(QColor(173, 216, 230))
                    quantity_item.setBackground(QColor(173, 216, 230))

                    table.setItem(i, 0, ingredient_item)
                    table.setItem(i, 1, quantity_item)
                # Resize the table to show all rows
                table.resizeRowsToContents()

                header = table.horizontalHeader()
                header.setSectionResizeMode(QHeaderView.ResizeToContents)
                # Calculate the required height based on the row heights
                total_height = sum(table.rowHeight(row) * 3 for row in range(table.rowCount())) 
                
                # Set the fixed height of the table to show all rows
                table.setFixedHeight(total_height)

            except sqlite3.Error as error:
                QMessageBox.warning(self, "Warning", str(error))

            conn.close()


    def refresh(self):
        conn, cursor = self.connect()
        if conn and cursor:
            try:
                cursor.execute("SELECT Item_id, Item_name FROM items")
                items = cursor.fetchall()

                existing_tables = []

                # Iterate over items
                for item in items:
                    item_id = item[0]
                    item_name = item[1]

                    # Check if table already exists
                    table_widget = self.findChild(QTableWidget, f"table_{item_id}")
                    if table_widget:
                        # Table already exists, update its data
                        table_id = int(table_widget.objectName().split('_')[1])
                        self.load_data(table_widget, table_id)
                        existing_tables.append(table_id)
                    else:
                        # Table does not exist, create a new table and load data
                        item_label = QLabel(f"Item: {item_name}")
                        self.scroll_layout.addWidget(item_label)

                        table_widget = self.create_table(['Ingredient', 'Quantity'])
                        table_widget.setObjectName(f"table_{item_id}")  # Set object name for table widget
                        self.load_data(table_widget, item_id)
                        existing_tables.append(item_id)

                        self.scroll_layout.addWidget(table_widget)

                # Remove tables that no longer exist
                child_widgets = self.scroll_widget.findChildren(QTableWidget)
                for child_widget in child_widgets:
                    table_name = child_widget.objectName()
                    table_id = int(table_name.split('_')[1])
                    if table_id not in existing_tables:
                        child_widget.setParent(None)

            except sqlite3.Error as error:
                QMessageBox.warning(self, "Warning", str(error))

            conn.close()
        else:
            QMessagebox.warning(self,"Connection problem","Database connection failed")

    def print_current_tab(self):
        current_tab_widget = self.scroll_area.widget()

        printer = QPrinter(QPrinter.HighResolution)
        printer.setOrientation(QPrinter.Portrait)
        printer.setFullPage(True)  # Set to True to print the entire page
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            painter = QPainter(printer)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calculate the scaling factor to zoom the tab
            scale = min(printer.pageRect().width() / current_tab_widget.width(),
                        printer.pageRect().height() / current_tab_widget.height())
            
            # Calculate the offset to center the tab on the page
            x_offset = (printer.pageRect().width() - (current_tab_widget.width() * scale)) / 2
            y_offset = (printer.pageRect().height() - (current_tab_widget.height() * scale)) / 2
            
            # Apply the scale and offset transformations
            painter.translate(x_offset, y_offset)
            painter.scale(scale, scale)
            
            current_tab_widget.render(painter)
            painter.end()




    def create_item_tabs(self):
        conn, cursor = self.connect()
        if conn and cursor:
            try:
                cursor.execute("SELECT DISTINCT Item_category FROM items")
                categories = cursor.fetchall()

                tab_widget = QTabWidget()

                for category in categories:
                    category_name = category[0]
                    category_tab = QWidget()
                    category_layout = QVBoxLayout(category_tab)

                    cursor.execute("SELECT Item_id, Item_name FROM items WHERE Item_category=?", (category_name,))
                    items = cursor.fetchall()

                    for item in items:
                        item_id = item[0]
                        item_name = item[1]

                        item_label = QLabel(f"Item: {item_name}")
                        item_label.setFixedHeight(100)
                        category_layout.addWidget(item_label)

                        table_widget = self.create_table(['Ingredient', 'Quantity'])
                        table_widget.setObjectName(f"table_{item_id}")

                        self.load_data(table_widget, item_id)

                        category_layout.addWidget(table_widget)

                    tab_widget.addTab(category_tab, category_name)
                    # Adjust the height of category_layout
                    category_tab.adjustSize()

                self.scroll_layout.addWidget(tab_widget)

            except sqlite3.Error as error:
                QMessageBox.warning(self, "Warning", str(error))

            conn.close()


