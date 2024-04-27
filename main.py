import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from time import time

app = FastAPI()

class CustomerModel(BaseModel):
    customer_id: int | None = None
    name: str
    phoneNum: str
    

class ItemModel(BaseModel):
    item_id: int | None = None
    name: str
    price: float
    

class OrderModel(BaseModel):
    order_id: int | None = None
    customer_id: int
    notes: str
    item_ids: list[int]


def get_db_connection() -> sqlite3.Connection:
    return sqlite3.connect('db.sqlite')

@app.get('/customers/{customer_id}')
async def get_customers(customer_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute('SELECT id, phoneNum, name FROM Customers WHERE id=?', (customer_id,))
        sql_result = db_cursor.fetchone()
    db_conn.close()
    if not sql_result:
        raise HTTPException(status_code=404, detail="Customer not found")
    cust_id, cust_phone, cust_name = sql_result
    return {
        "id": cust_id,
        "phone": cust_phone,
        "name": cust_name,
    }

@app.get('/items/{item_id}')
async def get_items(item_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute('SELECT id, name, price FROM Items WHERE id=?', (item_id,))
        sql_result = db_cursor.fetchone()
    db_conn.close()
    if not sql_result:
        raise HTTPException(404, "Item not found")
    db_item_id, db_item_name, db_item_price = sql_result
    return {
        "id": db_item_id,
        "name": db_item_name,
        "price": db_item_price
    }


@app.get('/orders/{order_id}')
async def get_orders(order_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        db_cursor.execute('SELECT Orders.id, Orders.notes, Orders.customerId, Orders.timestamp, OrderList.itemId FROM Orders JOIN OrderList on Orders.id=OrderList.orderId WHERE Orders.id=?', (order_id,))
        sql_result: list[tuple] = db_cursor.fetchall()
    db_conn.close()
    item_id_list = []
    for db_order_id, db_order_notes, db_customer_id, db_order_timestamp, db_item_id in sql_result:
        ret_order_id = db_order_id
        ret_order_notes = db_order_notes
        ret_customer_id = db_customer_id
        ret_order_timestamp = db_order_timestamp
        item_id_list.append(db_item_id)
    return {
        'orderid': ret_order_id,
        'ordernotes': ret_order_notes,
        'customerid': ret_customer_id,
        'ordertimestamp': ret_order_timestamp,
        'itemsids': item_id_list
    }
    
        
@app.post('/customers')
async def create_customer(customer_payload: CustomerModel):
    if customer_payload.customer_id is not None:
        raise HTTPException(400, 'Customer ID not allowed')
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        sql_stmt = 'INSERT INTO Customers (name, phoneNum) VALUES (?,?)'
        db_cursor.execute(sql_stmt, (customer_payload.name, customer_payload.phoneNum))
        new_customer_id = db_cursor.lastrowid
    db_conn.close()
    return {"customerId": new_customer_id}
    

@app.post('/items')
async def create_item(item_payload: ItemModel):
    if item_payload.item_id is not None:
        raise HTTPException(400, 'Item ID not allowed')
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        sql_stmt = 'INSERT INTO Items (name, price) VALUES (?,?)'
        db_cursor.execute(sql_stmt, (item_payload.name, item_payload.price))
        new_item_id = db_cursor.lastrowid
    db_conn.close()
    return {"itemId": new_item_id}


@app.post('/orders')
async def create_order(order_payload: OrderModel):
    if order_payload.order_id is not None:
        raise HTTPException(400, 'Order ID not allowed')
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        find_customer_sql_stmt = 'SELECT COUNT(*) FROM Customers WHERE id=?'
        db_cursor.execute(find_customer_sql_stmt, (order_payload.customer_id,))
        sql_result = db_cursor.fetchone()
        if sql_result[0] == 0:
            raise HTTPException(400, 'Customer ID not found')
        
        for input_item_id in order_payload.item_ids:
            find_item_sql_stmt = 'SELECT COUNT(*) FROM Items WHERE id=?'
            db_cursor.execute(find_item_sql_stmt, (input_item_id,))
            sql_result = db_cursor.fetchone()
            if sql_result[0] == 0:
                raise HTTPException(400, f'Item ID {input_item_id} not found')
            
        order_sql_stmt = 'INSERT INTO Orders (customerId, notes, timestamp) VALUES (?,?,?)'
        db_cursor.execute(order_sql_stmt, (order_payload.customer_id, order_payload.notes, int(time())))
        new_order_id = db_cursor.lastrowid
        
        for input_item_id in order_payload.item_ids:
            order_list_sql_stmt = 'INSERT INTO OrderList (orderId, itemId) VALUES (?,?)'
            db_cursor.execute(order_list_sql_stmt, (new_order_id, input_item_id))
            
    db_conn.close()
    return {'orderId': new_order_id}


@app.delete('/customers/{customer_id}')
async def delete_customer(customer_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        delete_customer_sql_stmt = 'DELETE FROM Customers WHERE id=?'
        db_cursor.execute(delete_customer_sql_stmt, (customer_id,))
        rows_changed = db_conn.total_changes
    db_conn.close()
    if rows_changed == 0:
        raise HTTPException(404, 'Item Not Found')
    return rows_changed


@app.delete('/items/{items_id}')
async def delete_item(item_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        delete_item_sql_stmt = 'DELETE FROM Items WHERE id=?'
        db_cursor.execute(delete_item_sql_stmt, (item_id,))
        rows_changed = db_conn.total_changes
    db_conn.close()
    if rows_changed == 0:
        raise HTTPException(404, 'Item Not Found')
    return rows_changed


@app.delete('/orders/{order_id}')
async def delete_order(order_id: int):
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        delete_order_sql_stmt = 'DELETE FROM Orders WHERE id=?'
        db_cursor.execute(delete_order_sql_stmt, (order_id,))
        rows_changed = db_conn.total_changes
    db_conn.close()
    if rows_changed == 0:
        raise HTTPException(404, 'Item Not Found')
    return rows_changed


@app.put('/customers/{customer_id}')
async def update_customer(customer_id: int, customer_payload: CustomerModel):
    if customer_id != customer_payload.customer_id:
        raise HTTPException(400, 'Mismatching customer IDs')
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        update_customer_sql_stmt = 'UPDATE Customers SET name=?, phone=? WHERE id=?'
        db_cursor.execute(update_customer_sql_stmt, (customer_payload.name, customer_payload.phoneNum, customer_id))
        rows_changed = db_conn.total_changes
    db_conn.close()
    if rows_changed == 0:
            raise HTTPException(404, 'Item not found')
    return customer_payload


@app.put('/items/{item_id}')
async def update_item(item_id: int, item_payload: ItemModel):
    if item_id != item_payload.item_id:
        raise HTTPException(400, 'Mismatching item IDs')
    db_conn = get_db_connection()
    with db_conn:
        db_cursor = db_conn.cursor()
        update_item_sql_stmt = 'UPDATE Items SET name=?, price=? WHERE id=?'
        db_cursor.execute(update_item_sql_stmt, (item_payload.name, item_payload.price, item_id))
        rows_changed = db_conn.total_changes
    db_conn.close()
    if rows_changed == 0:
            raise HTTPException(404, 'Item not found')
    return item_payload


@app.put('/orders/{order_id}')
async def update_order(order_id: int):
    pass
