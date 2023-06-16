import os
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QPushButton, QLabel, QDateEdit, QHBoxLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSlot, QDate, QRect
import matplotlib.pyplot as plt
import sqlite3
import numpy as np



class AnalysisTabWidget(QWidget):
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

        # Add the scroll area to the analysis tab layout
        self.layout.addWidget(self.scroll_area)
        
        # Create a refresh button
        self.refresh_button = QPushButton("Refresh Analysis")
        self.layout.addWidget(self.refresh_button)

        # Connect the clicked signal of the refresh button to the update_analysis slot
        self.refresh_button.clicked.connect(self.update_analysis)

          # create date widgets
        start_date_label = QLabel(self)
        start_date_label.setText("Start Date")
        # start_date_label.setAlignment(Qt.AlignRight)
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
        
        # Add the date_layout to the scroll_layout
        self.layout.addLayout(date_layout)

        # Add the scroll area to the analysis tab layout
        self.layout.addWidget(self.scroll_area)
        self.update_analysis()


        
    def connect(self):
        try:
            conn = sqlite3.connect("restaurant_database.db")
            cursor = conn.cursor()
            return conn, cursor
        except sqlite3.Error as error:
            QMessageBox.warning(form, "Warning", error)

    @pyqtSlot()
    def update_analysis(self):
        # Check if the database connection is already established
        connection, cursor = self.connect()
        
        # Retrieve the selected start and end dates
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()

        # Clear the previous analysis content
        for i in reversed(range(self.scroll_layout.count())):
            item = self.scroll_layout.itemAt(i)
            self.scroll_layout.removeItem(item)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            # item.widget().setParent(None)
        # Examples
        # Example 1: Total Sales by Date
        # Example: Lovely Items
        # Analyze the top-selling items
        top_selling_items_query = f"""
           SELECT 
            i.Item_id,
            i.Item_name,
            SUM(o.quantity) AS Total_Sales
        FROM
            items AS i
        LEFT JOIN orders AS o ON i.Item_id = o.product_id
        WHERE o.order_date >= '{start_date}' AND o.order_date <= '{end_date}'
        GROUP BY
            i.Item_id,
            i.Item_name
        ORDER BY
            Total_Sales DESC
        LIMIT 10;

        """

        cursor.execute(top_selling_items_query)
        top_selling_items_result = cursor.fetchall()

        top_selling_items = [row[1] for row in top_selling_items_result]
        total_sales = [row[2] for row in top_selling_items_result]

        plt.figure()
        plt.bar(top_selling_items, total_sales)
        plt.xlabel('Items')
        plt.ylabel('Total Sales')
        plt.title('Top Selling Items')
        plt.xticks(rotation=45)
        plt.tight_layout()
        top_selling_items_image_path = "top_selling_items.png"
        plt.savefig(top_selling_items_image_path)
        plt.close()

        top_selling_items_label = QLabel()
        top_selling_items_pixmap = QPixmap(top_selling_items_image_path)
        top_selling_items_label.setPixmap(top_selling_items_pixmap)
        top_selling_items_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(top_selling_items_label)

        # ...

        # Example: Lovely Ingredients
        lovely_ingredients_query = """
            SELECT ingredients.ingred_name, SUM(orders.quantity) AS total_quantity
            FROM orders
            INNER JOIN items ON orders.product_id = items.Item_id
            INNER JOIN item_ingredients ON items.Item_id = item_ingredients.Item_id
            INNER JOIN ingredients ON item_ingredients.Ingred_id = ingredients.Ingredients_id
            WHERE orders.order_date BETWEEN ? AND ?
            GROUP BY ingredients.ingred_name
            ORDER BY total_quantity DESC
            LIMIT 10
        """
        cursor.execute(lovely_ingredients_query, (start_date, end_date))
        lovely_ingredients_result = cursor.fetchall()

        ingredient_names = [row[0] for row in lovely_ingredients_result]
        total_quantity = [row[1] for row in lovely_ingredients_result]

        # Plot the data
        plt.figure()
        plt.bar(ingredient_names, total_quantity, color='lightgreen')
        plt.ylabel("Total Quantity")
        plt.xlabel("Ingredient Name")
        plt.title("Top Selling Ingredients")
        plt.tight_layout()
        lovely_ingredients_image = plt.gcf()
        plt.close()

        # Save the figure as an image
        lovely_ingredients_image_path = "lovely_ingredients.png"
        lovely_ingredients_image.savefig(lovely_ingredients_image_path)

        lovely_ingredients_label = QLabel()
        lovely_ingredients_pixmap = QPixmap(lovely_ingredients_image_path)
        lovely_ingredients_label.setPixmap(lovely_ingredients_pixmap)
        lovely_ingredients_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(lovely_ingredients_label)

        # ...
        # Example: Purchased Ingredients
        purchases_query = """
            SELECT Ingrident_name, sum(Ingrident_count)
            FROM purchases
            WHERE Entry_date BETWEEN ? AND ?
            Group by Ingrident_name
            limit 10
        """
        cursor.execute(purchases_query, (start_date, end_date))
        purchases_result = cursor.fetchall()

        ingredient_names = [row[0] for row in purchases_result]
        ingredient_counts = [row[1] for row in purchases_result]

        # Plot the data
        plt.figure()
        plt.bar(ingredient_names, ingredient_counts, color='orange')
        plt.xlabel("Ingredient")
        plt.ylabel("Quantity")
        plt.title("Purchased Ingredients")
        plt.xticks(rotation='vertical')
        plt.tight_layout()
        purchased_ingredients_image = plt.gcf()
        plt.close()

        # Save the figure as an image
        purchased_ingredients_image_path = "purchased_ingredients.png"
        purchased_ingredients_image.savefig(purchased_ingredients_image_path)

        purchased_ingredients_label = QLabel()
        purchased_ingredients_pixmap = QPixmap(purchased_ingredients_image_path)
        purchased_ingredients_label.setPixmap(purchased_ingredients_pixmap)
        purchased_ingredients_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(purchased_ingredients_label)

       

        # ...

        # Example: Most Common Customers
        common_customers_query = """
            SELECT customers.Name, COUNT(*) AS num_orders
            FROM orders
            INNER JOIN customers ON orders.customer_id = customers.Id
            WHERE orders.order_date BETWEEN ? AND ?
            GROUP BY customers.Name
            ORDER BY num_orders DESC
            LIMIT 5
        """
        cursor.execute(common_customers_query, (start_date, end_date))
        common_customers_result = cursor.fetchall()

        customer_names = [row[0] for row in common_customers_result]
        num_orders = [row[1] for row in common_customers_result]

        # Plot the data
        plt.figure()
        plt.bar(customer_names, num_orders, color='pink')
        plt.xlabel("Customer Name")
        plt.ylabel("Number of Orders")
        plt.title("Top Common Customers")
        plt.tight_layout()
        common_customers_image = plt.gcf()
        plt.close()

        # Save the figure as an image
        common_customers_image_path = "common_customers.png"
        common_customers_image.savefig(common_customers_image_path)

        common_customers_label = QLabel()
        common_customers_pixmap = QPixmap(common_customers_image_path)
        common_customers_label.setPixmap(common_customers_pixmap)
        common_customers_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(common_customers_label)

        # ...

        # Example: Item Preference by Customers
        item_preference_query = """
            SELECT customers.Name, items.item_name, COUNT(*) AS num_orders
            FROM orders
            INNER JOIN customers ON orders.customer_id = customers.Id
            INNER JOIN items ON orders.product_id = items.Item_id
            WHERE orders.order_date BETWEEN ? AND ?
            GROUP BY customers.Name, items.item_name
        """
        cursor.execute(item_preference_query, (start_date, end_date))
        item_preference_result = cursor.fetchall()

        customer_names = list(set([row[0] for row in item_preference_result]))
        item_names = list(set([row[1] for row in item_preference_result]))

        # Create a dictionary to store the number of orders for each customer and item
        num_orders_dict = {}
        for row in item_preference_result:
            customer_name = row[0]
            item_name = row[1]
            num_orders = row[2]
            if customer_name not in num_orders_dict:
                num_orders_dict[customer_name] = {}
            num_orders_dict[customer_name][item_name] = num_orders

        # Prepare the data for plotting
        num_customers = len(customer_names)
        item_counts = np.zeros((num_customers, len(item_names)))
        for i, customer_name in enumerate(customer_names):
            if customer_name in num_orders_dict:
                customer_orders = num_orders_dict[customer_name]
                for j, item_name in enumerate(item_names):
                    if item_name in customer_orders:
                        item_counts[i][j] = customer_orders[item_name]

        # Plot the data
        plt.figure(figsize=(10, 6))
        bottom = np.zeros(num_customers)
        colors = plt.cm.get_cmap('tab20c', len(item_names))

        for j, item_name in enumerate(item_names):
            plt.bar(customer_names, item_counts[:, j], bottom=bottom, label=item_name, color=colors(j))
            bottom += item_counts[:, j]

        plt.xlabel("Customer Name")
        plt.ylabel("Number of Orders")
        plt.title("Item Preference by Customers")
        plt.legend(title="Item Name", loc="upper right")
        plt.xticks(rotation=90)
        plt.tight_layout()
        item_preference_image = plt.gcf()
        plt.close()

        # Save the figure as an image
        item_preference_image_path = "item_preference.png"
        item_preference_image.savefig(item_preference_image_path)

        item_preference_label = QLabel()
        item_preference_pixmap = QPixmap(item_preference_image_path)
        item_preference_label.setPixmap(item_preference_pixmap)
        item_preference_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(item_preference_label)

        sales_by_date_query = """
            SELECT order_date, SUM(total_price) AS total_sales
            FROM orders
            WHERE order_date BETWEEN ? AND ?
            GROUP BY order_date
            ORDER BY order_date
        """
        cursor.execute(sales_by_date_query, (start_date, end_date))
        sales_by_date_result = cursor.fetchall()

        dates = [row[0] for row in sales_by_date_result]
        total_sales = [row[1] for row in sales_by_date_result]

        plt.figure()
        plt.plot(dates, total_sales)
        plt.xlabel("Date")
        plt.ylabel("Total Sales")
        plt.title("Total Sales by Date")
        plt.xticks(rotation=45)
        plt.tight_layout()
        sales_by_date_image = plt.gcf()
        plt.close()

        # Save the figure as an image
        sales_by_date_image_path = "sales_by_date.png"
        sales_by_date_image.savefig(sales_by_date_image_path)

        sales_by_date_label = QLabel()
        sales_by_date_pixmap = QPixmap(sales_by_date_image_path)
        sales_by_date_label.setPixmap(sales_by_date_pixmap)
        sales_by_date_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(sales_by_date_label)

        # ...
        # Example 3: Sales by Category
        sales_by_category_query = """
            SELECT item_category, SUM(total_price) AS total_sales
            FROM orders
            INNER JOIN items ON orders.product_id = items.Item_id
            WHERE order_date BETWEEN ? AND ?
            GROUP BY item_category
        """
        cursor.execute(sales_by_category_query, (start_date, end_date))
        sales_by_category_result = cursor.fetchall()

        categories = [row[0] for row in sales_by_category_result]
        total_sales = [row[1] for row in sales_by_category_result]

        plt.figure()

        # Create dummy handles for legend
        handles = []
        for i, category in enumerate(categories):
            handles.append(plt.plot([], [], marker='o', color='C{}'.format(i), label=category)[0])

        plt.pie(total_sales, labels=categories, autopct='%1.1f%%', normalize=False)
        plt.title("Sales by Category")
        plt.tight_layout()

        # Add legend
        plt.legend(handles=handles, title='Categories', loc='best')

        sales_by_category_image = plt.gcf()
        plt.close()
        # Save the figure as an image
        sales_by_category_image_path = "sales_by_category.png"
        sales_by_category_image.savefig(sales_by_category_image_path)

        sales_by_category_label = QLabel()
        sales_by_category_pixmap = QPixmap(sales_by_category_image_path)
        sales_by_category_label.setPixmap(sales_by_category_pixmap)
        sales_by_category_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(sales_by_category_label)

        

        # Calculate the gross profit margin
        gross_profit_margin_query = f"""
            SELECT
            i.Item_id,
            i.Item_name,
            (SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                            FROM item_ingredients AS ii
                                            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                            WHERE ii.Item_id = i.Item_id)) AS Gross_Profit,
            SUM(o.quantity) AS Total_Sales,
            ((SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                                FROM item_ingredients AS ii
                                                JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                                WHERE ii.Item_id = i.Item_id)) / SUM(o.quantity)) * 100 AS Gross_Profit_Margin
        FROM
            items AS i
        LEFT JOIN orders AS o ON i.Item_id = o.product_id
        WHERE o.order_date >= '{start_date}' AND o.order_date <= '{end_date}'
        GROUP BY
            i.Item_id,
            i.Item_name;

        """

        cursor.execute(gross_profit_margin_query)
        gross_profit_margin_result = cursor.fetchall()

        # Calculate the net profit margin
        net_profit_margin_query = f"""
            SELECT
            i.Item_id,
            i.Item_name,
            (SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                            FROM item_ingredients AS ii
                                            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                            WHERE ii.Item_id = i.Item_id)) AS Revenue,
            SUM(o.quantity) AS Total_Sales,
            ((SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                                FROM item_ingredients AS ii
                                                JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                                WHERE ii.Item_id = i.Item_id)) / SUM(o.quantity)) * 100 AS Net_Profit_Margin
        FROM
            items AS i
        LEFT JOIN orders AS o ON i.Item_id = o.product_id
        WHERE o.order_date >= '{start_date}' AND o.order_date <= '{end_date}'
        GROUP BY
            i.Item_id,
            i.Item_name;

        """

        cursor.execute(net_profit_margin_query)
        net_profit_margin_result = cursor.fetchall()

        # Visualize the gross profit margin and net profit margin
        items = [row[1] for row in gross_profit_margin_result]
        gross_profit_margin = [row[4] for row in gross_profit_margin_result]
        net_profit_margin = [row[4] for row in net_profit_margin_result]

        plt.figure()
        plt.plot(items, gross_profit_margin, label='Gross Profit Margin')
        plt.plot(items, net_profit_margin, label='Net Profit Margin')
        plt.xlabel('Items')
        plt.ylabel('Profit Margin (%)')
        plt.title('Profit Margin Analysis')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        profit_margin_image_path = "profit_margin_analysis.png"
        plt.savefig(profit_margin_image_path)
        plt.close()

        profit_margin_label = QLabel()
        profit_margin_pixmap = QPixmap(profit_margin_image_path)
        profit_margin_label.setPixmap(profit_margin_pixmap)
        profit_margin_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(profit_margin_label)

        

        # Analyze the profitability of different item categories
        profitability_by_category_query = f"""
            SELECT 
            i.item_category,
            SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                            FROM item_ingredients AS ii
                                            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                            WHERE ii.Item_id = i.Item_id) AS Profit,
            SUM(i.Item_price * o.quantity) AS Revenue
        FROM
            items AS i
        LEFT JOIN orders AS o ON i.Item_id = o.product_id
        WHERE o.order_date >= '{start_date}' AND o.order_date <= '{end_date}'
        GROUP BY
            i.item_category;

        """

        cursor.execute(profitability_by_category_query)
        profitability_by_category_result = cursor.fetchall()

        categories = [row[0] for row in profitability_by_category_result]
        profits = [row[1] for row in profitability_by_category_result]
        revenues = [row[2] for row in profitability_by_category_result]

        plt.figure()
        plt.bar(categories, profits, label='Profit')
        plt.bar(categories, revenues, label='Revenue')
        plt.xlabel('Item Category')
        plt.ylabel('Amount')
        plt.title('Profitability by Item Category')
        plt.legend()
        plt.xticks(rotation=45)
        plt.tight_layout()
        profitability_by_category_image_path = "profitability_by_category.png"
        plt.savefig(profitability_by_category_image_path)
        plt.close()

        profitability_by_category_label = QLabel()
        profitability_by_category_pixmap = QPixmap(profitability_by_category_image_path)
        profitability_by_category_label.setPixmap(profitability_by_category_pixmap)
        profitability_by_category_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(profitability_by_category_label)

        # Calculate the return on investment (ROI) for each item
        roi_query = f"""
            SELECT 
            i.Item_id,
            i.Item_name,
            (SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                            FROM item_ingredients AS ii
                                            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                            WHERE ii.Item_id = i.Item_id)) AS Revenue,
            (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
            FROM item_ingredients AS ii
            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
            WHERE ii.Item_id = i.Item_id) * SUM(o.quantity) AS Total_Cost,
            ((SUM(i.Item_price * o.quantity) - (SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
                                                FROM item_ingredients AS ii
                                                JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
                                                WHERE ii.Item_id = i.Item_id)) / 
            ((SELECT SUM(ii.Ingred_amount * p.Ingrident_price_per_unit)
            FROM item_ingredients AS ii
            JOIN purchases AS p ON ii.Ingred_id = p.Ingriednt_id
            WHERE ii.Item_id = i.Item_id) * SUM(o.quantity))) * 100 AS ROI
        FROM
            items AS i
        LEFT JOIN orders AS o ON i.Item_id = o.product_id
        WHERE o.order_date >= '{start_date}' AND o.order_date <= '{end_date}'
        GROUP BY
            i.Item_id,
            i.Item_name;

        """

        cursor.execute(roi_query)
        roi_result = cursor.fetchall()

        item_names = [row[1] for row in roi_result]
        roi_values = [row[4] for row in roi_result]

        plt.figure()
        plt.bar(item_names, roi_values)
        plt.xlabel('Item')
        plt.ylabel('ROI (%)')
        plt.title('Return on Investment (ROI) Analysis')
        plt.xticks(rotation=45)
        plt.tight_layout()
        roi_image_path = "roi_analysis.png"
        plt.savefig(roi_image_path)
        plt.close()

        roi_label = QLabel()
        roi_pixmap = QPixmap(roi_image_path)
        roi_label.setPixmap(roi_pixmap)
        roi_label.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(roi_label)

        # Remove the temporary image files
        os.remove(sales_by_date_image_path)
        os.remove(sales_by_category_image_path)
        os.remove(roi_image_path)
        os.remove(top_selling_items_image_path)
        os.remove(lovely_ingredients_image_path)
        os.remove(common_customers_image_path)
        os.remove(profit_margin_image_path)
        os.remove(item_preference_image_path)
        os.remove(purchased_ingredients_image_path)
        os.remove(profitability_by_category_image_path)

        # # Close the database connection
        connection.close()
        