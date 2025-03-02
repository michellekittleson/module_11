from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
from flask_marshmallow import Marshmallow
from typing import List
import datetime
from marshmallow import fields, validate, ValidationError
from sqlalchemy import select, delete
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Lynn060386!@localhost/e_commerce_db'

class Base(DeclarativeBase):
    pass

ma = Marshmallow(app)
db = SQLAlchemy(app, model_class=Base)
CORS(app)

order_product = db.Table(
    'Order_Product',
    Base.metadata,
    db.Column('order_id', db.ForeignKey('Orders.id'), primary_key=True),
    db.Column('product_id', db.ForeignKey('Products.id'), primary_key=True)
)


class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(320))
    phone: Mapped[str] = mapped_column(db.String(15))
    customer_account: Mapped["CustomerAccount"] = db.relationship(back_populates="customer")
    orders: Mapped[List["Order"]] = db.relationship(back_populates="customer")

class Order(Base):
    __tablename__ = 'Orders'
    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[datetime.date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    customer: Mapped["Customer"] = db.relationship(back_populates="orders")

    products: Mapped[List["Product"]] = db.relationship(secondary=order_product)


class CustomerAccount(Base):
    __tablename__ = 'Customer_Accounts'
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('customers.id'))

    customer: Mapped["Customer"] = db.relationship(back_populates="customer_account")

class Product(Base):
    __tablename__ = 'Products'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)



class CustomerSchema(ma.Schema):
    id = fields.Integer(required=False)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "email", "phone")

# This is line 77
class CustomersSchema(ma.Schema):
    id = fields.Integer(required=True)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)

    class Meta:
        fields = ("id", "name", "email", "phone")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True) ## Not sure about this line

class ProductSchema(ma.Schema):
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("name", "price", "id")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

@app.route('/customers', methods=['GET'])
def get_customers():
    query = select(Customer)
    result = db.session.execute(query).scalars()
    customers = result.all()

    return customers_schema.jsonify(customers)

@app.route('/customers', methods=['POST'])
def add_cusotmer():
    try:

        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    with Session(db.engine) as session:
        with session.begin():
            new_customer = Customer(name=customer_data['name'], email=customer_data['email'], phone=customer_data['phone'])
            session.add(new_customer)
            session.commit()
    
    return jsonify({"message": "New customer added successfully"}), 201

@app.route('/customers/<int:id>', methods=['PUT'])
def update_customer(id):
    with Session(db.engine) as session:
        with session.begin():

            query = select(Customer).filter(Customer.id==id)
            result = session.execute(query).scalars().first()
            if result is None:
                return jsonify({"error": "Customer not found"}), 404
            
            customer = result
            try:

                customer_data = customer_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            

            for field, value in customer_data.items():
                setattr(customer, field, value)



            session.commit()
            return jsonify({"message": "Customer details updated successfully"}), 200



@app.route('/customers/<int:id>', methods=['DELETE'])
def delete_customer(id):

    delete_statement = delete(Customer).where(Customer.id == id)
    with db.sesion.begin():

        result = db.session.execute(delete_statement)





        return jsonify({"message": "Customer removed successfully"}), 200

@app.route('/products', methods=['POST'])
def add_product():
    try:

        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session:
        with session.begin():



            new_product = Product(name=product_data['name'], price=product_data['price'])
            session.add(new_product)
            session.commit()
    
    return jsonify({"message": "New product added successfully"}), 201

@app.route('/products', methods=['GET'])
def get_products():
    query = select(Product)
    result = db.session.execute(query).scalars()
    products = result.all()

    return products_schema.jsonify(products)

@app.route('/products/<int:id>', methods=['PUT'])
def update_product(id):
    with Session(db.engine) as session:
        with session.begin():
            
            query = select(Product).filter(Product.id == id)
            result = session.execute(query).scalars().first()
            if result is None:
                return jsonify({"error": "Product not found"}), 404



            product = result
            try:
                

                product_data = product_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400



            for field, value in product_data.items():
                


                setattr(product, field, value)
            
            session.commit()
            return jsonify({"message": "Product details updated successfully"}), 200

@app.route('/products/<int:id>', methods=['DELETE'])
def delete_product(id):

    delete_statement = delete(Product).where(Product.id == id)
    with db.sesion.begin():
        result = db.session.execute(delete_statement)
        if result.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
        
        return jsonify({"message": "Product removed successfully"}), 200



@app.route('/customers/<int:id>', methods=['GET'])
def get_customer_by_id(id):
    query = select(Customer).filter(Customer.id == id)
    customer = db.session.execute(query).scalars().first()

    if customer:
        return customer_schema.jsonify(customer)
    else:
        return jsonify({"message": "Customer not found"}), 404

@app.route('/customers/by-email')
def query_customer_by_email():
    email = request.args.get('email')
    query = select(Customer).filter_by(email=email)
    customers = db.session.execute(query).scalars().all()

    return customers_schema.jsonify(customers)

@app.route('/products/<int:id>', methods=['GET'])
def get_product_by_id(id):
    query = select(Product).where(Product.id == id)
    product = db.session.execute(query).scalars().first()

    if product:
        return product_schema.jsonify(product)
    else:
        return jsonify({"message": "Product not found"}), 404

@app.route('/products/by-name', methods=['GET'])
def query_product_by_name():
    name = request.args.get('name')
    search = f"%{name}%"
    query = select(Product).where(Product.name.like(search)).order_by(Product.price.asc())
    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products)

with app.app_context():

    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
        