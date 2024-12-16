from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize the Flask application
app = Flask(__name__)

# Configure the database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'  # Use SQLite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable track modifications
db = SQLAlchemy(app)

# Define the Order model
class Order(db.Model):
    __tablename__ = 'orders'  # Name of the table in the database

    id = db.Column(db.Integer, primary_key=True)  # Order ID
    customer_id = db.Column(db.Integer, nullable=False)  # Customer ID
    shipping_address = db.Column(db.String(255), nullable=False)  # Shipping Address
    consignment_weight = db.Column(db.Float, nullable=False)  # Weight of the consignment
    shipping_cost = db.Column(db.Float, nullable=False)  # Shipping cost
    status = db.Column(db.String(50), default='Pending')  # Order status

    def __repr__(self):
        return f'<Order {self.id}>'

# Create the database tables
with app.app_context():
    db.create_all()

# Function to calculate shipping cost
def calculate_shipping_cost(weight):
    base_cost = 5.0  # Base cost for shipping
    cost_per_kg = 2.0  # Cost per kilogram
    return base_cost + (cost_per_kg * weight)

# Create an order (POST)
@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.json  # Get the JSON data from the request
    new_order = Order(
        customer_id=data['customer_id'],
        shipping_address=data['shipping_address'],
        consignment_weight=data['consignment_weight'],
        shipping_cost=calculate_shipping_cost(data['consignment_weight'])  # Calculate shipping cost
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify({'message': 'Order created successfully', 'order_id': new_order.id}), 201

# Retrieve all orders (GET)
@app.route('/api/orders', methods=['GET'])
def get_orders():
    orders = Order.query.all()  # Query all orders
    return jsonify([{
        'id': order.id,
        'customer_id': order.customer_id,
        'shipping_address': order.shipping_address,
        'consignment_weight': order.consignment_weight,
        'shipping_cost': order.shipping_cost,
        'status': order.status
    } for order in orders]), 200

# Retrieve a specific order (GET)
@app.route('/api/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    order = Order.query.get(order_id)  # Query the order by ID
    if order:
        return jsonify({
            'id': order.id,
            'customer_id': order.customer_id,
            'shipping_address': order.shipping_address,
            'consignment_weight': order.consignment_weight,
            'shipping_cost': order.shipping_cost,
            'status': order.status
        }), 200
    return jsonify({'message': 'Order not found'}), 404

# Update an order (PUT)
@app.route('/api/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    order = Order.query.get(order_id)  # Query the order by ID
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    data = request.json  # Get the JSON data from the request
    order.customer_id = data.get('customer_id', order.customer_id)
    order.shipping_address = data.get('shipping_address', order.shipping_address)
    order.consignment_weight = data.get('consignment_weight', order.consignment_weight)
    order.shipping_cost = calculate_shipping_cost(order.consignment_weight)  # Recalculate shipping cost
    order.status = data.get('status', order.status)

    db.session.commit()
    return jsonify({'message': 'Order updated successfully'}), 200

# Delete an order (DELETE)
@app.route('/api/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    order = Order.query.get(order_id)  # Query the order by ID
    if not order:
        return jsonify({'message': 'Order not found'}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({'message': 'Order deleted successfully'}), 200

# Define a route for the root URL
@app.route('/')
def home():
    return "Welcome to the RapidXcel Logistics Order Management API!"

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
