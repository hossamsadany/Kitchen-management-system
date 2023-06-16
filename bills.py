from PyQt5.QtWidgets import QWidget,QScrollArea,QCompleter, QHBoxLayout, QVBoxLayout,QLineEdit, QDateEdit, QPushButton, QLabel, QTableWidgetItem, QHeaderView, QTableWidget
from PyQt5.QtCore import  Qt, pyqtSlot, QDate, QRect, QRegExp, QSizeF
from PyQt5.QtGui import QFont, QColor, QValidator, QRegExpValidator, QTextDocument, QPainter, QImage
import sqlite3
import pandas as pd
from PyQt5.QtWidgets import QMessageBox
from datetime import datetime
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter


class BillsTabWidgt(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("background-color: grey; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # Create a scroll area and set its widget resizable
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        # Create a widget to hold the main content
        content_widget = QWidget()

        # Set up the main layout for the content widget
        self.bills_layout = QVBoxLayout(content_widget)
        self.bills_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        self.bills_layout.setSpacing(10)
       
        # create date widgets
        start_date_label = QLabel(self)
        start_date_label.setText("Start Date")
        start_date_label.setGeometry(QRect(1000, 60, 120, 25))
        start_date_label.setFont(QFont("Arial", 12, QFont.Bold))


        end_date_label = QLabel(self)
        end_date_label.setText("End Date")
        # end_date_label.setAlignment(Qt.AlignRight)
        end_date_label.setGeometry(QRect(1150, 60, 120, 25))
        end_date_label.setFont(QFont("Arial", 12, QFont.Bold))  

        self.start_date_edit = QDateEdit(QDate.currentDate().addDays(1 - QDate.currentDate().day()), self)
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setGeometry(1050, 80, 120, 25)

        self.end_date_edit = QDateEdit(QDate.currentDate().addDays(QDate.currentDate().daysInMonth() - QDate.currentDate().day()), self)
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setGeometry(1200, 80, 120, 25)

        date_layout = QHBoxLayout()
        date_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Align buttons to top center
        date_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        date_layout.setSpacing(10)
        date_layout.addWidget(start_date_label)
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(end_date_label)
        date_layout.addWidget(self.end_date_edit)
        self.bills_layout.addLayout(date_layout)
        # Create buttons for viewing bills
        view_all_bills_button = QPushButton("View All Bills")
        view_all_bills_button.setFixedWidth(250)
        view_all_bills_button.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")

        view_incomplete_bills_button = QPushButton("View Incomplete Bills")
        view_incomplete_bills_button.setFixedWidth(250)
        view_incomplete_bills_button.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # Create the update button
        self.update_button = QPushButton("Update Bills")
        self.update_button.setStyleSheet("background-color: green;")

        # self.update_button.setFixedWidth(250)
        # self.update_button.setStyleSheet("background-color: green; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # Create a horizontal layout for the buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)  # Align buttons to top center
        buttons_layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        buttons_layout.setSpacing(10)  # Remove spacing between buttons
        buttons_layout.addWidget(view_all_bills_button)
        buttons_layout.addWidget(view_incomplete_bills_button)
        # buttons_layout.addWidget(self.update_button)

        # Create a container widget for the buttons layout
        buttons_container = QWidget()
        buttons_container.setStyleSheet("background-color: rgba(0, 0, 0, 0);")  # Set transparent background for the container
        buttons_container.setLayout(buttons_layout)

        # Add the buttons container to the bills layout
        self.bills_layout.addWidget(buttons_container)

        

        # Create labels and input fields
        conn , cursor = self.connect()
        cursor.execute("SELECT DISTINCT Name, Phone, Address, Phone2  FROM customers")
        names = [name[0] for name in cursor.fetchall()]
        conn.close()
        completer = QCompleter(names)
        name_label = QLabel("Name:")
        self.name_line_edit = QLineEdit()
        name_validator = QRegExpValidator(QRegExp("[a-zA-Z\u0600-\u06FF\s/]+"), self.name_line_edit)
        self.name_line_edit.setValidator(name_validator)
        self.name_line_edit.setCompleter(completer)
        self.name_line_edit.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # Connect the name_line_edit textChanged signal to a slot
        self.name_line_edit.returnPressed.connect(self.check_customer_info)
        bill_number_label = QLabel("Bill Number:")
        self.bill_number_input = QLineEdit()
        self.bill_number_input.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # self.bill_number_input.returnPressed.connect(self.check_customer_info)
        customer_info_label = QLabel("Customer Information:")
        self.customer_info_label = QLabel()
        self.customer_info_label.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        unpaid_bills_label = QLabel("Unpaid Bills:")
        self.unpaid_bills_label = QLabel()
        self.unpaid_bills_label.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: red; font-size: 18px; font-weight: bold;")
        
        payed_amount_label = QLabel("Payed Amount:")
        self.payed_amount_input = QLineEdit()
        self.payed_amount_input.setStyleSheet("background-color: white; border: 3px solid black; border-radius: 5px; color: black; font-size: 18px; font-weight: bold;")
        # Set input field validation
        bill_number_validator = QRegExpValidator(QRegExp("^[1-9]\d*"), self.bill_number_input)
        self.bill_number_input.setValidator(bill_number_validator)
        pay_amount_validator = QRegExpValidator(QRegExp("^[1-9]\d*(\.\d{1,3})?$"), self.payed_amount_input)
        self.payed_amount_input.setValidator(pay_amount_validator)
        self.print_bill_button = QPushButton("Print Bills")
        # self.print_bill_button.setFont(font)
        self.print_bill_button.setStyleSheet("background-color: blue;")
        
        

        # Create layout for the input fields and labels
        input_layout = QVBoxLayout()
        input_layout.addWidget(name_label)
        input_layout.addWidget(self.name_line_edit)
        input_layout.addWidget(customer_info_label)
        input_layout.addWidget(self.customer_info_label)
        input_layout.addWidget(unpaid_bills_label)
        input_layout.addWidget(self.unpaid_bills_label)
        input_layout.addWidget(bill_number_label)
        input_layout.addWidget(self.bill_number_input)
        input_layout.addWidget(payed_amount_label)
        input_layout.addWidget(self.payed_amount_input)
        input_layout.addWidget(self.update_button)
        input_layout.addWidget(self.print_bill_button)
        
        
        # Create a container widget for the input layout
        input_container = QWidget()
        input_container.setLayout(input_layout)
        
        # Add the input container to the main layout
        self.bills_layout.addWidget(input_container)
        
        
        headers = ["Bill Number", "Customer Name", "Total Bill", "Discount", "Delivery fees", "Bill Net", "Deposit", "Remaining Amount"]
        # Create and load the all_bills_table
        self.all_bills_table = self.create_table(headers=headers)

        # Add the table widget to the bills tab layout
        title_label = QLabel("All Bills Table")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bills_layout.addWidget(title_label)
        self.bills_layout.addWidget(self.all_bills_table)

        incompelte_headers = ["Bill Number", "Customer Name", "Total Bill", "Discount", "Delivery fees", "Bill Net", "Deposit", "Remaining Amount"]
        # Create and load the all_bills_table
        self.incompelete_bills_table = self.create_table(headers=incompelte_headers)

        # Add the table widget to the bills tab layout
        title_label = QLabel("Incompelete Bills Table")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.bills_layout.addWidget(title_label)
        self.bills_layout.addWidget(self.incompelete_bills_table)
        # Add the content widget to the scroll area
        scroll_area.setWidget(content_widget)

        # Set the scroll area as the main layout of the widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

        # Connect the buttons to their respective functions
        view_all_bills_button.clicked.connect(lambda _, table=self.all_bills_table,sql_table=None, all_bills=True : self.load_data(table=table, sql_table=sql_table, all_bills=all_bills) )
        view_incomplete_bills_button.clicked.connect((lambda _, table=self.incompelete_bills_table,sql_table=None,  incomplete_bills=True : self.load_data(table=table, sql_table=sql_table, incomplete_bills=incomplete_bills) ))
        self.update_button.clicked.connect(self.update_bills)
        self.update_button.clicked.connect(self.check_customer_info)
        self.update_button.clicked.connect(lambda _, table=self.all_bills_table,sql_table=None, all_bills=True : self.load_data(table=table, sql_table=sql_table, all_bills=all_bills) )
        self.update_button.clicked.connect(lambda _, table=self.incompelete_bills_table,sql_table=None,  incomplete_bills=True : self.load_data(table=table, sql_table=sql_table, incomplete_bills=incomplete_bills))
        self.print_bill_button.clicked.connect(self.print_bill)
    def check_customer_info(self):
        customer_name = self.name_line_edit.text()
        # Retrieve customer information and unpaid bills from the database based on the bill number
        conn, cursor = self.connect()
        cursor.execute("SELECT * FROM customers WHERE Id IN (SELECT customer_id FROM bills WHERE Name = ?)", (customer_name,))
        customer_info = cursor.fetchone()
        
        conn.close()
        # Display customer information
        if customer_info:
            conn, cursor = self.connect()
            cursor.execute("SELECT * FROM bills WHERE customer_id = ? AND remaining_money > 0", (customer_info[0],))
            unpaid_bills = cursor.fetchall()
            conn.close()
            customer_name = customer_info[1]
            customer_phone = customer_info[2]
            self.customer_info_label.setText(f"Customer Name: {customer_name}\nPhone: {customer_phone}")
            # Display unpaid bills
            if unpaid_bills:
                unpaid_bills_text = "\n"
                for bill in unpaid_bills:
                    unpaid_bills_text += f"Bill ID: {bill[1]}, Total Deposit: {bill[7]} , Last Deposit Date: {bill[2]}, Remaining Money: {bill[8]}\n"
                self.unpaid_bills_label.setText(unpaid_bills_text)
                
            else:
                self.unpaid_bills_label.setText("No unpaid bills.")
        else:
            self.customer_info_label.setText("Customer not found.")
        

    
    def update_bills(self):
        
        if self.bill_number_input.text() and self.payed_amount_input.text():
            bill_number = self.bill_number_input.text()
            # Update the paid amount in the database
            payed_amount = float(self.payed_amount_input.text())
            conn, cursor = self.connect()
            cursor.execute("UPDATE bills SET remaining_money = remaining_money - ? WHERE bill_id = ?", (payed_amount, bill_number))
            cursor.execute("UPDATE bills SET deposite = deposite + ? WHERE bill_id = ?", (payed_amount, bill_number))
            cursor.execute("UPDATE bills set date = current_date where bill_id = ?", (bill_number,))
            conn.commit()
            conn.close()
            QMessageBox.information(self, "Successeful Transaction", f"You just Deposit {payed_amount} to Bill number {bill_number}")
        else:
            QMessageBox.warning(self,"Invalid Info", "Bill Number or payed_amount is missing!")

    def load_data(self,table, sql_table , all_bills= False, incomplete_bills= False):
        conn, cursor = self.connect()
        start = self.start_date_edit.date().toString("yyyy-MM-dd")
        end = self.end_date_edit.date().toString("yyyy-MM-dd")
        if all_bills == True:
           df = pd.read_sql_query(f"""
                SELECT DISTINCT b.bill_id, c.Name, SUM(o.total_price) AS total_price, b.discount,
                    b.deliver_fees, b.bill_net, b.deposite, b.remaining_money
                FROM bills AS b
                LEFT JOIN customers AS c ON b.customer_id = c.id
                LEFT JOIN orders AS o ON o.bill_id = b.bill_id
                Where b.date between '{start}' and '{end}'
                GROUP BY b.bill_id, c.Name, b.discount, b.deliver_fees, b.bill_net, b.deposite, b.remaining_money
            """, conn)
        elif incomplete_bills == True:
            df = pd.read_sql_query(f"""
                SELECT DISTINCT b.bill_id, c.Name, SUM(o.total_price) AS total_price, b.discount,
                    b.deliver_fees, b.bill_net, b.deposite, b.remaining_money
                FROM bills AS b
                LEFT JOIN customers AS c ON b.customer_id = c.id
                LEFT JOIN orders AS o ON o.bill_id = b.bill_id
                where b.remaining_money > 0 and b.date between '{start}' and '{end}'
                GROUP BY b.bill_id, c.Name, b.discount, b.deliver_fees, b.bill_net, b.deposite, b.remaining_money
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
    def print_bill(self):
        bill_number = self.bill_number_input.text()
        if bill_number:
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
                QMessageBoc.warning(self, "Ambigouse Bill","No bill found for the provided bill number.")

            conn.close()
        else:
            QMessageBox.warning(self, "Ambiguouse Bill", "Please Insert a Bill Number")
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