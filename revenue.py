from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel, QDateEdit, QHBoxLayout, \
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt
import sqlite3

class StatisticsTab(QWidget ):
    def __init__(self, start_label, end_label):
        super().__init__()
        self.start_label = start_label
        self.end_label = end_label
        self.setStyleSheet("background-color: grey; border: 3px solid black; border-radius: 5px; color: black; "
                           "font-size: 18px; font-weight: bold;")
        self.layout = QVBoxLayout(self)

        # Create a scroll area widget
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_widget = QWidget()
        self.scroll_widget.setStyleSheet("background-color: white;")
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        self.scroll_widget.setLayout(self.scroll_layout)
        self.scroll_area.setWidget(self.scroll_widget)

        # Add the scroll area to the analysis tab layout
        self.layout.addWidget(self.scroll_area)

        # Create a refresh button
        self.refresh_button = QPushButton("Refresh Statistics")
        self.layout.addWidget(self.refresh_button)
        headers = ["Item ID", "Item Name", "Item Price", "Item Cost", "Total Sales", "Total Cost", "Gross", "Revenue"]
        self.table = self.create_table(headers)
        self.scroll_layout.addWidget(self.table)

        # Connect the clicked signal of the refresh button to the refresh_statistics slot
        self.refresh_button.clicked.connect(self.refresh_statistics)
        self.refresh_statistics()

    def refresh_statistics(self):
        start = self.start_label.date().toString("yyyy-MM-dd")
        end = self.end_label.date().toString("yyyy-MM-dd")
        conn, cursor = self.connect()

        cursor.execute(f"""
        SELECT
        i.Item_id,
        i.Item_name,
        i.Item_price,
        (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
        FROM item_ingredients AS ii
        LEFT JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
        WHERE ii.Item_id = i.Item_id) AS Item_cost_per_unit,
        o.Total_sales,
        (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
        FROM item_ingredients AS ii
        LEFT JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
        WHERE ii.Item_id = i.Item_id) * o.Total_sales AS Total_cost,
        i.Item_price * o.Total_sales AS Gross,
        i.Item_price * o.Total_sales - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                        FROM item_ingredients AS ii
                                        LEFT JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                        WHERE ii.Item_id = i.Item_id) * o.Total_sales AS Revenue
    FROM
        items AS i
    LEFT JOIN (
        SELECT product_id, SUM(quantity) AS Total_sales
        FROM orders
        WHERE order_date >= '{start}' AND order_date <= '{end}'
        GROUP BY product_id
    ) AS o ON i.Item_id = o.product_id
    GROUP BY
        i.Item_id,
        i.Item_name,
        i.Item_price;
        """)
        data = cursor.fetchall()

        if data:
            
            self.table.setRowCount(len(data))
            
            self.table.verticalScrollBar().setStyleSheet("QScrollBar { width: 30px; }")
            self.table.horizontalHeader().setStretchLastSection(True)
            self.table.horizontalHeader().setFont(QFont("Arial", 12, QFont.Bold))
            self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.table.setStyleSheet("background-color: transparent;")

            for row, row_data in enumerate(data):
                for col, value in enumerate(row_data):
                    item = QTableWidgetItem(str(value))
                    item.setTextAlignment(Qt.AlignCenter)
                    item.setBackground(QColor(173, 216, 230))
                    if col == 7:  # Revenue column index is 7
                        if value:
                            revenue = float(value)
                            if revenue < 0:
                                item.setForeground(QColor("red"))
                            elif revenue > 0:
                                item.setForeground(QColor("green"))
                    self.table.setItem(row, col, item)

            self.table.resizeRowsToContents()
            # self.table.resizeColumnsToContents()
            
        else:
            QMessageBox.warning(self, "Warning", "No data available.")


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

    def connect(self):
        conn = sqlite3.connect("restaurant_database.db")
        cursor = conn.cursor()
        return conn, cursor
