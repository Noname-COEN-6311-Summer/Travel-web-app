import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = os.urandom(24)


class Package:
    def __init__(self, destination, hotel, flights, activities, departure, price):
        self.destination = destination
        self.hotel = hotel
        self.flights = flights
        self.activities = activities
        self.departure = departure
        self.price = price

    def represent_packages(destination):
        agent = Agent()
        package = agent.get_packages(destination)
        if package:
            report = {
                'Destination': package.destination,
                'Hotel': package.hotel,
                'Flights': package.flights,
                'Activities': package.activities,
                'Departure_Time': package.departure,
                'Price': package.price
            }
            return report
        return None

    @staticmethod
    def calculate_price(package):
        prices = {
            'New York': 1000,
            'Paris': 1200,
            'London': 800,
            'Rome': 900,
            'Montreal': 800,
            'Tokyo': 1000,
            'Toronto': 1100,
            'Vancouver': 1200,

            'Hilton': 200,
            'Holiday': 100,
            'Marriott': 300,

            'Air Canada': 500,
            'West Jet': 400,
            'Poter': 300,
            'Air Transit': 200,

            'guided tour': 100,
            'food': 50,
            'excursions': 200,
        }

        destination_price = prices.get(package.destination, 0)
        hotel_price = prices.get(package.hotel, 0)
        flights_price = prices.get(package.flights, 0)
        activities_price = prices.get(package.activities, 0)
        total_price = destination_price + hotel_price + flights_price + activities_price

        return total_price

    @staticmethod
    def store_package(package):
        agent = Agent()
        agent.store_package(package)


class Agent:
    def __init__(self):
        self.packages = {
            'iceland': Package('Iceland', 'Lagoon', 'Air Canada', 'Excursions', '6am 07/05/23', 2100),
            'greece': Package('Greece', 'Westin', 'Air Canada', 'Food Tour', '6am 07/05/23', 2000),
            'banff': Package('Banff', 'Fairmont', 'Air Canada', 'Guided Tour', '6am 07/05/23', 1900),
        }

    def get_packages(self, destination):
        return self.packages.get(destination)

    def represent_packages(self, destination):
        package = self.get_packages(destination)
        if package:
            report = {
                'Destination': package.destination,
                'Hotel': package.hotel,
                'Flights': package.flights,
                'Activities': package.activities,
                'Departure_Time': package.departure,
                'Price': package.price
            }
            return report
        return None

    def calculate_price(self, package):
        prices = {
            'New York': 1000,
            'Paris': 1200,
            'London': 800,
            'Rome': 900,
            'Montreal': 800,
            'Tokyo': 1000,
            'Toronto': 1100,
            'Vancouver': 1200,

            'Hilton': 200,
            'Holiday': 100,
            'Marriott': 300,

            'Air Canada': 500,
            'West Jet': 400,
            'Poter': 300,
            'Air Transit': 200,

            'guided tour': 100,
            'food': 50,
            'excursions': 200,
        }

        destination_price = prices.get(package.destination, 0)
        hotel_price = prices.get(package.hotel, 0)
        flights_price = prices.get(package.flights, 0)
        activities_price = prices.get(package.activities, 0)
        total_price = destination_price + hotel_price + flights_price + activities_price

        return total_price

    def create_table(self):
        connection = sqlite3.connect('packages.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS packages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT,
                hotel TEXT,
                flights TEXT,
                activities TEXT,
                departure TEXT,
                price INTEGER
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

    def store_package(self, package):
        connection = sqlite3.connect('packages.db')
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO packages (destination, hotel, flights, activities, departure, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
        package.destination, package.hotel, package.flights, package.activities, package.departure, package.price))
        connection.commit()
        cursor.close()
        connection.close()

    def show_database(self):
        connection = sqlite3.connect('packages.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM packages')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        packages = []
        for row in rows:
            destination = row[1]
            hotel = row[2]
            flights = row[3]
            activities = row[4]
            departure = row[5]
            price = row[6]
            package = Package(destination, hotel, flights, activities, departure, price)
            packages.append(package)

        return packages

    def check_booking(self):
        customers = self.get_customers_info()
        bookings = []

        for customer in customers:
            customer_bookings = customer.get_book_information().get_bookings()
            bookings.extend(customer_bookings)

        return bookings

    def get_customers_info(self):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        customers = []
        for row in rows:
            username = row[1]
            customer = Customer()
            customer.username = username
            customers.append(customer)

        return customers

    def modify_booking(self, username, booking_id, destination, hotel, flights, activities, departure):
        customer = Customer()
        customer.username = username
        customer.db_name = f'{username}_bookings.db'
        book_manager = customer.get_book_information()
        bookings = book_manager.get_bookings()

        for booking in bookings:
            if booking.id == int(booking_id):
                booking.destination = destination
                booking.hotel = hotel
                booking.flights = flights
                booking.activities = activities
                booking.departure = departure

                # book_manager = BookManager(username)
                # book_manager.create_table()
                book_manager.store_booking(booking)  # Update the booking in the customer's database

                return True

        return False


