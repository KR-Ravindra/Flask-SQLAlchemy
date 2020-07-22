from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.automap import automap_base
import decimal
import flask.json

app = Flask(__name__)


class MyJSONEncoder(flask.json.JSONEncoder):
    ''' Custom JSONEncoder that will help flask.jsonify to avoid TypeError for JSON serializing Decimal values from Database results. '''

    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)  # Convert decimal instances to strings.
        return super(MyJSONEncoder, self).default(obj)


# Sets json_encoder to my custom class MyJSONEncoder.
app.json_encoder = MyJSONEncoder
# DatabaseURI for mysql installed on system.
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/northwind_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

''' The following code block automaps the SQL Alchemy without defining any models with pre existing MySql database on the server '''
base = automap_base()
base.prepare(db.engine, reflect=True)
Products = base.classes.Products
Customers = base.classes.Customers
Orders = base.classes.Orders


@app.route('/products', methods=['GET'])
def products():
    ''' Lists all the produts '''
    results = db.session.query(Products).all()
    listing = []
    for r in results:
        r = r.__dict__  # Converts the class instance to dictionary
        # Removes the InstantState which prevents json Serializability
        del r['_sa_instance_state']
        listing.append(r)
    return flask.jsonify(listing)  # uses MyJSONEncoder


@app.route('/product/add', methods=['POST'])
def add_product():
    '''Adds entry into Products table of the database.'''
    new_product = Products(ProductID=request.json['ProductID'], ProductName=request.json['ProductName'], SupplierID=request.json['SupplierID'], CategoryID=request.json['CategoryID'], Discontinued=request.json['Discontinued'], QuantityPerUnit=request.json['QuantityPerUnit'],
                           UnitPrice=request.json['UnitPrice'], UnitsInStock=request.json['UnitsInStock'], UnitsOnOrder=request.json['UnitsOnOrder'], ReorderLevel=request.json['ReorderLevel'])
    db.session.add(new_product)
    db.session.commit()
    return "Successfully added product"


@app.route('/product/<id>', methods=['GET'])
def search_product(id):
    '''Searches product using ProductID'''
    results = db.session.query(Products).get(id)
    if results == None:
        return "Record Not Found"
    results = results.__dict__
    del results['_sa_instance_state']
    return flask.jsonify(results)


@app.route('/product/update/<id>', methods=['PUT'])
def update_product(id):
    '''Product update is performed here by referencing desired product by it ProductID'''
    product = db.session.query(Products).get(id)
    if product == None:
        return "Record Not Found"
    product.ProductID = request.json['ProductID']
    product.ProductName = request.json['ProductName']
    product.SupplierID = request.json['SupplierID']
    product.CategoryID = request.json['CategoryID']
    product.Discontinued = request.json['Discontinued']
    product.QuantityPerUnit = request.json['QuantityPerUnit']
    product.UnitPrice = request.json['UnitPrice']
    product.UnitsInStock = request.json['UnitsInStock']
    product.UnitsOnOrder = request.json['UnitsOnOrder']
    product.ReorderLevel = request.json['ReorderLevel']
    db.session.commit()
    return search_product(id)

# Not desired in the task but without this the rest of the code won't really feel RESTful.


@app.route('/product/remove/<id>', methods=['DELETE'])
def remove_product(id):
    '''This removes the entry in the table by referencing with CustomerID'''
    product = db.session.query(Products).get(id)
    if product == None:
        return "Record Not Found"
    db.session.delete(product)
    db.session.commit()
    return "Deleted Product Successfully"


@app.route('/customers', methods=['GET'])
def customers():
    '''Lists all the customers in json '''
    results = db.session.query(Customers).all()
    listing = []
    for r in results:
        r = r.__dict__
        del r['_sa_instance_state']
        listing.append(r)
    return flask.jsonify(listing)


@app.route('/customer/<id>', methods=['GET'])
def search_customer(id):
    '''Search a particular customer entry by means of CustomerID'''
    results = db.session.query(Customers).get(id)
    if results == None:
        return "Record Not Found"
    results = results.__dict__
    del results['_sa_instance_state']
    return flask.jsonify(results)


@app.route('/customer/add', methods=['POST'])
def add_customer():
    '''Adds an entry into Customer table'''
    new_customer = Customers(CustomerID=request.json['CustomerID'], CompanyName=request.json['CompanyName'], ContactName=request.json['ContactName'], ContactTitle=request.json['ContactTitle'], Address=request.json['Address'],
                             City=request.json['City'], Region=request.json['Region'], PostalCode=request.json['PostalCode'], Fax=request.json['Fax'], Phone=request.json['Phone'], Country=request.json['Country'])
    db.session.add(new_customer)
    db.session.commit()
    return "Successfully Added the Customer!"


@app.route('/customer/update/<id>', methods=['PUT'])
def update_customer(id):
    '''Updates Customer entries, takes CustomerID to select the entry that is to be updated'''
    customer = db.session.query(Customers).get(id)
    if customer == None:
        return "Record Not Found"
    customer.CustomerID = request.json['CustomerID']
    customer.CompanyName = request.json['CompanyName']
    customer.ContactName = request.json['ContactName']
    customer.ContactTitle = request.json['ContactTitle']
    customer.Address = request.json['Address']
    customer.City = request.json['City']
    customer.Region = request.json['Region']
    customer.PostalCode = request.json['PostalCode']
    customer.Fax = request.json['Fax']
    customer.Phone = request.json['Phone']
    customer.Country = request.json['Country']
    db.session.commit()
    return search_customer(id)

# Not desired in the task but without this the rest of the code won't really feel RESTful.


@app.route('/customer/remove/<id>', methods=['DELETE'])
def remove_customer(id):
    '''This removes the entry in the table by referencing with CustomerID'''
    customer = db.session.query(Customers).get(id)
    if customer == None:
        return "Record Not Found"
    db.session.delete(customer)
    db.session.commit()
    return "Deleted Customer Successfully"


@app.route('/orderhistory/<id>', methods=['GET'])
def order_history(id):
    results = db.session.query(Orders).filter(Orders.CustomerID == id).all()
    if results == None:
        return "Record Not Found"
    listing = []
    for r in results:
        r = r.__dict__
        del r['_sa_instance_state'], r['Freight'], r['EmployeeID'], r['RequiredDate'], r[
            'ShipAddress'], r['ShipRegion'], r['ShipVia'], r['ShipPostalCode'], r['ShippedDate'], r['CustomerID']
        listing.append(r)
    return flask.jsonify(listing)


@app.route('/', methods=['GET'])
def base_route():
    '''BaseRoute URL'''
    URL = "https://documenter.getpostman.com/view/12122001/T1DnidZm"
    return f"Welcome! This might not be the page you are looking for, learn the functionality of this API at {URL}"


if __name__ == "__main__":
    app.run(debug=True, port=5000, host='0.0.0.0')
