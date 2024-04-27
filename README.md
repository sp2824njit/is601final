# IS 601 Final Project

## What it does
REST API that keeps track of and updates information about a restaurant's customers, items, and orders

## Usage
`py init_db.py`

`uvicorn main:app`

## Design
System initializes sqlite database with existing customer, item, and order information from example_orders.json, then starts a REST API to perform CRUD operations on customers, items, and orders