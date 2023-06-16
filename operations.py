# PyQt5.QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QDialog, QListWidget, QTabWidget, QTreeView, QListView, QTableView, QGraphicsView, QAction, QMenuBar, QToolBar, QStatusBar, QFileDialog, QInputDialog, QDateEdit, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QMenu, QFormLayout, QCompleter, QDialogButtonBox

# PyQt5.QtGui
from PyQt5.QtGui import QIcon, QPixmap, QFont, QColor, QPalette, QPainter, QBrush, QPen, QCursor, QImage, QKeySequence, QValidator, QStandardItemModel, QStandardItem, QTextCursor, QRegExpValidator

# PyQt5.QtCore
from PyQt5.QtCore import Qt, QEvent, QPoint, QRect, pyqtSlot, QRegularExpression, QDateTime, QTime, QDate, QTimeZone, QItemSelection, QRegExp

import sqlite3
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np
import io
import os
import sys
from analysis import AnalysisTabWidget
from bills import BillsTabWidgt
from orders import OrderDialog
from components import Components
from revenue import StatisticsTab

class OperationWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
        
        

        # Set the context menu policy to custom so we can show our right-click menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showRightClickMenu)

    def initUI(self):
        self.setWindowTitle("Operation Window")
        self.setWindowIcon(QIcon("Images/icon.png"))
        self.set_background_image("Images/food.png")
        self.create_title_label()
        self.create_date_widgets()
        self.create_menu_bar()
        self.create_actions()
       


        tab_widget = QTabWidget(self)
        tab_widget.setGeometry(QRect(50, 100, 1300, 600))

        items_headers = ["Item ID", "Item Name", "Item_category", "Unit_price"]
        self.items_table = self.create_tab(tab_widget, "Items", headers=items_headers)

        sales_headers = ["Customer Name", "Item Name", "Item Category", "Quantity", "Item Price", "Total items Prices", "Note"]
        self.sales_table = self.create_tab(tab_widget, "Sales", headers=sales_headers)

        inventory_headers = ["Ingrident Name", "Ingrident Average price per unit", "Total Ingrdient count", "Total price"]
        self.inventory_table = self.create_tab(tab_widget, "Updated Inventory", headers=inventory_headers)

        purchase_headers = ["Ingrident Name", "Ingrident price per unit", "Ingrdient count", "Total price", "Purchase Date"]
        self.purchase_table = self.create_tab(tab_widget, "Purchases", headers=purchase_headers)

        total_income_headers = ["Total purchases for today", "Total deposit for today", "Bank Net"]
        self.total_income_table = self.create_tab(tab_widget, "Bank Net Today", headers=total_income_headers)

        bills_tab = BillsTabWidgt()
        tab_widget.addTab(bills_tab, "Bills")

        self.components_tab = Components()
        tab_widget.addTab(self.components_tab, "Components")

        analysis_tab = AnalysisTabWidget()
        tab_widget.addTab(analysis_tab, "Analysis")

        revenue_tab = StatisticsTab(start_label=self.start_date_edit, end_label=self.end_date_edit)
        tab_widget.addTab(revenue_tab, "Statistics")   
        
        self.refresh()

    def create_actions(self):
        # Create a right-click menu
        self.right_click_menu = QMenu(self)
        
        # Add a "Refresh" action to the menu
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh)

        add_item_action =QAction("add_item", self)
        add_item_action.triggered.connect(self.add_item)

        remove_item_action = QAction("remove_item", self)
        remove_item_action.triggered.connect(self.remove_item)

        add_ingrident_action = QAction("add_ingrident to Inventory", self)
        add_ingrident_action.triggered.connect(self.add_ingredient)

        add_purchase_action = QAction("add_purchase", self)
        add_purchase_action.triggered.connect(self.add_purchase)

        add_order_action = QAction("new_order", self)
        add_order_action.triggered.connect(self.show_orders)

        update_item_action = QAction("update Item", self)
        update_item_action.triggered.connect(self.update_item)

        self.right_click_menu.addAction(refresh_action)
        self.right_click_menu.addAction(add_item_action)
        self.right_click_menu.addAction(remove_item_action)
        self.right_click_menu.addAction(add_ingrident_action)
        self.right_click_menu.addAction(add_purchase_action)
        self.right_click_menu.addAction(add_order_action)
        self.right_click_menu.addAction(update_item_action)

    def create_tab(self, tab_widget, tab_name, headers):
        tab = QWidget()
        tab.setStyleSheet("background-color: grey; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        table = self.create_table(headers=headers)
        layout = QVBoxLayout(tab)
        layout.addWidget(table)
        tab_widget.addTab(tab, tab_name)
        return table
    def create_menu_bar(self):
        menu_bar = self.menuBar()

        # Create an "Items" menu
        items_menu = menu_bar.addMenu("Items")
        add_item_action = QAction("Add Item", self)
        add_item_action.triggered.connect(self.add_item)
        items_menu.addAction(add_item_action)

        remove_item_action = QAction("Remove Item", self)
        remove_item_action.triggered.connect(self.remove_item)
        items_menu.addAction(remove_item_action)

        update_item_action = QAction("Update Item", self)
        update_item_action.triggered.connect(self.update_item)
        items_menu.addAction(update_item_action)

        # Create an "Orders" menu
        orders_menu = menu_bar.addMenu("Orders")
        new_order_action = QAction("New Order", self)
        new_order_action.triggered.connect(self.show_orders)
        orders_menu.addAction(new_order_action)

        # Create an "Inventory" menu
        inventory_menu = menu_bar.addMenu("Inventory")
        add_ingredient_action = QAction("Add Ingredient", self)
        add_ingredient_action.triggered.connect(self.add_ingredient)
        inventory_menu.addAction(add_ingredient_action)

        # Create a "Purchases" menu
        purchases_menu = menu_bar.addMenu("Purchases")
        add_purchase_action = QAction("Add Purchase", self)
        add_purchase_action.triggered.connect(self.add_purchase)
        purchases_menu.addAction(add_purchase_action)    

    def create_date_widgets(self):
        start_date_label = QLabel(self)
        start_date_label.setText("Start Date")
        start_date_label.setAlignment(Qt.AlignRight)
        start_date_label.setGeometry(QRect(1000, 60, 120, 25))
        start_date_label.setFont(QFont("Arial", 12, QFont.Bold))

        end_date_label = QLabel(self)
        end_date_label.setText("End Date")
        end_date_label.setAlignment(Qt.AlignRight)
        end_date_label.setGeometry(QRect(1150, 60, 120, 25))
        end_date_label.setFont(QFont("Arial", 12, QFont.Bold))

        self.start_date_edit = QDateEdit(QDate.currentDate().addDays(1 - QDate.currentDate().day()), self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setGeometry(1050, 80, 120, 25)

        self.end_date_edit = QDateEdit(QDate.currentDate().addDays(QDate.currentDate().daysInMonth() - QDate.currentDate().day()), self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setGeometry(1200, 80, 120, 25)
    def set_background_image(self, image_path):
        palette = QPalette()
        bg_image = QImage(image_path)
        palette.setBrush(QPalette.Background, QBrush(bg_image))
        self.setPalette(palette)
    def create_title_label(self):
        title_label = QLabel(self)
        title_label.setText("Operations")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setGeometry(QRect(400, 50, 600, 50))
        title_label.setStyleSheet("background-color: rgba(255, 255, 255, 150); font-size: 40px;")
    
    def show_orders(self):
        conn, c = self.connect()
        items_data = pd.read_sql_query("select * from items", conn)
        conn.close()
        order_dialog = OrderDialog(data= items_data, parent=self)
        order_dialog.show()
    
    def showRightClickMenu(self, point):
        # Show the right-click menu at the given point
        self.right_click_menu.exec_(self.mapToGlobal(point))

    def refresh(self):
        # Your refresh logic here
        print("Refreshing...")
        self.load_data(table = self.inventory_table, sql_table="Inventory", Inventory=True)
        self.load_data(table= self.purchase_table, sql_table="purchases", purchase=True)
        self.load_data(table=self.items_table, sql_table="items")
        self.load_data(table=self.sales_table, sql_table="orders",sales=True )
        self.load_data(table=self.total_income_table, sql_table= None,total_income=True)
        self.components_tab.refresh()
    def get_all_ingredients(self):
        conn, c = self.connect()
        ingridents_in_Inventory = pd.read_sql_query("select Ingred_name from ingredients", conn)["Ingred_name"].apply(lambda x: str(x).lower()).tolist()
        conn.close()
        return ingridents_in_Inventory
    # function to add a new item to the database
    def add_item(self):
        # create a connection to the database
        conn , c = self.connect()
        # create a form to input the item name, price, and ingredients
        form = QDialog()
        form.setWindowTitle("Add Item")
        form.setFixedSize(500, 300)
        form_layout = QFormLayout(form)
        name_input = QLineEdit()
        name_validator = QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), name_input)
        name_input.setValidator(name_validator)
        price_input = QLineEdit()
        price_validator = QRegExpValidator(QRegExp("^[1-9]\d*(\.\d{1,3})?$"), price_input)
        price_input.setValidator(price_validator)
        category_input = QComboBox()
        category_input.addItems(['Meet', 'Chicken', 'Fish', 'Side_dish', 'Salads', 'Soups', 'Pasta', 'Main_plate', 'Sushi_mahshi', 'Fatta', 'Brams', 'Sweets', "bakery"])
        ingredient_table = QTableWidget()
        ingredient_table.setColumnCount(2)
        ingredient_table.setHorizontalHeaderLabels(["Ingredient", "Amount"])
        ingredient_table.horizontalHeader().setStretchLastSection(True)
        ingredient_table.setSortingEnabled(True)
        ingredient_label = QLabel("Ingredient:")
        amount_label = QLabel("Amount:")
        ingredient_input = QComboBox()
        ingredient_input.setEditable(True)
        ingredient_input.setCompleter(QCompleter(self.get_all_ingredients(), self))
        ingredient_input.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), ingredient_input))
        amount_input = QLineEdit()
        amount_validator = QRegExpValidator(QRegExp("^[0-9]\d*(\.\d{1,3})?$"), amount_input)
        amount_input.setValidator(amount_validator)
        add_ingredient_button = QPushButton("Add Ingredient")
        remove_ingredient_button = QPushButton("Remove Ingredient")
        ingredient_layout = QHBoxLayout()
        ingredient_layout.addWidget(ingredient_label)
        ingredient_layout.addWidget(ingredient_input)
        ingredient_layout.addWidget(amount_label)
        ingredient_layout.addWidget(amount_input)
        ingredient_layout.addWidget(add_ingredient_button)
        ingredient_layout.addWidget(remove_ingredient_button)
        form_layout.addRow("Item Name:", name_input)
        form_layout.addRow("Item Price:", price_input)
        form_layout.addRow("Category:", category_input)
        form_layout.addRow("Ingredients:", ingredient_table)
        form_layout.addRow(ingredient_layout)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addRow(button_box)

        
        # when the form is submitted, try to insert the item into the database
        def add_item_to_database():
            # get the name and price from the form
            name = name_input.text().upper()
            price = price_input.text().upper()
            category = category_input.currentText().upper()
            
            # check if the item already exists in the database
            c.execute("SELECT * FROM items WHERE Item_name=?", (name,))
            result = c.fetchone()
            if result is not None:
                # display a warning message if the item already exists
                QMessageBox.warning(form, "Item Already Exists", f"The item '{name}' already exists in the database.")
            else:
                passwords= pd.read_sql_query("select password from users where authorization = 'admin'", conn)
                ok , password = self.permission()
                if name and price and category and ok and password in passwords.values and ingredient_table.rowCount() > 0:
                    try:
                        # insert the new item into the database
                        c.execute("INSERT INTO items (Item_name, Item_price, Item_category) VALUES (?, ?, ?)", (name, price, category))
                        conn.commit()
                        
                        # retrieve the ID of the newly inserted item
                        c.execute("SELECT MAX(Item_id) FROM items")
                        item_id = c.fetchone()[0]
                        
                        # Insert the ingredients for the new item into the database
                        for i in range(ingredient_table.rowCount()):
                            ingred_name = ingredient_table.item(i, 0).text().upper()
                            ingred_amount = ingredient_table.item(i, 1).text()

                            # Check if the ingredient already exists in the database
                            c.execute("SELECT * FROM ingredients WHERE Ingred_name=?", (ingred_name,))
                            result = c.fetchone()

                            if result is not None:
                                # If the ingredient already exists, retrieve its ID
                                ingred_id = result[0]
                            else:
                                # If the ingredient does not exist, insert it into the ingredients table
                                c.execute("INSERT INTO ingredients (Ingred_name) VALUES (?)", (ingred_name,))
                                ingred_id = c.lastrowid

                            # Insert the ingredient and its amount into the item_ingredients table
                            c.execute("INSERT INTO item_ingredients (Item_id, Ingred_id, Ingred_amount) VALUES (?, ?, ?)", (item_id, ingred_id, ingred_amount))

                        conn.commit()

                        # refresh the table widget to show the new item
                        self.load_data(table=self.items_table, sql_table="items")
                    except sqlite3.Error as error:
                        QMessageBox.warning(form, "Warning", error)
                    finally:
                        # close the form
                        form.close()
                else:
                    QMessageBox.warning(form, "Warning", "Please complete the form.")
        def add_item_ingredient():
            ingredient_name = ingredient_input.currentText().upper()
            ingredient_amount = amount_input.text()

            # Check if ingredient name is empty
            if not ingredient_name:
                QMessageBox.warning(self, "Warning", "Please select an ingredient.")
                return

            # Check if ingredient amount is empty
            if not ingredient_amount:
                QMessageBox.warning(self, "Warning", "Please enter an ingredient amount.")
                return

            # Check if ingredient already exists in the table
            row_count = ingredient_table.rowCount()
            for i in range(row_count):
                if ingredient_table.item(i, 0).text().upper() == ingredient_name:
                    # Update the existing row instead of returning
                    ingredient_table.setItem(i, 1, QTableWidgetItem(ingredient_amount))
                    ingredient_table.sortItems(0)
                    # Clear the input fields
                    ingredient_input.setCurrentIndex(0)
                    amount_input.setText("")
                    
                    return

            # Add ingredient to table
            row_position = ingredient_table.rowCount()
            ingredient_table.insertRow(row_position)
            ingredient_table.setItem(row_position, 0, QTableWidgetItem(ingredient_name))
            ingredient_table.setItem(row_position, 1, QTableWidgetItem(ingredient_amount))
            # ingredient_table.sortItems(0)
            # Clear the input fields
            ingredient_input.setCurrentIndex(0)
            amount_input.setText("")
            ingredient_input.setCompleter(QCompleter(self.get_all_ingredients(), self))

        def remove_item_ingredient():
            selected_items = ingredient_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "Warning", "Please select an ingredient to remove.")
                return

            # Get a set of the unique row numbers corresponding to the selected items
            selected_rows = {item.row() for item in selected_items}

            # Remove the rows in reverse order
            for row in reversed(sorted(selected_rows)):
                ingredient_table.removeRow(row)

        add_ingredient_button.clicked.connect(add_item_ingredient)
        remove_ingredient_button.clicked.connect(remove_item_ingredient)    
            
        button_box.accepted.connect(add_item_to_database)
        button_box.rejected.connect(form.reject)
        
        form.exec_()
        
        # close the database connection
        conn.close()
    
     # function to add a new item to the database
    def remove_item(self):
        # create a connection to the database
        conn, c = self.connect()
        
        # create a form to input the item name and price
        form = QDialog()
        form.setWindowTitle("remove Item")
        form.setFixedSize(300, 150)
        form_layout = QFormLayout(form)
        items = pd.read_sql_query("select Item_name from items", conn)["Item_name"].values
        name_input = QComboBox()
        name_input.addItems(list(items))
        
        
        form_layout.addRow("Item Name:", name_input)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addRow(button_box)
        
        # when the form is submitted, try to insert the item into the database
        def remove_item_from_database():
            # get the name and price from the form
            name = name_input.currentText().upper()
            
            # check if the item already exists in the database
            c.execute("SELECT * FROM items WHERE Item_name=?", (name,))
            result = c.fetchone()
            if result is None:
                # display a warning message if the item already exists
                QMessageBox.warning(form, "Item Not Exists", f"The item '{name}' not exists in the database.")
            else:
                passwords= pd.read_sql_query("select password from users where authorization = 'admin'", conn)
                ok , password = self.permission()
                if name and ok and password in passwords.values:
                    try:

                        # insert the new item into the database
                        c.execute(f"Delete from items where Item_name = '{name}'")
                        conn.commit()
                        # refresh the table widget to show the new item
                        self.load_data(table=self.items_table, sql_table="items")
                        
                    except sqlite3.Error as error:
                        QMessageBox.warning(form, "Warnning" ,error)
                    finally:
                        # close the form
                        form.close()

                else:
                    QMessageBox.warning(form, "Warnning" ,"Please Complete the Form.")
            
            
        button_box.accepted.connect(remove_item_from_database)
        button_box.rejected.connect(form.reject)
        
        form.exec_()
        
        # close the database connection
        conn.close()
    # function to add a new ingrident to the database
    def add_ingredient(self):
        # create a connection to the database
        conn , c= self.connect()
        passwords= pd.read_sql_query("select password from users where authorization = 'admin'", conn)
        # create a form to input the ingrident name and price and count
        form = QDialog()
        form.setWindowTitle("Add Ingrident")
        form.setFixedSize(300, 150)
        form_layout = QFormLayout(form)
        name_input = QComboBox()
        name_input.setEditable(True)
        name_input.setCompleter(QCompleter(self.get_all_ingredients(), self))
        name_input.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), name_input))

        count_input = QLineEdit()

        price_input = QLineEdit()

        price_input.setValidator(QRegExpValidator(QRegExp("^[0-9]\d*(\.\d{1,3})?$"), price_input))

        form_layout.addRow("Ingrident Name:", name_input)
        form_layout.addRow("Ingrident Price", price_input)
        form_layout.addRow("Ingrident count:", count_input)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addRow(button_box)
        
        # when the form is submitted, try to insert the item into the database
        def add_ingrident_to_database():
            # Get the name, price, and count from the form
            name = name_input.currentText().upper()
            price = price_input.text()
            count = count_input.text().upper()
            ok, password = self.permission()
            
            if name and count:
                if ok and password in passwords.values:
                    # Check if the ingredient already exists in the database
                    c.execute("SELECT * FROM Inventory WHERE Ingrident_name=?", (name,))
                    result = c.fetchone()
                    if result is not None:
                        # If the ingredient already exists, update its count by adding the new count
                        current_count = result[4]
                        new_count = str(round(float(current_count) + float(count), 3))
                        c.execute("UPDATE Inventory SET Ingrident_count=? WHERE Ingrident_name=?", (new_count, name))
                    else:
                        # Check if the ingredient already exists in the database
                        c.execute("SELECT * FROM ingredients WHERE Ingred_name=?", (name,))
                        result = c.fetchone()

                        if result is not None:
                            # If the ingredient already exists, retrieve its ID
                            ingred_id = result[0]
                        else:
                            # If the ingredient does not exist, insert it into the ingredients table
                            c.execute("INSERT INTO ingredients (Ingred_name) VALUES (?)", (name,))
                            ingred_id = c.lastrowid
                        # If the ingredient does not exist, insert it into the database
                        c.execute("INSERT INTO Inventory (Ingriednt_id,Ingrident_name, Ingrident_price_per_unit, Ingrident_count) VALUES (?,?,?,?)", (ingred_id,name, price, count))
                    
                    conn.commit()
                    
                    # Refresh the table widget to show the updated data
                    self.load_data(table=self.inventory_table, sql_table="Inventory", Inventory=True)
                    
                    # Close the form
                    form.close()
                elif ok and password not in passwords.values:
                    QMessageBox.warning(form, "Authorization Error", "Incorrect password")
                else:
                    pass
            else:
                QMessageBox.warning(form, "Warning", "Please complete the form.")

            
            
        button_box.accepted.connect(add_ingrident_to_database)
        button_box.rejected.connect(form.reject)
        
        form.exec_()
        
        # close the database connection
        conn.close()
    # Function to update an existing item in the database
    def update_item(self):
        # Create a connection to the database
        conn , c = self.connect()

        # Create a form to input the item details
        form = QDialog()
        form.setWindowTitle("Update Item")
        form.setFixedSize(500, 300)
        form_layout = QFormLayout(form)

        items = pd.read_sql_query("SELECT Item_name FROM items", conn)["Item_name"].values
        name_input = QComboBox()
        name_input.addItems(list(items))

        # Get the existing details of the selected item
        selected_item = name_input.currentText()
        c.execute("SELECT Item_name, Item_price, Item_category FROM items WHERE Item_name=?", (selected_item,))
        item_details = c.fetchone()
        if item_details:
            # Create the input fields with the existing details pre-filled
            name_input.setCurrentText(item_details[0])
            price_input = QLineEdit(str(item_details[1]))
            category_input = QComboBox()
            category_input.addItems(['Meet', 'Chicken', 'Fish', 'Side_dish', 'Salads', 'Soups', 'Pasta', 'Main_plate', 'Sushi_mahshi', 'Fatta', 'Brams', 'Sweets'])
            category_input.setCurrentText(item_details[2])

            ingredient_table = QTableWidget()
            ingredient_table.setColumnCount(2)
            ingredient_table.setHorizontalHeaderLabels(["Ingredient", "Amount"])
            ingredient_table.horizontalHeader().setStretchLastSection(True)
            ingredient_table.setSortingEnabled(True)

            # Fetch the existing ingredients for the selected item
            c.execute("""
                SELECT i.Ingred_name, ii.Ingred_amount
                FROM ingredients AS i
                JOIN item_ingredients AS ii ON i.Ingredients_id = ii.Ingred_id
                JOIN items AS it ON ii.Item_id = it.Item_id
                WHERE it.Item_name=?
            """, (selected_item,))
            ingredients = c.fetchall()

            # Populate the ingredient table with existing ingredients
            ingredient_table.setRowCount(len(ingredients))
            for i, ingredient in enumerate(ingredients):
                ingredient_name = ingredient[0]
                ingredient_amount = ingredient[1]
                ingredient_table.setItem(i, 0, QTableWidgetItem(ingredient_name))
                ingredient_table.setItem(i, 1, QTableWidgetItem(ingredient_amount))

            ingredient_label = QLabel("Ingredient:")
            amount_label = QLabel("Amount:")
            ingredient_input = QComboBox()
            ingredient_input.setEditable(True)
            ingredient_input.setCompleter(QCompleter(self.get_all_ingredients(), self))
            ingredient_input.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), ingredient_input))
            amount_input = QLineEdit()
            amount_validator = QRegExpValidator(QRegExp("^[0-9]\d*(\.\d{1,3})?$"), amount_input)
            amount_input.setValidator(amount_validator)
            add_ingredient_button = QPushButton("Add Ingredient")
            remove_ingredient_button = QPushButton("Remove Ingredient")
            ingredient_layout = QHBoxLayout()
            ingredient_layout.addWidget(ingredient_label)
            ingredient_layout.addWidget(ingredient_input)
            ingredient_layout.addWidget(amount_label)
            ingredient_layout.addWidget(amount_input)
            ingredient_layout.addWidget(add_ingredient_button)
            ingredient_layout.addWidget(remove_ingredient_button)
            form_layout.addRow("Item Name:", name_input)
            form_layout.addRow("Item Price:", price_input)
            form_layout.addRow("Category:", category_input)
            form_layout.addRow("Ingredients:", ingredient_table)
            form_layout.addRow(ingredient_layout)
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            form_layout.addRow(button_box)

            # When the form is submitted, try to update the item in the database
            def update_item_in_database():
                # Get the selected item and its new details
                selected_item = name_input.currentText()
                new_name = name_input.currentText().upper()
                new_price = price_input.text().upper()
                new_category = category_input.currentText().upper()

                # Check if the item exists in the database
                c.execute("SELECT * FROM items WHERE Item_name=?", (selected_item,))
                result = c.fetchone()
                if result is None:
                    # Display a warning message if the item does not exist
                    QMessageBox.warning(form, "Item Not Found", f"The item '{selected_item}' was not found in the database.")
                else:
                    passwords = pd.read_sql_query("SELECT password FROM users WHERE authorization = 'admin'", conn)
                    ok, password = self.permission()
                    if new_name and new_price and new_category and ok and password in passwords.values and ingredient_table.rowCount() > 0:
                        try:
                            # Update the item details in the database
                            c.execute("UPDATE items SET Item_name=?, Item_price=?, Item_category=? WHERE Item_name=?", (new_name, new_price, new_category, selected_item))
                            conn.commit()

                            # Retrieve the ID of the updated item
                            c.execute("SELECT Item_id FROM items WHERE Item_name=?", (new_name,))
                            item_id = c.fetchone()[0]

                            # Delete the existing ingredients for the item from the database
                            c.execute("DELETE FROM item_ingredients WHERE Item_id=?", (item_id,))

                            # Insert the updated ingredients for the item into the database
                            for i in range(ingredient_table.rowCount()):
                                ingred_name = ingredient_table.item(i, 0).text().upper()
                                ingred_amount = ingredient_table.item(i, 1).text()

                                # Check if the ingredient already exists in the database
                                c.execute("SELECT * FROM ingredients WHERE Ingred_name=?", (ingred_name,))
                                result = c.fetchone()

                                if result is not None:
                                    # If the ingredient already exists, retrieve its ID
                                    ingred_id = result[0]
                                else:
                                    # If the ingredient does not exist, insert it into the ingredients table
                                    c.execute("INSERT INTO ingredients (Ingred_name) VALUES (?)", (ingred_name,))
                                    ingred_id = c.lastrowid

                                # Insert the ingredient and its amount into the item_ingredients table
                                c.execute("INSERT INTO item_ingredients (Item_id, Ingred_id, Ingred_amount) VALUES (?, ?, ?)", (item_id, ingred_id, ingred_amount))

                            conn.commit()

                            # Refresh the table widget to show the updated item
                            self.load_data(table=self.items_table, sql_table="items")
                        except sqlite3.Error as error:
                            QMessageBox.warning(form, "Warning", error)
                        finally:
                            # Close the form
                            form.close()
                    else:
                        QMessageBox.warning(form, "Warning", "Please complete the form.")

            def add_item_ingredient():
                ingredient_name = ingredient_input.currentText().upper()
                ingredient_amount = amount_input.text()

                # Check if ingredient name is empty
                if not ingredient_name:
                    QMessageBox.warning(self, "Warning", "Please select an ingredient.")
                    return

                # Check if ingredient amount is empty
                if not ingredient_amount:
                    QMessageBox.warning(self, "Warning", "Please enter an ingredient amount.")
                    return

                # Check if ingredient already exists in the table
                row_count = ingredient_table.rowCount()
                for i in range(row_count):
                    if ingredient_table.item(i, 0).text().upper() == ingredient_name:
                        # Update the existing row instead of returning
                        ingredient_table.setItem(i, 1, QTableWidgetItem(ingredient_amount))
                        ingredient_table.sortItems(0)
                        # Clear the input fields
                        ingredient_input.setCurrentIndex(0)
                        amount_input.setText("")

                        return

                # Add ingredient to table
                row_position = ingredient_table.rowCount()
                ingredient_table.insertRow(row_position)
                ingredient_table.setItem(row_position, 0, QTableWidgetItem(ingredient_name))
                ingredient_table.setItem(row_position, 1, QTableWidgetItem(ingredient_amount))
                # ingredient_table.sortItems(0)
                # Clear the input fields
                ingredient_input.setCurrentIndex(0)
                amount_input.setText("")
                ingredient_input.setCompleter(QCompleter(self.get_all_ingredients(), self))

            def remove_item_ingredient():
                selected_items = ingredient_table.selectedItems()
                if not selected_items:
                    QMessageBox.warning(self, "Warning", "Please select an ingredient to remove.")
                    return

                # Get a set of the unique row numbers corresponding to the selected items
                selected_rows = {item.row() for item in selected_items}

                # Remove the rows in reverse order
                for row in reversed(sorted(selected_rows)):
                    ingredient_table.removeRow(row)

            add_ingredient_button.clicked.connect(add_item_ingredient)
            remove_ingredient_button.clicked.connect(remove_item_ingredient)
            button_box.accepted.connect(update_item_in_database)
            button_box.rejected.connect(form.reject)

            form.exec_()

            # Close the database connection
            conn.close()
        else:
            error_box = QMessageBox()
            error_box.setIcon(QMessageBox.Critical)
            error_box.setWindowTitle("Error")
            error_box.setText("There Is No Item To Update")
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.exec_()
    # function to add a new purchases to the database
    def add_purchase(self):
        # create a connection to the database
        conn, c = self.connect()
        
        
        # create a form to input the ingrident name and price and count
        form = QDialog()
        form.setWindowTitle("Add Purchase")
        form.setFixedSize(300, 150)
        form_layout = QFormLayout(form)
        name_input = QComboBox()
        name_input.setEditable(True)
        name_input.setCompleter(QCompleter(self.get_all_ingredients(), self))
        name_input.setValidator(QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), name_input))
        price_input = QLineEdit()
        price_validator = QRegExpValidator(QRegExp("^[0-9]\d*(\.\d{1,3})?$"), price_input)
        price_input.setValidator(price_validator)
        count_input = QLineEdit()
        count_validator = QRegExpValidator(QRegExp("^[0-9]\d*(\.\d{1,3})?$"), count_input)
        count_input.setValidator(count_validator)
        form_layout.addRow("Ingrident Name:", name_input)
        form_layout.addRow("Ingrident Price:", price_input)
        form_layout.addRow("Ingrident count:", count_input)
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form_layout.addRow(button_box)
        
        # when the form is submitted, try to insert the item into the database
        def add_purchase_to_database():
            # get the name and price from the form
            name = name_input.currentText().upper()
            price = price_input.text().upper()
            count = count_input.text().upper()
            if name and price and count:
                # insert the new ingrdients into the database
                c.execute("INSERT INTO purchases (Ingrident_name, Ingrident_price_per_unit, Ingrident_count) VALUES (?,?,?)", (name, price, count))
                conn.commit()
                # refresh the table widget to show the new item
                self.load_data(table= self.purchase_table, sql_table="purchases", purchase=True)
                self.load_data(table= self.total_income_table,sql_table=None, total_income= True)
                # close the form
                form.close()
            else:
                QMessageBox.warning(form, "Warnning" ,"Please Complete the Form.")
        # when the form is submitted, try to insert the item into the database
        def add_ingrident_to_database():
            # get the name, price, and count from the form
            name = name_input.currentText().upper()
            price = price_input.text().upper()
            count = count_input.text().upper()
            if name and price and count:
                # check if the ingredient already exists in the database
                c.execute("SELECT * FROM Inventory WHERE Ingrident_name = ?", (name,))
                existing_row = c.fetchone()

                if existing_row:
                    # ingredient already exists, update the amount and calculate the new average price
                    existing_count = round(float(existing_row[5]), 3)
                    print(existing_count)
                    existing_price = round(float(existing_row[4]), 3)
                    print(existing_price)
                    print("count:", count)
                    total_count = existing_count + float(count)
                    avg_price = round(((existing_price * existing_count) + (float(price) * float(count))) / total_count , 3)

                    # update the existing record in the database
                    c.execute("UPDATE Inventory SET Ingrident_count = ?, Ingrident_price_per_unit = ? WHERE Ingriednt_id = ?",
                            (total_count, avg_price, existing_row[1]))
                else:
                    c.execute("SELECT * FROM ingredients WHERE Ingred_name=?", (name,))
                    result = c.fetchone()

                    if result is not None:
                        # If the ingredient already exists, retrieve its ID
                        ingred_id = result[0]
                    else:
                        # If the ingredient does not exist, insert it into the ingredients table
                        c.execute("INSERT INTO ingredients (Ingred_name) VALUES (?)", (name,))
                        ingred_id = c.lastrowid
                    # ingredient doesn't exist, insert a new record into the database
                    c.execute("INSERT INTO Inventory (Ingriednt_id, Ingrident_name, Ingrident_price_per_unit, Ingrident_count) VALUES (?,?,?,?)",
                            (ingred_id,name, price, count))
                    conn.commit()
                c.execute("select * from ingredients where Ingred_name = ?", (name,))
                ingred_row = c.fetchone()
                if ingred_row:
                    pass
                else:
                    c.execute(f"insert into ingredients (Ingred_name) values('{name}')" )
                    conn.commit()

                conn.commit()
                # refresh the table widget to show the updated or new item
                self.load_data(table=self.inventory_table, sql_table="Inventory", purchase=True)
                # close the form
                form.close()
   
            
        button_box.accepted.connect(add_purchase_to_database)
        button_box.accepted.connect(add_ingrident_to_database)
        button_box.rejected.connect(form.reject)
        
        form.exec_()
        
        # close the database connection
        conn.close()
            
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
    # function to load data from database and populate table
    def load_data(self,table, sql_table , Inventory=False, purchase= False, sales= False, total_income = False):
        start = self.start_date_edit.date().toString("yyyy-MM-dd")
        end = self.end_date_edit.date().toString("yyyy-MM-dd")
        # create a connection to the database
        conn , cursor = self.connect()
        if Inventory == True:
            df = pd.read_sql_query(f"SELECT Distinct Ingrident_name , round(avg(Ingrident_price_per_unit),2), round(sum(Ingrident_count), 2), round(sum(Total_price),2) FROM {sql_table} group by Ingrident_name", conn)
            # df = pd.read_sql_query(f"SELECT Distinct Ingrident_name , round(avg(Ingrident_price_per_unit),2), round(sum(Ingrident_count), 2), round(sum(Total_price),2) FROM {sql_table} where Entry_date >= '{start}' and Entry_date <='{end}' group by Ingrident_name", conn)
        elif purchase== True:
            df = pd.read_sql_query(f"SELECT  Ingrident_name , round(Ingrident_price_per_unit,2), round(Ingrident_count, 2), round(Total_price,2), Entry_date FROM {sql_table} where Entry_date >= '{start}' and Entry_date <='{end}' order by Ingrident_name, Entry_date ", conn)

        elif sales == True:
            df = pd.read_sql_query(f"""SELECT
             CASE WHEN ROW_NUMBER() OVER (PARTITION BY c.Name ORDER BY o.bill_id) = 1 THEN CAST(c.Name AS TEXT) ELSE '' END 
             AS customer_Name, i.Item_name, i.Item_category, o.quantity, i.Item_price, o.total_price , o.note
             FROM orders AS o 
             left JOIN items AS i
             ON o.product_id = i.Item_id 
             left join customers AS c
             ON o.customer_id = c.id
             WHERE o.order_date >= '{start}' and o.order_date <= '{end}' 
             ORDER BY o.customer_id, o.bill_id """, conn)
        elif total_income == True:
            # Execute the SQL query
            df = pd.read_sql_query(f"""
                SELECT
                COALESCE((SELECT SUM(Total_price) FROM purchases WHERE Entry_date = CURRENT_DATE), 0) AS total_purchases_today,
                COALESCE((SELECT SUM(deposite) FROM bills WHERE bill_net > 0 AND date = CURRENT_DATE), 0) AS total_Income_today,
                COALESCE((SELECT SUM(deposite) FROM bills WHERE bill_net > 0 AND date = CURRENT_DATE), 0) - COALESCE((SELECT SUM(Total_price) FROM purchases WHERE Entry_date = CURRENT_DATE), 0) AS net_amount_in_bank;

            """, conn)
        
        else:
            # read the data into a pandas dataframe
            df = pd.read_sql_query(f"SELECT * FROM {sql_table} ", conn)

        # set the number of rows in the table widget
        table.setRowCount(df.shape[0])
        # set font and background color for table items
        font = QFont("Arial", 12, QFont.Bold)
        table.setStyleSheet("color: black; background-color: transparent;")
        # populate the table widget with the data
        for row in range(df.shape[0]):
            for col in range(df.shape[1]):
                ingrident = QTableWidgetItem(str(df.iloc[row, col]))
                ingrident.setFont(font)
                ingrident.setBackground(QColor(173, 216, 230))
                ingrident.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, col, ingrident)
        # table.resizeColumnsToContents()
        table.resizeRowsToContents()
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)    

        # close the database connection
        conn.close()
    def connect(self):
        try:
            conn = sqlite3.connect("restaurant_database.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as error:
            QMessageBox.warning(form, "Warning", error)

    def permission(self):
        password_dialog = QInputDialog()
        password_dialog.setWindowTitle("Take Permission")
        password_dialog.setInputMode(QInputDialog.TextInput)
        password_dialog.setLabelText("Please enter the admin password:")
        password_dialog.setTextEchoMode(QLineEdit.Password)
        ok = password_dialog.exec_()
        password = password_dialog.textValue()
        conn, cursor = self.connect()
        cursor.execute("select password from users where authorization = 'admin'")
        correct_passwords = cursor.fetchall()[0]
        if password in correct_passwords:
            return ok , password
        else:
            return None , None
