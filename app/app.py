import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import MySQLdb.cursors
import uuid

app = Flask(__name__)

app.secret_key = "abcdefgh"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "dasak"
app.config["MYSQL_DB"] = "DASAK"

mysql = MySQL(app)

@app.route("/")
@app.route("/main", methods=["GET", "POST"])
def main():
    message = "CU"
    return render_template("main.html", message=message)

@app.route('/login', methods =['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM customer WHERE name = % s AND cid = % s', (email, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['cid']
            session['email'] = user['name']
            message = 'Logged in successfully!'
            return redirect(url_for('main_page'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)

@app.route('/register', methods =['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' :
        account_type = request.form.get('account_type')  
        email = request.form['email']
        password = request.form['password']
        

        if not all([email, password]):
            message = 'Please fill out the form!'
            return render_template('register.html', message = message)

        # Validation for fields
        if len(password) > 6:
            message = 'Password must not exceed 6 characters.'
            return render_template('login.html', message=message)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email FROM User WHERE users.email =  %s', (email,))
        

        account = cursor.fetchone()

        if account:
            message = 'Choose a different email!'
  
        elif not email or not password:
            message = 'Please fill out the form!'

        else:
            random_uuid = uuid.uuid4()
            cursor.execute('INSERT INTO Users (cid, name) VALUES (% s, % s)', (password, username))
            mysql.connection.commit()
            
            if account_type == 'Astronaut':
                title = request.form.get('title')
                first_name = request.form.get('first_name')
                middle_name = request.form.get('middle_name', '')  # Optional field
                last_name = request.form.get('last_name')
                date_of_birth = request.form.get('date_of_birth')
                nationality = request.form.get('nationality')
                rank = request.form.get('rank')

                cursor.execute('INSERT INTO Person VALUES (%s, %s, %s, %s, %s)', (new_id, title, first_name, middle_name, last_name))
                cursor.execute('INSERT INTO Astronaut VALUES (%s, %s, %s, %s, %s)', (new_id, date_of_birth, nationality, rank, 0))

            elif account_type == 'Company':
                street = request.form.get('street')
                city = request.form.get('city')
                state = request.form.get('state')
                postal_code = request.form.get('postal_code')
                founding_date = request.form.get('founding_date')
                area_code = request.form.get('area_code')
                number = request.form.get('number')
                cursor.execute('INSERT INTO Company VALUES (%s, %s, %s, %s, %s, %s, %s, %s)', (new_id, street, city, state, postal_code, founding_date, 0, area_code, number))

            if 'Bidder' in request.form:  # Assuming a checkbox named 'Bidder'
                specialization = request.form.get('specialization')
                cursor.execute('INSERT INTO Bidder VALUES (%s, %s)', (new_id, specialization))

            if 'Employer' in request.form:  # Assuming a checkbox named 'Employer'
                industry = request.form.get('industry')
                cursor.execute('INSERT INTO Employer VALUES (%s, %s)', (new_id, industry))
                message = 'User successfully created!'
                
            return render_template('login.html', message=message)

    return render_template('register.html', message = message)


@app.route("/create_mission", methods=["GET", "POST"])
def createMission():

    return render_template("create_mission.html")

@app.route("/manage_astronauts", methods=["GET", "POST"])
def manageAstronauts():

    return render_template("manage_astronauts.html")

@app.route("/assign_trainings", methods=["GET", "POST"])
def assignTrainings():

    return render_template("assign_trainings.html")


@app.route("/bid_for_mission", methods=["GET", "POST"])
def bidForMission():

    return render_template("bid_for_mission.html")




if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
