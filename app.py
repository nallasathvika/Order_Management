from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Database connection function
def get_db_connection():
    conn = sqlite3.connect('RapidXcel.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route to display products
@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT stock_id, stock_name, price, quantity FROM stocks').fetchall()
    conn.close()
    return render_template('index.html', products=products)

# Place order route (handles order preview and pin code validation)
@app.route('/place_order', methods=['POST'])
def place_order():
    # Get customer inputs
    delivery_address = request.form['delivery_address']
    pin_code = request.form['pin_code']
    phone_number = request.form['phone_number']

    # Validate pin code
    if not validate_pin_code(pin_code):
        return "Invalid Pin Code. We do not service this area."

    # Retrieve products and calculate total cost and update stock
    products = []
    total_cost = 0
    shipping_cost = 0
    conn = get_db_connection()

    for product in conn.execute('SELECT stock_id, stock_name, price, quantity FROM stocks'):
        # Get quantity ordered, default to 0 if not selected
        quantity_ordered = request.form.get(f'quantity_{product["stock_id"]}', type=int, default=0)

        # Only process the product if a valid quantity > 0 is entered
        if quantity_ordered > 0:
            total_cost += product['price'] * quantity_ordered
            products.append({
                'stock_name': product['stock_name'],
                'quantity_ordered': quantity_ordered,
                'price': product['price'],
                'total': product['price'] * quantity_ordered
            })
            # Decrease the stock quantity in the database
            conn.execute('UPDATE stocks SET quantity = quantity - ? WHERE stock_id = ?',
                         (quantity_ordered, product['stock_id']))
    
    # Calculate shipping cost based on pin code and total weight
    total_weight = sum([prod['quantity_ordered'] for prod in products])
    shipping_cost = calculate_shipping_cost(pin_code, total_weight)

    conn.commit()
    conn.close()

    # Show order preview
    return render_template('preview.html', products=products, total_cost=total_cost, shipping_cost=shipping_cost, 
                           delivery_address=delivery_address, pin_code=pin_code, phone_number=phone_number)

# Function to validate pin code
def validate_pin_code(pin_code):
    # Example valid pin codes for testing
    valid_pin_codes = ['62701', '90001', '10001', '110001', '500001', 'SW1A 1AA']
    return pin_code in valid_pin_codes


# Function to calculate shipping cost
def calculate_shipping_cost(pin_code, total_weight):
    cost_per_kg = 10  # Example cost per kilogram
    return total_weight * cost_per_kg

# Confirm order route
@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    # Get final order details
    delivery_address = request.form['delivery_address']
    pin_code = request.form['pin_code']
    phone_number = request.form['phone_number']

    # Logic to save the order in the database
    # Placeholder: Insert order into the 'orders' table (not shown in this code)
    return f"Your order has been placed successfully! Delivery Address: {delivery_address}, Phone: {phone_number}"

if __name__ == '__main__':
    app.run(debug=True)
