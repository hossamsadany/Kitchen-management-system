import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QScrollArea, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox, QHBoxLayout, QVBoxLayout, QGridLayout, QGroupBox, QDialog, QListWidget, QTabWidget, QTreeView, QListView, QTableView, QGraphicsView, QAction, QMenuBar, QToolBar, QStatusBar, QFileDialog, QInputDialog, QDateEdit, QWidget, QTableWidget, QHeaderView, QTableWidgetItem, QMenu, QFormLayout, QCompleter, QDialogButtonBox
from PyQt5.QtGui import QTextDocument, QIcon, QPixmap, QFont, QColor, QPalette, QPainter, QBrush, QPen, QCursor, QImage, QKeySequence, QValidator, QStandardItemModel, QStandardItem, QTextCursor, QRegExpValidator
from PyQt5.QtCore import QSizeF, Qt, QEvent, QPoint, QRect, pyqtSlot, QRegularExpression, QDateTime, QTime, QDate, QTimeZone, QItemSelection, QRegExp
import pandas as pd
from PyQt5.QtPrintSupport import QPrinter
import matplotlib.pyplot as plt
import numpy as np
import io
import os
from datetime import datetime
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter

class OrderDialog(QDialog):
    def __init__(self, parent=None, data=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)  # Set window flags
        self.data = data  # Data containing items, prices, categories
        self.items = self.data[["Item_name", "Item_price"]]
        self.orders = {}
        self.discount = 0.0
        self.delivery_fees = 0.0
        self.note_edits = {}
        self.customer_data = {}
        self.init_ui()

    def init_ui(self):
        # set background image
        palette = QPalette()
        bg_image = QImage("Images/items.png")
        palette.setBrush(QPalette.Background, QBrush(bg_image))
        self.setPalette(palette)

        # self.resize(1400, 600) 
        font = QFont("Arial", 14, QFont.Bold)      
        self.total_label = QLabel("Total:")
        self.total_value_label = QLabel("0.00")
        self.total_label.setFont(font)
        self.total_value_label.setFont(font)

        main_layout = QVBoxLayout()  
        self.setLayout(main_layout)
        # Create a scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the main layout
        main_widget = QWidget()
        main_widget.setLayout(main_layout)

        # Set the main widget as the content of the scroll area
        scroll_area.setWidget(main_widget)

        # Set the scroll area as the main layout of the dialog
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(scroll_area)

        # Categories
        category_layout = QVBoxLayout()
        category_group_box = QGroupBox("Categories")
        category_group_box.setFixedHeight(200)
        
        category_group_box.setFont(font)
        category_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0.3); border: 3px solid gray; border-radius: 5px;}")
        category_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        category_group_box.setLayout(category_layout)
        
        button_layout = QHBoxLayout()

        buttons_per_line = 5
        button_counter = 0

        for category in self.data['Item_category'].unique():
            button = QPushButton(category)
            button.setFont(font)
            button.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);border: 3px solid white; border-radius: 5px;color: white; font-size: 18px;font-weight: bold;")
            button.setFixedWidth(200)
            button.clicked.connect(self.show_items)
            button_layout.addWidget(button)

            button_counter += 1
            if button_counter >= buttons_per_line:
                category_layout.addLayout(button_layout)
                button_layout = QHBoxLayout()
                button_counter = 0

        # Add the remaining buttons if not already added
        if button_counter > 0:
            category_layout.addLayout(button_layout)

        main_layout.addWidget(category_group_box)



        self.items_group_box = QGroupBox("Items")
        self.items_group_box.setFixedHeight(200)
        self.items_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0); border: 3px solid gray; border-radius: 5px;}")
        self.items_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        self.items_group_box.setFont(font)
        self.items_scroll_area = QScrollArea()
        self.items_scroll_area.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);border: 3px solid gray; border-radius: 5px;")
        self.items_scroll_area.setWidgetResizable(True)

        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_widget.setLayout(self.items_layout)
    
        self.items_scroll_area.setWidget(self.items_widget)
        self.items_group_box.setLayout(QVBoxLayout())
        self.items_group_box.layout().addWidget(self.items_scroll_area)


        main_layout.addWidget(self.items_group_box)

        self.items_buttons = []

        # Orders
        orders_group_box = QGroupBox("Orders")
        orders_group_box.setFont(font)
        orders_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0); border: 3px solid gray; border-radius: 5px; }")
        orders_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        orders_group_box.setFixedHeight(200)
        orders_layout = QVBoxLayout(orders_group_box)
        new_order_headers = ["Item", "Price", "Quantity", "Total", "Note"]
        self.orders_table = self.create_table(headers=new_order_headers)
        remove_item_button = QPushButton("Remove Item")
        remove_item_button.setFont(font)
        orders_layout.addWidget(remove_item_button)
        orders_layout.addWidget(self.orders_table)

        main_layout.addWidget(orders_group_box)

        # Customer information
        info_group_box = QGroupBox("Customer Information")
        info_group_box.setFont(font)
        info_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0);border: 3px solid gray; border-radius: 5px; }")
        info_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        info_group_box.setFixedHeight(250)
        info_layout = QGridLayout(info_group_box)
        
        conn , cursor = self.connect()
        try:
            cursor.execute("SELECT DISTINCT Name, Phone, Address, Phone2  FROM customers")
        except sqlite3.Error as error:
                print(error)
        names = [name[0] for name in cursor.fetchall()]
        conn.close()
        completer = QCompleter(names)
        name_label = QLabel("Name:")
        self.name_line_edit = QLineEdit()
        name_validator = QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), self.name_line_edit)
        self.name_line_edit.setValidator(name_validator)
        self.name_line_edit.setCompleter(completer)
        # Connect the name_line_edit textChanged signal to a slot
        self.name_line_edit.returnPressed.connect(self.on_name_changed)
        info_layout.addWidget(name_label, 1, 0)
        info_layout.addWidget(self.name_line_edit, 1, 1)

        phone_label = QLabel("Phone:")
        self.phone_line_edit = QLineEdit()
        phone_validator = QRegExpValidator(QRegExp("^\\d{5,15}$"), self.phone_line_edit)
        self.phone_line_edit.setValidator(phone_validator)
        info_layout.addWidget(phone_label, 2, 0)
        info_layout.addWidget(self.phone_line_edit, 2, 1)

        address_label = QLabel("Address:")
        self.address_line_edit = QLineEdit()
        info_layout.addWidget(address_label, 3, 0)
        info_layout.addWidget(self.address_line_edit, 3, 1)

        other_phones_label = QLabel("Other Phones:")
        self.other_phones_line_edit = QLineEdit()
        phone_validator = QRegExpValidator(QRegExp("^\\d{5,15}$"), self.other_phones_line_edit)
        self.other_phones_line_edit.setValidator(phone_validator)
        info_layout.addWidget(other_phones_label, 4, 0)
        info_layout.addWidget(self.other_phones_line_edit, 4, 1)
        # Discount
        discount_label = QLabel("Discount:")
        self.discount_line_edit = QLineEdit()
        discount_validator = QRegExpValidator(QRegExp("^\\d*\\.?\\d*$"), self.discount_line_edit)
        self.discount_line_edit.setValidator(discount_validator)
        info_layout.addWidget(discount_label, 5, 0)
        info_layout.addWidget(self.discount_line_edit, 5, 1)

        # Delivery Fees
        delivery_label = QLabel("Delivery Fees:")
        self.delivery_line_edit = QLineEdit()
        delivery_validator = QRegExpValidator(QRegExp("^\\d*\\.?\\d*$"), self.delivery_line_edit)
        self.delivery_line_edit.setValidator(delivery_validator)
        info_layout.addWidget(delivery_label, 6, 0)
        info_layout.addWidget(self.delivery_line_edit, 6, 1)
        
        note_label = QLabel("Note:")
        self.order_note_edit = QLineEdit()
        info_layout.addWidget(note_label, 7, 0)
        info_layout.addWidget(self.order_note_edit, 7, 1)
        add_customer_button =  QPushButton("Add Customer")
        add_customer_button.setFixedWidth(200)
        add_customer_button.clicked.connect(self.on_name_changed)
        info_layout.addWidget(add_customer_button, 8, 1)
        info_layout.setAlignment(add_customer_button, Qt.AlignCenter)

        orders_info_layout = QHBoxLayout()
        orders_info_layout.addWidget(orders_group_box)
        orders_info_layout.addWidget(info_group_box)
        main_layout.addLayout(orders_info_layout)


         # Orders History
        orders_history_group_box = QGroupBox("Orders History")
        orders_history_group_box.setFixedHeight(250)
        orders_history_group_box.setFont(font)
        orders_history_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0); border: 3px solid gray; border-radius: 5px; }")
        orders_history_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        orders_history_layout = QVBoxLayout(orders_history_group_box)
        order_history_headers = ["Date","Bill Number","Item", "Price", "Quantity","Total" ,"Note"]
        self.orders_history_table = self.create_table(headers= order_history_headers)

        orders_history_layout.addWidget(self.orders_history_table)

        main_layout.addWidget(orders_history_group_box)

        # Bill History
        bills_history_group_box = QGroupBox("Bills History")
        bills_history_group_box.setFixedHeight(200)
        bills_history_group_box.setFont(font)
        bills_history_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0); border: 3px solid gray; border-radius: 5px; }")
        bills_history_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        bills_history_layout = QVBoxLayout(bills_history_group_box)
        bills_history_headers = ["Date","Bill Number", "Subtotal", "Delivery fees","Discount" ,"Total", "Deposit", "Remaining", "Note"]
        self.bills_history_table = self.create_table(headers= bills_history_headers)
        bills_history_layout.addWidget(self.bills_history_table)

        main_layout.addWidget(bills_history_group_box)

        # New Order button bar
        button_layout = QVBoxLayout()
        
        new_order_button = QPushButton("Submit Order")
        new_order_button.setFont(font)
        new_order_button.setStyleSheet("background-color: blue;")
        # button_layout.addWidget(self.total_label)
        # button_layout.addWidget(self.total_value_label)
        
        # remove_item_button = QPushButton("Remove Item")
        # remove_item_button.setFont(font)
        self.deposit_amount = QLineEdit()
        deposit_validator =  QRegExpValidator(QRegExp("^\\d*\\.?\\d*$"),self.deposit_amount)
        self.deposit_amount.setValidator(deposit_validator)
        self.deposit_amount.setFont(font)
        conn , cursor = self.connect()
       
        try:
            cursor.execute("select bill_id from orders ORDER BY bill_id DESC LIMIT 1")
        except sqlite3.Error as error:
                print(error)
        last_record = cursor.fetchone()
        if last_record == None: 
            self.Bill_number = 1
        else:
            self.Bill_number = last_record[0] + 1
        
        conn.close()
        bill_label = QLabel("Bill Number:", font=font)
        self.bill_value = QLabel(str(self.Bill_number), font=font)
        bill_data = QHBoxLayout()
        bill_data.addWidget(bill_label)
        bill_data.addWidget(self.bill_value)
        bill_data.addWidget(self.total_label)
        bill_data.addWidget(self.total_value_label)
        button_layout.addLayout(bill_data)
        button_layout.addWidget(bill_label)
        button_layout.addWidget(self.bill_value)
        # button_layout.addWidget(QLabel(f"Bill Number: {self.Bill_number}", font=font))
        # button_layout.addWidget(remove_item_button)
        
        deposit_label = QLabel("Deposit:")
        deposit_label.setFont(font)
        button_layout.addWidget(deposit_label)
        button_layout.addWidget(self.deposit_amount)
        button_layout.addWidget(new_order_button)


        new_order_button.clicked.connect(self.new_order)
        remove_item_button.clicked.connect(self.remove_item)
        # Assuming `remove_item_button` is a QPushButton or QAction object
        remove_item_button.setShortcut(QKeySequence(Qt.Key_D + Qt.ControlModifier))
        button_group_box = QGroupBox("New Order")
        button_group_box.setFont(font)
        button_group_box.setStyleSheet("QGroupBox {background-color: rgba(0, 0, 0, 0.5);border: 3px solid gray; border-radius: 5px; }")
        button_group_box.setStyleSheet("QGroupBox::title {subcontrol-origin: margin;  subcontrol-position: top center; padding-top: 5px;}")
        # button_group_box.setFixedHeight(100)
        button_group_box.setLayout(button_layout)

        main_layout.addWidget(button_group_box)
        # Connect discount and delivery fees line edits to their respective slots
        self.discount_line_edit.returnPressed.connect(self.set_discount)
        self.delivery_line_edit.textChanged.connect(self.set_delivery_fees)

        self.showMaximized()
        self.setWindowTitle("Orders")
    def set_discount(self):
        value = self.discount_line_edit.text()
        if value:
            ok , password = self.permission()
            if ok and  password:
                try:
                    self.discount = float(value)
                except ValueError:
                    self.discount = 0.0
                self.update_total()


    def set_delivery_fees(self, value):
        try:
            self.delivery_fees = float(value)
        except ValueError:
            self.delivery_fees = 0.0
        self.update_total()

    def on_name_changed(self):
        name = self.name_line_edit.text().strip()
        conn, cursor = self.connect()
        try:
            cursor.execute("SELECT DISTINCT Name, Phone, Address, Phone2, ID FROM customers")
        except sqlite3.Error as error:
            print(error)
        data = cursor.fetchall()
        # Store the data as a dictionary for quick lookup
        self.customer_data = {record[0]: (record[1], record[2], record[3], record[4]) for record in data}
        conn.close()
        if name in self.customer_data:
            phone, address, phone2 , id = self.customer_data[name]
            self.phone_line_edit.setText(str(phone))
            self.address_line_edit.setText(address)
            self.other_phones_line_edit.setText(str(phone2))
            self.load_history_data(table= self.orders_history_table, id= id, orders_history= True)
            self.load_history_data(table= self.bills_history_table, id = id, bills_history= True)
        else:
            reply = QMessageBox.warning(self, "Unknown Customer", f"{name} is not in our customers data.\n\nDo you want to add it to the customers data?", QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                conn, c = self.connect()
                phone = self.phone_line_edit.text().strip()
                address= self.address_line_edit.text().strip()
                other_phone = self.other_phones_line_edit.text().strip()
                if name and phone and address :
                    try:
                        c.execute("INSERT INTO customers (Name, Phone, Address, Phone2) values(?,?,?,?)",(name, phone , address, other_phone))
                        conn.commit()
                        QMessageBox.information(self, "Successful Task", f"The Customer {name} has been added successfully")
                        c.execute("SELECT DISTINCT Name, Phone, Address, Phone2  FROM customers")
                    except sqlite3.Error as error:
                        print(error)
                    names = [name[0] for name in c.fetchall()]
                    id = c.lastrowid
                    completer = QCompleter(names)
                    self.name_line_edit.setCompleter(completer)
                    self.customer_data ={name: (phone, address, other_phone, id)}
                    print(self.customer_data)
                    self.load_history_data(table= self.orders_history_table, id= id, orders_history= True)
                    self.load_history_data(table= self.bills_history_table, id = id, bills_history= True)
                else:
                    QMessageBox.warning(self, "Missing Data", "Please Insert Name And Phone And Address, Other phone is option")
            # Clear the fields if the name doesn't exist
            self.phone_line_edit.clear()
            self.address_line_edit.clear()
            self.other_phones_line_edit.clear()

    def connect(self):
        try:
            conn = sqlite3.connect("restaurant_database.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as error:
            QMessageBox.warning(form, "Warning", error)
    def create_table(self, headers):
            table = QTableWidget()
            table.setColumnCount(len(headers))
            table.setHorizontalHeaderLabels(headers)
            table.verticalScrollBar().setStyleSheet("QScrollBar { width: 30px; }")
            table.horizontalHeader().setStretchLastSection(True)
            table.horizontalHeader().setFont(QFont("Arial", 12, QFont.Bold))
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setStyleSheet("background-color: transparent;")
            return table
    def show_items(self):
        category = self.sender().text()
        items = self.data[self.data['Item_category'] == category]

        # Remove existing buttons
        for button in self.items_buttons:
            self.items_layout.removeWidget(button)
            button.deleteLater()
            # button.setVisible(False)

        # Clear the items_buttons list
        self.items_buttons.clear()

        # Create a new QHBoxLayout for each row of buttons
        row_layout = QHBoxLayout()

        for row, item in items.iterrows():
            price = item["Item_price"]
            item_button = QPushButton(item['Item_name'])
            item_button.setStyleSheet("background-color: rgba(0, 0, 0, 0.7);border: 3px solid white; border-radius: 5px;color: white; font-size: 18px;font-weight: bold;")
            item_button.setFixedWidth(200)
            item_button.clicked.connect(lambda _, name=item["Item_name"], price=price: self.add_item(name, price))

            # Add the button to the current row layout
            row_layout.addWidget(item_button)

            # Check if the current row layout has reached the maximum number of buttons
            if row_layout.count() == 5:
                # Add the row layout to the items layout
                self.items_layout.addLayout(row_layout)

                # Create a new row layout for the next row
                row_layout = QHBoxLayout()

            # Check if button already exists in items_buttons list
            if item_button not in self.items_buttons:
                self.items_buttons.append(item_button)

        # Add the remaining buttons if not already added
        if row_layout.count() > 0:
            self.items_layout.addLayout(row_layout)
    def add_item(self, name, price):
        if name in self.orders:
            self.orders[name]["quantity"] += 1
        else:
            self.orders[name] = {"price": price, "quantity": 1}
        
        self.update_orders_table()
        self.update_total()


    def remove_item(self):
        selected_items = self.orders_table.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            row = item.row()
            col = item.column()
            item_name = self.orders_table.item(row, 0).text()
            if self.orders[item_name]["quantity"] > 1:
                self.orders[item_name]["quantity"] -= 1
            else:
                del self.orders[item_name]
            self.update_orders_table()
            self.update_total()

    def update_total(self):
        total = sum(order["price"] * order["quantity"] for order in self.orders.values())
        total -= self.discount
        total += self.delivery_fees
        self.total_value_label.setText(f"{total:.2f}")
        self.total_value_label.setStyleSheet("color: red;")
        

    def update_orders_table(self):
        self.orders_table.setRowCount(len(self.orders))
        # table.resizeColumnsToContents()
        self.orders_table.resizeRowsToContents()
        header = self.orders_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents) 
        row = 0
        for item_name, order in self.orders.items():
            price = order["price"]
            quantity = order["quantity"]
            total = int(price) * int(quantity)
            
            # Set font size and bold formatting
            font = QFont()
            font.setBold(True)
            font.setPointSize(16)  # Adjust the font size as desired
            # Set item values
            item_name_item = QTableWidgetItem(item_name)
            price_item = QTableWidgetItem(f"{price:.2f}")
            quantity_item = QTableWidgetItem(str(quantity))
            total_item = QTableWidgetItem(f"{total:.2f}")
            note_edit = QLineEdit()
            note_edit.setFont(font)
            note_edit.setStyleSheet("background-color: yellow;")            
            
            item_name_item.setFont(font)
            price_item.setFont(font)
            quantity_item.setFont(font)
            total_item.setFont(font)

            # Set items in the table
            self.orders_table.setItem(row, 0, item_name_item)
            self.orders_table.setItem(row, 1, price_item)
            self.orders_table.setItem(row, 2, quantity_item)
            self.orders_table.setItem(row, 3, total_item)
            self.orders_table.setCellWidget(row, 4, note_edit)
            # Set background color for the entire row
            for col in range(self.orders_table.columnCount()):
                cell_item = self.orders_table.item(row, col)
                if cell_item is not None:
                    cell_item.setBackground(QColor(173, 216, 230))
            self.note_edits[item_name] = note_edit
            row += 1  

    def load_history_data(self, table, id, orders_history = False, bills_history= False):
        conn, cursor = self.connect()
        if orders_history == True:
            df = pd.read_sql_query(f"SELECT o.order_date ,o.bill_id, i.Item_name, i.Item_price, o.quantity, o.total_price, o.note FROM orders as o left join items as i on i.Item_id == o.product_id where o.customer_id = '{id}' order by o.order_date DESC", conn)
        if bills_history == True:
            df = pd.read_sql_query(f"""SELECT b.date, b.bill_id, sum(o.total_price), b.deliver_fees, b.discount, b.bill_net , b.deposite , b.remaining_money, b.bill_note From bills as b 
            left join orders as o on o.bill_id = b.bill_id where b.customer_id = {id}  
            GROUP BY b.date, b.bill_id , b.deliver_fees, b.discount, b.bill_net, b.deposite, b.remaining_money
            order by b.remaining_money DESC , b.date DESC""", conn)
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
            if bills_history == True:
                # Set the font and text color for column 6
                font_special = QFont("Arial", 12, QFont.Bold)
                item = QTableWidgetItem(str(df.iloc[row, 7]))
                item.setFont(font_special)
                item.setBackground(QColor(173, 216, 230))
                if int(item.text()) > 0:
                    item.setForeground(QColor("red"))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 7, item)
            elif orders_history == True:
                font_special = QFont("Arial", 12, QFont.Bold)
                item = QTableWidgetItem(str(df.iloc[row, 5]))
                item.setFont(font_special)
                item.setForeground(QColor("blue"))
                item.setBackground(QColor(173, 216, 230))
                item.setTextAlignment(Qt.AlignCenter)
                table.setItem(row, 5, item)
        
            
        # table.resizeColumnsToContents()
        table.resizeRowsToContents()
        header = table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)    

        # close the database connection
        conn.close()

        
    def permission(self):
        password_dialog = QInputDialog()
        password_dialog.setWindowTitle("Take Permission")
        password_dialog.setInputMode(QInputDialog.TextInput)
        password_dialog.setLabelText("Please enter the admin password:")
        password_dialog.setTextEchoMode(QLineEdit.Password)
        ok = password_dialog.exec_()
        password = password_dialog.textValue()
        conn, cursor = self.connect()
        try:
            cursor.execute("select password from users where authorization = 'admin'")
        except sqlite3.Error as error:
            print(error)
        correct_passwords = cursor.fetchall()[0]
        if password in correct_passwords:
            return ok , password
        else:
            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Critical)
            message_box.setWindowTitle("Warming!!")
            message_box.setText("The Password Is Not Correct!!")
            message_box.setStandardButtons(QMessageBox.Ok)
            message_box.exec_()
            return None , None
    def new_order(self):
        conn, cursor = self.connect()
        # Retrieve customer information
        bill_number = self.Bill_number
        customer_name  = self.name_line_edit.text().strip()
        customer_phone  = self.phone_line_edit.text().strip()
        customer_address  = self.address_line_edit.text().strip()
        other_phones = self.other_phones_line_edit.text().strip()
        discount = self.discount
        delivery_fees =self.delivery_line_edit.text()
        bill_note = self.order_note_edit.text().strip()
        orders = self.orders.items()
        deposit_value = self.deposit_amount.text().strip()
        net_total = self.total_value_label.text().strip()
        
        if not customer_name:
            QMessageBox.warning(self, "Customer Name", "Please Insert customer Name")  
        elif self.customer_data == {}:
            QMessageBox.warning(self, "Customer Data", "Please Add The customer Information to the Database")
        elif self.orders == {}:
            QMessageBox.warning(self, "Orders Can't Be Null", "Please Add An Item At least")    
        elif not deposit_value:
            QMessageBox.warning(self, "Deposit Can't Be Null", "Please Add Any Deposit '0' is acceptable")
            
        else:    
            customer_id = self.customer_data[customer_name][3]
            remaining_money = float(net_total) - float(deposit_value)
            
            # print(bill_number, customer_name, customer_phone, customer_address, other_phones, discount, delivery_fees, order_note)
            
            # print(self.orders)
            # checking missing ingredients
            missing_ingredients = []
            insufficient_ingredients = []
            for item_name, order in self.orders.items():
                try:
                    product_id = cursor.execute("SELECT Item_id FROM items WHERE Item_name = ?", (item_name,)).fetchone()[0]
                except sqlite3.Error as error:
                    print(error)
                quantity = order["quantity"]
                try:
                    cursor.execute("SELECT Ingred_id, Ingred_amount FROM item_ingredients WHERE Item_id = ?", (product_id,))
                except sqlite3.Error as error:
                    print(error)
                ingredients = cursor.fetchall()
                # print(ingredients)
                for ingredient_id, ingredient_amount in ingredients:
                    try:
                        cursor.execute("SELECT i.Ingred_name, v.Ingrident_count FROM ingredients as i INNER JOIN Inventory as v ON i.Ingredients_id = v.Ingriednt_id WHERE v.Ingriednt_id = ?", (ingredient_id,))
                    except sqlite3.Error as error:
                        print(error)
                    result = cursor.fetchone()
                    
                    if result is not None:
                        ingredient_name, current_count = result
                        # print(ingredient_name, current_count)
                        
                        if current_count >= ingredient_amount * quantity:
                            continue
                        else:
                            # print("Not enough",ingredient_name, current_count , ingredient_amount * quantity)
                            insufficient_ingredients.append(ingredient_name)
                    else:
                        # print(ingredient_id)
                        try:
                            cursor.execute("SELECT Ingred_name FROM ingredients WHERE Ingredients_id = ?", (ingredient_id,))
                        except sqlite3.Error as error:
                            print(error)
                        not_exist_ingredient = cursor.fetchone()[0]
                        # print("not exsit",not_exist_ingredient)
                        missing_ingredients.append(not_exist_ingredient)
            conn.close()
            
            if missing_ingredients or insufficient_ingredients:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                message = ""
                if missing_ingredients:
                    message += "The following ingredients are not available in the Inventory: " + ", ".join(np.unique(missing_ingredients).tolist()) + "\n"
                if insufficient_ingredients:
                    message += "The following ingredients do not have enough quantity in the Inventory: " + ", ".join(np.unique(insufficient_ingredients).tolist())
                msg.setText(message)
                msg.setWindowTitle("Warning")
                msg.exec_()
                return  # Abort the order submission
            
            # Perform necessary actions for creating a new order using the provided customer information
            
            try:
                conn, cursor = self.connect()
                for item_name, order in self.orders.items():
                    try:
                        product_id = cursor.execute("SELECT Item_id FROM items WHERE Item_name = ?", (item_name,)).fetchone()[0]
                        quantity = order["quantity"]
                        price = order["price"]
                        total_price = price * quantity
                        note_edit_widget = self.note_edits[item_name]
                        note_text = note_edit_widget.text()
                        cursor.execute("insert into orders (bill_id, customer_id, product_id, quantity, total_price, note) values (?,?,?,?,?,?)", (bill_number,customer_id,product_id, quantity, total_price , note_text) )
                        conn.commit()
                        cursor.execute("SELECT Ingred_id, Ingred_amount FROM item_ingredients WHERE Item_id = ?", (product_id,))
                        ingredients = cursor.fetchall()
                    except sqlite3.Error as error:
                        print(error)
                
                    for ingredient_id, ingredient_amount in ingredients:
                        try:
                            cursor.execute("UPDATE Inventory SET Ingrident_count = Ingrident_count - ? WHERE Ingriednt_id = ?", (ingredient_amount * quantity, ingredient_id))
                            conn.commit()
                            
                        except sqlite3.Error as error:
                            print(error)
                conn.close()
                try:
                    conn, cursor = self.connect()
                    cursor.execute("INSERT INTO bills (bill_id, customer_id, discount, deliver_fees, bill_net, deposite, remaining_money, bill_note) values(?,?,?,?,?,?,?,?)",
                (bill_number, customer_id,discount,delivery_fees,net_total, deposit_value, remaining_money , bill_note))
                
                    conn.commit()
                    
                except sqlite3.Error as error:
                    print(error)
                self.print_bill(bill_number=bill_number)
            except sqlite3.Error as error:
                print(error)
            conn.close()
            
            


            # Clear the customer information fields
            self.name_line_edit.clear()
            self.phone_line_edit.clear()
            self.address_line_edit.clear()
            self.other_phones_line_edit.clear()
            self.discount_line_edit.clear()
            self.delivery_line_edit.clear()
            self.order_note_edit.clear()
            self.discount = 0.0
            self.delivery_fees = 0.0
            self.orders = {}
            self.update_orders_table()
            self.update_total()
            self.deposit_amount.clear()
            # Clear the orders table
            self.orders_table.clearContents()
            self.orders_table.setRowCount(0)
            self.orders_history_table.clearContents()
            self.orders_history_table.setRowCount(0)
            self.bills_history_table.clearContents()
            self.bills_history_table.setRowCount(0)
            self.customer_data = {}
            conn, cursor = self.connect()
            items_data = pd.read_sql_query("SELECT * FROM items", conn)
            try:
                cursor.execute("SELECT DISTINCT Name, Phone, Address, Phone2 FROM customers")
            except sqlite3.Error as error:
                print(error)
            names = [name[0] for name in cursor.fetchall()]
            completer = QCompleter(names)
            self.name_line_edit.setCompleter(completer)
            try:
                cursor.execute("select bill_id from orders ORDER BY order_date DESC, bill_id DESC LIMIT 1")
            except sqlite3.Error as error:
                print(error)
            last_record = cursor.fetchone()        
            if last_record == None: 
                self.Bill_number = 1
            else:
                self.Bill_number = last_record[0] + 1
            
            conn.close()
            self.bill_value.setText(str(self.Bill_number))
            self.data = items_data
            


    def print_bill(self, bill_number):
        conn, cursor = self.connect()
        
        # Retrieve the necessary data for the bill
        try:
            cursor.execute("SELECT c.Name, c.Phone, c.Address, b.discount, b.deliver_fees, b.bill_net, "
                    "b.deposite, b.remaining_money, o.product_id, o.quantity, o.total_price, o.note, "
                    "i.Item_name, i.Item_price, b.bill_note "
                    "FROM orders AS o "
                    "INNER JOIN customers AS c ON o.customer_id = c.ID "
                    "INNER JOIN items AS i ON o.product_id = i.Item_id "
                    "INNER JOIN bills AS b ON o.bill_id = b.bill_id "
                    "WHERE o.bill_id = ?", (bill_number,))
        except sqlite3.Error as error:
                print(error)
        bill_data = cursor.fetchall()
        

        if bill_data:
            customer_name, customer_phone, customer_address, discount, delivery_fees, bill_net, deposit, remaining_money, product_id, quantity, total_price, note, item_name, item_price, bill_notes = bill_data[0]

            # Prepare the bill content
            
            bill_content = f'''
            <!DOCTYPE html>
            <html>
            <head>
            <style>
            body {{
                background-color: white;
            }}

            .container {{
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
            }}

            table {{
                margin: 0 auto; /* Center the table horizontally */
                border-collapse: collapse;
            }}

            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}

            th {{
                background-color: #f2f2f2;
            }}
            </style>
            </head>
            <body>
            <div class="container">
                <div>
                    <h2 style="text-align: center;">Bill Number: {bill_number}</h2>
                    <p style="text-align: center;">Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <h3>Customer Name: {customer_name}</h3>
                    <p>Phone: {customer_phone}</p>
                    <p>Address: {customer_address}</p>
                    <hr>
                    <table>
                        <tr><th>Item</th><th>Quantity</th><th>Price</th><th>Total</th><th>Note</th></tr>
            '''

            for row in bill_data:
                _, _, _, _, _, _, _, _, product_id, quantity, total_price, note, item_name, item_price, bill_notes = row
                bill_content += f"<tr><td>{item_name}</td><td>{quantity}</td><td>{item_price}</td><td>{total_price}</td><td>{note}</td></tr>"

            bill_content += f'''
                    </table>
                    <p>&nbsp;</p> <!-- Add an empty paragraph for the line -->
                    <hr>
                    <p>Discount: {discount}</p>
                    <p>Delivery Fees: {delivery_fees}</p>
                    <p>Net Total: {bill_net}</p>
                    <p>Deposit: {deposit}</p>
                    <p>Remaining Money: {remaining_money}</p>
                    <p>Bill Note: {bill_notes}</p>
                </div>
            </div>
            </body>
            </html>
            '''


            # Create a QTextDocument with the bill content
            document = QTextDocument()
            document.setHtml(bill_content)

            # Create a QPrinter and configure it
            printer = QPrinter(QPrinter.HighResolution)
            # printer.setPageSize(QPrinter.A4)
            printer.setPageSize(QPrinter.Custom)
            printer.setPaperSize(QSizeF(80, 297), QPrinter.Millimeter)

            printer.setOrientation(QPrinter.Portrait)

            # Create a QPrintDialog and check if the user accepted the dialog
            print_dialog = QPrintDialog(printer, self)
            if print_dialog.exec_() == QPrintDialog.Accepted:
                # Print the QTextDocument
                document.print_(printer)
        else:
            print("No bill found for the provided bill number.")

        conn.close()