class Customer:
    def __init__(self):
        self.agent = Agent()
        self.username = None
        self.db_name = None

    def search_destination(self, query):
        query = query.lower()
        if query in self.agent.packages:
            return f'/{query}.html'
        return None

    def modify_package(self, destination, hotel, flights, activities, departure):
        package = self.agent.get_packages(destination)
        if package:
            package.hotel = hotel
            package.flights = flights
            package.activities = activities
            package.departure = departure
            return True
        return False

    def edit_profile(self, username):
        self.username = username  # Store the logged-in username
        self.db_name = f'{self.username}_bookings.db'

    def get_profile(self):
        if self.username:
            username = self.username  # Store the username in a local variable
            # Fetch the user profile details from the database based on the stored username
            connection = sqlite3.connect('accounts.db')
            cursor = connection.cursor()
            cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
            profile = cursor.fetchone()
            cursor.close()
            connection.close()
            return profile
        return None

    def book_package(self, destination):
        package = self.agent.get_packages(destination)
        if package:
            # Store the booking information in the database
            self.agent.store_package(package)
            return True
        return False

    def get_bookings(self):
        connection = sqlite3.connect('bookings.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM bookings')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        bookings = []
        for row in rows:
            destination = row[1]
            hotel = row[2]
            flights = row[3]
            activities = row[4]
            departure = row[5]
            price = row[6]
            package = Package(destination, hotel, flights, activities, departure, price)
            bookings.append(package)

        return bookings

    def get_book_information(self):
        return BookManager(self.username)

    def cancel_booking(self, booking_id):
        if self.username is None:
            return []

        db_name = f'{self.username}_bookings.db'

        connection = sqlite3.connect(db_name)
        cursor = connection.cursor()
        cursor.execute('DELETE FROM bookings WHERE id=?', (booking_id,))
        connection.commit()
        cursor.close()
        connection.close()

        book_manager = BookManager(self.username)
        bookings = book_manager.get_bookings()
        return bookings

    def pay_booking(self, booking_id):
        pass

    def register(self, username, password, favorite_color):
        account_manager = AccountManager()
        account_manager.register(username, password, favorite_color)

    def login(self, username, password):
        account_manager = AccountManager()
        return account_manager.login(username, password)

    def logout(self):
        account_manager = AccountManager()
        account_manager.logout()

    def reset_password(self, username, new_password):
        account_manager = AccountManager()
        account_manager.reset_password(username, new_password)


class AccountManager:
    def __init__(self):
        self.create_table()
        self.agentaccounts()

    def create_table(self):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT,
                favorite_color TEXT,
                consecutive_failures INTEGER DEFAULT 0
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

    def register(self, username, password, favorite_color):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO accounts (username, password, favorite_color) VALUES (?, ?, ?)',
                       (username, password, favorite_color))
        connection.commit()
        cursor.close()
        connection.close()

    def login(self, username, password):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        account = cursor.fetchone()

        if account and account[2] == password:  # Check if the password is correct
            session['logged_in'] = True
            cursor.close()
            connection.close()
            return True

        cursor.close()
        connection.close()
        session['logged_in'] = False
        return False

    def logout(self):
        session.pop('logged_in', None)

    def agentaccounts(self):
        # Add agent account data to the 'accounts' table in the 'agent.db' database
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()

        agent_accounts = [
            ('DiWang', '123456', 'blue'),
            ('Melika', '1234567', 'red'),
        ]

        for username, password, favorite_color in agent_accounts:
            cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
            existing_account = cursor.fetchone()
            if existing_account is None:
                cursor.execute('INSERT INTO accounts (username, password, favorite_color) VALUES (?, ?, ?)', (username, password, favorite_color))

        connection.commit()
        cursor.close()
        connection.close()

    def account_security(self, username, new_password=None):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username=?', (username,))
        account = cursor.fetchone()

        if account:
            if new_password:  # Check if a new password is provided for password reset
                cursor.execute('UPDATE accounts SET password=? WHERE username=?', (new_password, username))
                connection.commit()
                cursor.close()
                connection.close()
                return None
            else:
                return 'Please reset your password.'

        cursor.close()
        connection.close()
        return None

    def check_security_answer(self, username, security_answer):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username=? AND favorite_color=?',
                       (username, security_answer))
        account = cursor.fetchone()
        cursor.close()
        connection.close()
        return account is not None

    def reset_password(self, username, new_password):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('UPDATE accounts SET password=? WHERE username=?', (new_password, username))
        connection.commit()
        cursor.close()
        connection.close()

