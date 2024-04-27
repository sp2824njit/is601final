import sqlite3
import json

db_conn = sqlite3.connect('db.sqlite')

with db_conn:
    # SQL statments to create DB schema
    customer_create_sql = 'CREATE TABLE IF NOT EXISTS Customers (id integer NOT NULL, name varchar(100), phoneNum varchar(20), PRIMARY KEY (id));'
    items_create_sql = 'CREATE TABLE IF NOT EXISTS Items (id integer NOT NULL, name varchar(100), price float, PRIMARY KEY (id));'
    orders_create_sql = 'CREATE TABLE IF NOT EXISTS Orders (id integer NOT NULL, customerId int, notes varchar(255), timestamp integer, PRIMARY KEY (id), CONSTRAINT fk_customerid FOREIGN KEY (customerId) REFERENCES Customers(id));'
    order_list_create_sql = 'CREATE TABLE IF NOT EXISTS OrderList (id integer NOT NULL, orderId integer, itemId integer, PRIMARY KEY (id), CONSTRAINT fk_orderId FOREIGN KEY (orderId) REFERENCES Orders(id), CONSTRAINT fk_itemId FOREIGN KEY (itemId) REFERENCES Items(id))'
    
    # Creating tables in DB
    db_cursor = db_conn.cursor()
    db_cursor.execute(customer_create_sql)
    db_cursor.execute(items_create_sql)
    db_cursor.execute(orders_create_sql)
    db_cursor.execute(order_list_create_sql)
    
    # Reading orders file
    with open('example_orders.json') as f:
        orders_list = json.load(f)
    
    for order_obj in orders_list:
        customer_name = order_obj['name']
        customer_phone = order_obj['phone']
        order_notes = order_obj['notes']
        order_timestamp = order_obj['timestamp']
        
        # Check if customer is already in DB
        db_cursor.execute('SELECT * FROM Customers WHERE name=? AND phoneNum=?', (customer_name, customer_phone))
        rs_tuple = db_cursor.fetchone()
        customer_id = None
        if not rs_tuple:
            # Customer does not exist, add customer into DB
            db_cursor.execute('INSERT INTO Customers (name, phoneNum) VALUES (?,?)', (customer_name, customer_phone))
            customer_id = db_cursor.lastrowid
        else:
            customer_id = rs_tuple[0]
        
        db_cursor.execute('INSERT INTO Orders (customerId, notes, timestamp) VALUES (?,?,?)', (customer_id, order_notes, order_timestamp))
        order_id = db_cursor.lastrowid
        
        for item_obj in order_obj['items']:
            item_name = item_obj['name']
            item_price = item_obj['price']
            
            # Check if item is already in DB
            db_cursor.execute('SELECT * FROM Items WHERE name=? AND price=?', (item_name, item_price))
            rs_tuple = db_cursor.fetchone()
            item_id = None
            
            if not rs_tuple:
                # Item  does not exist, add item into DB
                db_cursor.execute('INSERT INTO Items (name, price) VALUES (?,?)', (item_name, item_price))
                item_id = db_cursor.lastrowid
            else:
                item_id = rs_tuple[0]
            
            db_cursor.execute("INSERT INTO OrderList (orderId, itemId) VALUES (?,?)", (order_id, item_id))


db_conn.close()
