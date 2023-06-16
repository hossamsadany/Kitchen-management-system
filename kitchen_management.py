from PyQt5.QtWidgets import QApplication
from opening import LoginWindow
import sqlite3

admin, password = "hossam", "s3danys"

def create_database():
    # Connect to the database
    conn = sqlite3.connect("restaurant_database.db")
    c = conn.cursor()
    
    # If the users table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS authorization
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    authorization TEXT NOT NULL,
                    validation Text NOT NULL)''')
    c.execute("Select * from authorization")
    check_authorization = c.fetchall()
    if not check_authorization:
    # Add some default users for testing
        c.execute("INSERT INTO authorization (authorization, validation) VALUES (?,?)", ("s3danyshome", "NOT Yet"))
    # Commit the changes to the database
        conn.commit()
    # If the users table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS users
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    authorization TEXT)''')
    conn.commit()
    c.execute("Select * from users")
    check_user = c.fetchall()
    if not check_user:
        # Add some default users for testing
        c.execute("INSERT INTO users (username, password, authorization) VALUES (?, ?,?)", (admin, password, 'admin'))
        # Commit the changes to the database
        conn.commit()
    # Check if the items table exists
    # If the users table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS items
                    (Item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Item_name TEXT NOT NULL,
                    Item_category Text NOT NULL,
                    Item_price NUMERIC(10,3) NOT NULL)''')
    
    # Commit the changes to the database
    conn.commit()
    # Check if the purchases table exists
    # If the purchase table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS purchases
                    (Ingriednt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    Ingrident_name TEXT NOT NULL,
                    Ingrident_price_per_unit NUMERIC(10,3) NOT NULL,
                    Ingrident_count NUMERIC(10,3) NOT NULL,
                    Total_price NUMERIC(10,3) AS  (ingrident_price_per_unit * Ingrident_count) NOT NULL)''')
    
    # Commit the changes to the database
    conn.commit()
    # Check if the Inventory table exists
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS Inventory
                    (id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Ingriednt_id INTEGER NOT NULL,
                    Entry_date DATE NOT NULL DEFAULT CURRENT_DATE,
                    Ingrident_name TEXT NOT NULL,
                    Ingrident_price_per_unit NUMERIC(10,3) NOT NULL,
                    Ingrident_count NUMERIC(10,3) NOT NULL,
                    Total_price NUMERIC(10,3) AS  (ingrident_price_per_unit * Ingrident_count) NOT NULL)''')
    
    # Commit the changes to the database
    conn.commit()
    # Check if the ingredients table exists
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS ingredients
                    (Ingredients_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Ingred_name TEXT NOT NULL)''')
    
    # Commit the changes to the database
    conn.commit()
    
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS item_ingredients
                    (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Item_id INTEGER NOT NULL ,
                    Ingred_id INTEGER NOT NULL,
                    Ingred_amount NUMERIC(10,3) NOT NULL)''')
    
    # Commit the changes to the database
    conn.commit()
    # Check if the orders table exists
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bill_id INTEGER Not NULL,
        customer_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        order_date DATE ,
        quantity INTEGER NOT NULL,
        total_price DECIMAL(10, 2),
        note Text)''')
    c.execute('''CREATE TRIGGER IF NOT EXISTS set_default_created_date
                AFTER INSERT ON orders
                BEGIN
                    UPDATE orders
                    SET order_date = date('now', 'localtime')
                    WHERE id = new.id;
                END;''')
    
    
    # Commit the changes to the database
    conn.commit()
    # Check if the customers table exists
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS customers
                    (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL UNIQUE,
                    Phone INTEGER NOT NULL,
                    Address NOT NULL,
                    Phone2 INTEGER )''')
    
    # Commit the changes to the database
    conn.commit()
    # Check if the bills table exists
    # If the Inventory table doesn't exist, create it
    c.execute('''CREATE TABLE IF NOT EXISTS bills
                    (Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    bill_id INTEGER NOT NULL,
                    date DATE NOT NULL DEFAULT CURRENT_DATE,
                    customer_id INTEGER NOT NULL,
                    discount DECIMAL(10,2),
                    deliver_fees DECIMEL(10,2),
                    bill_net DECIMAL(10,2) NOT NULL,
                    deposite DECIMAL(10,2) NOT NULL,
                    remaining_money DECIMAL(10,2),
                    bill_note TEXT

                    )''')
    
    # Commit the changes to the database
    conn.commit()
        
    # Close the database connection
    conn.close()

if __name__ == "__main__":
    app = QApplication([])
    create_database()
    window = LoginWindow()
    window.run()
    app.exec_()
    
    