account_manager = AccountManager()


class BookManager:
    def __init__(self, username):
        self.username = username
        self.db_name = f'{self.username}_bookings.db'
        self.create_table()

    def create_table(self):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                destination TEXT,
                hotel TEXT,
                flights TEXT,
                activities TEXT,
                departure TEXT,
                price INTEGER
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

    def store_booking(self, package):
        connection = sqlite3.connect(self.db_name)
        cursor = connection.cursor()
        cursor.execute('''
            INSERT INTO bookings (destination, hotel, flights, activities, departure, price)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            package.destination, package.hotel, package.flights, package.activities, package.departure, package.price))
        connection.commit()
        cursor.close()
        connection.close()

    def get_bookings(self):
        connection = sqlite3.connect(f'{self.username}_bookings.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM bookings')
        rows = cursor.fetchall()
        cursor.close()
        connection.close()

        bookings = []
        for row in rows:
            destination = row[1]
            hotel = row[2]
            flights = row[3]
            activities = row[4]
            departure = row[5]
            price = row[6]
            package = Package(destination, hotel, flights, activities, departure, price)
            bookings.append(package)

        return bookings

# book_manager = BookManager()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form.get('search')
        customer = Customer()
        destination_url = customer.search_destination(search_query)
        if destination_url:
            return redirect(destination_url)
        else:
            return render_template('index.html', search_error=True)

    logged_in = False
    username = None
    if 'logged_in' in session:
        logged_in = session['logged_in']
        username = session.get('username')

    return render_template('index.html', search_error=False, logged_in=logged_in, username=username)


@app.route('/creation', methods=['GET', 'POST'])
def creation():
    agent = Agent()
    book_manager = BookManager(session['username'])

    if request.method == 'POST':
        modification_mode = request.form.get('modification_mode')
        if modification_mode:
            destination = request.form.get('destination')
            hotel = request.form.get('hotel')
            flights = request.form.get('flights')
            activities = request.form.get('activities')
            departure = request.form.get('departure')
            customer = Customer()
            customer.modify_package(destination, hotel, flights, activities, departure)
            return redirect(url_for('creation'))
        else:
            destination = request.form.get('destination')
            hotel = request.form.get('hotel')
            flights = request.form.get('flights')
            activities = request.form.get('activities')
            departure = request.form.get('departure')

            package = Package(destination, hotel, flights, activities, departure, price=0)
            agent.store_package(package)  # Store the new package in the database
            book_manager.store_booking(package)  # Store the new package in the bookings database

            session['package'] = {
                'destination': destination,
                'hotel': hotel,
                'flights': flights,
                'activities': activities,
                'departure': departure,
                'price': agent.calculate_price(package)
            }

            report = agent.represent_packages(package.destination)  # Retrieve the package details for the report

            return render_template('creation.html', package=package, total_price=agent.calculate_price(package), report=report)

    return render_template('creation.html', package=None, total_price=0, report=None)


@app.route('/iceland.html')
def iceland():
    agent = Agent()
    report = agent.represent_packages('iceland')

    session['package'] = {
        'destination': report['Destination'],
        'hotel': report['Hotel'],
        'flights': report['Flights'],
        'activities': report['Activities'],
        'departure': report['Departure_Time'],
        'price': report['Price']
    }

    return render_template('iceland.html', report=report)


@app.route('/greece.html')
def greece():
    agent = Agent()
    report = agent.represent_packages('greece')

    session['package'] = {
        'destination': report['Destination'],
        'hotel': report['Hotel'],
        'flights': report['Flights'],
        'activities': report['Activities'],
        'departure': report['Departure_Time'],
        'price': report['Price']
    }

    return render_template('greece.html', report=report)


@app.route('/banff.html')
def banff():
    agent = Agent()
    report = agent.represent_packages('banff')

    session['package'] = {
        'destination': report['Destination'],
        'hotel': report['Hotel'],
        'flights': report['Flights'],
        'activities': report['Activities'],
        'departure': report['Departure_Time'],
        'price': report['Price']
    }

    return render_template('banff.html', report=report)


@app.route('/<destination>.html')
def destination_page(destination):
    agent = Agent()
    report = agent.represent_packages(destination)
    if report:
        return render_template('destination.html', report=report)
    else:
        return redirect(url_for('index'))

@app.route('/database')
def view_database():
    agent = Agent()
    packages = agent.show_database()
    return render_template('database.html', packages=packages)


@app.route('/register', methods=['GET', 'POST'])
def register():
    error_message = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        favorite_color = request.form['security_answer']

        account_manager.register(username, password, favorite_color)
        return redirect(url_for('index'))

    return render_template('register.html', error_message=error_message)


@app.route('/login', methods=['GET', 'POST'])
def login():
    login_status = None  # Variable to indicate the login status
    error_message = None  # Variable to store the error message

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if account_manager.login(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            login_status = 'error'
            error_message = 'Invalid username or password.'

    return render_template('login.html', login_status=login_status, error_message=error_message)


@app.route('/logout')
def logout():
    account_manager.logout()
    # Perform logout operations here
    # Redirect to the desired page after logout
    return redirect(url_for('index'))

@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    error_message = None
    if request.method == 'POST':
        username = request.form['username']
        security_answer = request.form['security_answer']
        new_password = request.form['new_password']

        account = account_manager.account_security(username)
        if account and account_manager.check_security_answer(username, security_answer):
            account_manager.reset_password(username, new_password)
            return redirect(url_for('login', login_status='success', error_message='Password reset successful. Please log in with your new password.'))
        else:
            error_message = 'Invalid username or security answer.'

    return render_template('reset_password.html', error_message=error_message)


@app.route('/profile')
def profile():
    if 'logged_in' in session and session['logged_in']:
        customer = Customer()
        customer.username = session['username']
        profile = customer.get_profile()
        book_manager = BookManager(session['username'])
        bookings = book_manager.get_bookings()
        # bookings = customer.get_bookings()

        # Fetch the package information from the session
        package_data = session.get('package')
        total_price = request.args.get('total_price')

        for booking in bookings:
            booking.price = customer.agent.calculate_price(booking)

        if package_data:
            package = Package(
                package_data['destination'],
                package_data['hotel'],
                package_data['flights'],
                package_data['activities'],
                package_data['departure'],
                package_data['price']
            )
            bookings.append(package)

        return render_template('profile.html', profile=profile, bookings=bookings, total_price=total_price, book_manager=book_manager)
    else:
        return redirect(url_for('login'))


@app.route('/book', methods=['POST'])
def book():

    if request.method == 'POST':
        # Retrieve the package details from the session
        destination = request.form.get('destination')

        # Get the package details based on the destination
        agent = Agent()
        package = agent.get_packages(destination)

        if package:
            # Store the booking in the database
            customer = Customer()
            customer.username = session['username']
            if customer.book_package(destination):
                customer.agent.store_package(package)
                book_manager = customer.get_book_information()
                book_manager.store_booking(package)

                # Pass the total price as a query parameter to the profile route
                return redirect(url_for('profile', total_price=package.price))
            else:
                return render_template('creation.html')

        return render_template('creation.html')

@app.route('/cancel-booking', methods=['POST'])
def cancel_booking():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        customer = Customer()
        customer.username = session['username']
        customer.cancel_booking(booking_id)
        return redirect(url_for('profile'))

@app.route('/pay-booking', methods=['POST'])
def pay_booking():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        customer = Customer()
        customer.username = session['username']
        customer.pay_booking(booking_id)
        return redirect(url_for('profile'))

@app.route('/workstation')
def workstation():
    if 'logged_in' in session and session['logged_in']:
        if session['username'] == 'DiWang' or session['username'] == 'Melika':
            agent = Agent()
            customers = agent.get_customers_info()
            bookings = agent.check_booking()
            filtered_customers = [customer for customer in customers if customer.username not in ['DiWang', 'Melika']]
            return render_template('workstation.html', customers=filtered_customers, bookings=bookings)
        else:
            return "Sorry, you are not an agent."
    else:
        return redirect(url_for('login'))


@app.route('/modify-booking', methods=['POST'])
def modify_booking():
    if request.method == 'POST':
        booking_id = request.form.get('booking_id')
        destination = request.form.get('destination')
        hotel = request.form.get('hotel')
        flights = request.form.get('flights')
        activities = request.form.get('activities')
        departure = request.form.get('departure')

        agent = Agent()
        username = session['username']
        result = agent.modify_booking(username, booking_id, destination, hotel, flights, activities, departure)

        if result:
            return redirect(url_for('workstation'))
        else:
            return redirect(url_for('workstation'))


if __name__ == '__main__':
    # book_manager = BookManager()
    app.run(debug=True)