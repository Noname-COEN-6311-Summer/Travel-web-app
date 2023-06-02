import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

class Package:
    def __init__(self, destination, hotel, flights, activities, departure, price):
        self.destination = destination
        self.hotel = hotel
        self.flights = flights
        self.activities = activities
        self.departure = departure
        self.price = price


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


class Customer:
    def __init__(self):
        self.agent = Agent()

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


class AccountManager:
    def __init__(self):
        self.create_table()

    def create_table(self):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')
        connection.commit()
        cursor.close()
        connection.close()

    def register(self, username, password):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('INSERT INTO accounts (username, password) VALUES (?, ?)', (username, password))
        connection.commit()
        cursor.close()
        connection.close()

    def login(self, username, password):
        connection = sqlite3.connect('accounts.db')
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM accounts WHERE username=? AND password=?', (username, password))
        account = cursor.fetchone()
        cursor.close()
        connection.close()

        if account:
            session['logged_in'] = True
            return True
        return False

    def logout(self):
        session.pop('logged_in', None)

account_manager = AccountManager()


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
    if 'logged_in' in session:
        logged_in = True

    return render_template('index.html', search_error=False, logged_in=logged_in)


@app.route('/creation', methods=['GET', 'POST'])
def creation():
    agent = Agent()

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

            package = Package(destination, hotel, flights, activities, departure, 0)
            total_price = agent.calculate_price(package)
            agent.store_package(package)  # Store the new package in the database

            return render_template('creation.html', package=package, total_price=total_price)

    return render_template('creation.html', package=None, total_price=0)


@app.route('/iceland.html')
def iceland():
    agent = Agent()
    report = agent.represent_packages('iceland')
    return render_template('iceland.html', report=report)


@app.route('/greece.html')
def greece():
    agent = Agent()
    report = agent.represent_packages('greece')
    return render_template('greece.html', report=report)


@app.route('/banff.html')
def banff():
    agent = Agent()
    report = agent.represent_packages('banff')
    return render_template('banff.html', report=report)


@app.route('/<destination>.html')
def destination_page(destination):
    agent = Agent()
    report = agent.represent_packages(destination)
    if report:
        return render_template('destination.html', report=report)
    else:
        return redirect(url_for('index'))
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')
@app.route('/database')
def view_database():
    agent = Agent()
    packages = agent.show_database()
    return render_template('database.html', packages=packages)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        account_manager.register(username, password)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    login_status = None  # Variable to indicate the login status
    error_message = None  # Variable to store the error message
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if account_manager.login(username, password):
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            login_status = 'error'
            error_message = 'Invalid username or password.'
    return render_template('login.html', login_status=login_status, error_message=error_message)

@app.route('/logout')
def logout():
    # Perform logout operations here
    # Redirect to the desired page after logout
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
