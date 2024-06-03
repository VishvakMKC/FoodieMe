import webbrowser
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient
from sendemail import send_mail
app = Flask(__name__, static_folder='static')
app.secret_key = 'Replace with a secure secret key'  
XYZ_cart = {}
ABC_cart = {}

mongo_uri = "Replace with your MongoDB connection URI. "
client = MongoClient(mongo_uri)
db = client['Your_Database_Name']
collection = db['Your_Collection_Name']

name=""
email=""


@app.route('/') #normally our webpage will display the login page
def home():
    return render_template('Login.html')

def clear_carts():
    global XYZ_cart
    global ABC_cart
    XYZ_cart = {}
    ABC_cart = {}

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')

        # Check if the email is already registered
        if collection.find_one({'email': email}):
            flash('Email already exists. Please choose another email.', 'error')
        else:
            # Insert the user data into MongoDB Atlas
            user_data = {'name': name, 'email': email, 'password': password}
            collection.insert_one(user_data)

            # Flash a success message
            flash('Registration successful! You can now login.', 'success')

            # Redirect to the login page
            return redirect(url_for('home'))

    return render_template('Registration.html')

# Add a route to direct users from the login page to the registration page
@app.route('/create_account')
def create_account():
    return render_template('Registration.html')

@app.route('/check_login', methods=['POST'])
def check_login():
    if request.method == 'POST':

        provided_email = request.form.get('email') #getting the regno from the html form (Login.html)
        provided_password = request.form.get('password')  #getting the password from the html form (Login.html)

    user = collection.find_one({'email': provided_email,'password':provided_password}) # will perform a search operation in our database

    if user:
        global name  
        name = user['name'] 
        global email  
        email = user['email']
        clear_carts()
        return redirect(url_for('home_page' ,username=user['name'] )) #if user and password matches with the datum present in the mongo db, direct the page to home page or if that doesnt matches execute the else part
    else:
        flash('Invalid Username or Password','danger')
        return redirect(url_for('home') )#if user and password matches with the datum present in the mongo db, direct the page to home page or if that doesnt matches execute the else part


        
# Initialize separate carts for XYZ and ABC

def add_to_cart(restaurant_cart, item_name, item_price, item_quantity):
    # Overwrite the item's values if it already exists in the cart
    restaurant_cart[item_name] = {'price': item_price, 'quantity': item_quantity}


def calculate_total_cost(cart):
    total_cost = sum(item_info['price'] * item_info['quantity'] for item_info in cart.values())
    return total_cost


@app.route('/home/<username>')
def home_page(username):
    return render_template('homepage.html',username=username)

@app.route('/add_to_cart/<restaurant_name>', methods=['POST'])
def add_item_to_cart(restaurant_name):
    if request.method == 'POST':
        # Retrieve item information from the POST request
        item_name = request.form.get('item_name')
        item_price = float(request.form.get('item_price'))
        item_quantity = int(request.form.get('item_quantity'))

        # Validate the item information
        if item_name and item_price >= 0 and item_quantity >= 1:
            # Determine which cart to add the item to based on the restaurant name
            if restaurant_name == 'XYZ':
                add_to_cart(XYZ_cart, item_name, item_price, item_quantity)
                flash('Item added to XYZ cart successfully', 'success_XYZ')
            elif restaurant_name == 'ABC':
                add_to_cart(ABC_cart, item_name, item_price, item_quantity)
                flash('Item added to ABC cart successfully', 'success_ABC')
            else:
                flash('Invalid restaurant name', 'danger')
                return redirect(url_for('home_page'))

            return redirect(url_for(f'{restaurant_name}_page'))
        else:
            flash('Invalid item information', 'danger')
            return redirect(url_for(f'{restaurant_name}_page'))
    else:
        return 'Invalid request method'

@app.route('/remove_item/<restaurant_name>/<item_name_to_remove>', methods=['GET'])
def remove_item(restaurant_name, item_name_to_remove):
    # Determine which cart to remove the item from based on the restaurant name
    if restaurant_name == 'ABC':
        cart_to_modify = ABC_cart
    elif restaurant_name == 'XYZ':
        cart_to_modify = XYZ_cart
    else:
        cart_to_modify = None

    if cart_to_modify is not None:
        if item_name_to_remove in cart_to_modify:
            del cart_to_modify[item_name_to_remove]
            flash(f'Item "{item_name_to_remove}" removed from {restaurant_name.capitalize()} cart', 'danger')
        else:
            flash('Item not found in the cart', 'warning')
    else:
        flash('Invalid restaurant name', 'danger')

    return redirect(url_for(f'view_cart_{restaurant_name}'))


 
@app.route('/XYZ_page')
def XYZ_page():
    return render_template('XYZ.html')

@app.route('/ABC_page')
def ABC_page():
    return render_template('ABC.html')


@app.route('/view_cart_XYZ')
def view_cart_XYZ():
    total_cost_XYZ = calculate_total_cost(XYZ_cart)
    return render_template('view_cart_XYZ.html', XYZ_cart=XYZ_cart, total_cost_XYZ=total_cost_XYZ)

@app.route('/view_cart_ABC')
def view_cart_ABC():
    total_cost_ABC = calculate_total_cost(ABC_cart)
    return render_template('view_cart_ABC.html', ABC_cart=ABC_cart, total_cost_ABC=total_cost_ABC)

@app.route('/placeorder/<restaurant_name>')
def placeorder(restaurant_name):
    global XYZ_cart, ABC_cart  # Assuming XYZ_cart and ABC_cart are global variables
    cart = None  
    global relname
    if restaurant_name == "XYZ":
        relname="XYZ"
        cart = XYZ_cart
    elif restaurant_name == "ABC":
        relname="ABC"
        cart = ABC_cart
    else:
        return "Invalid restaurant name"

    total_cost = calculate_total_cost(cart)

    subject = "Your Order Details"
    message = f"Hello {name},<br><br>"
    message += f"Thank you for placing your order with {restaurant_name.capitalize()}!<br><br>"

    if cart:
        message += "<b>Cart Contents:</b><br>"
        message += "<ul>"
        for item_name, item_info in cart.items():
            message += f"<li>{item_name}: Price: ₹{item_info['price']}, Quantity: {item_info['quantity']}</li>"
        message += "</ul>"

    message += f"<br><b>Total Cost:</b> ₹{total_cost}<br><br>"
    message += f"We appreciate your business and look forward to serving you again soon."

    flash('Your order has been successfully placed, thank you!!Enjoy your FOOD!!','success')

    send_mail(name, email, subject, message)
    return redirect(url_for(f'view_cart_{relname}'))


#for user logout
@app.route('/logout')
def logout():
    return render_template('Login.html')


if __name__ == '__main__':
    # Open the browser automatically
    webbrowser.open('http://127.0.0.1:5000/')
    app.run(debug=True)