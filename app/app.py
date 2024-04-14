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
        cursor.execute('SELECT * FROM User WHERE email = % s AND password = % s', (email, password, ))
        user = cursor.fetchone()
        if user:              
            session['loggedin'] = True
            session['userid'] = user['id']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return redirect(url_for('main'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)

#TODO CHECK IF USER IS INSERTED EVEN THOUGH UNSUCCESFUL CREATION
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
        cursor.execute('SELECT email FROM User WHERE email =  %s', (email,))
        

        account = cursor.fetchone()

        if account:
            message = 'Choose a different email!'
  
        elif not email or not password:
            message = 'Please fill out the form!'

        else:
            random_uuid = uuid.uuid4()
            cursor.execute('INSERT INTO User (id, email, password) VALUES (%s, % s, % s)', (str(random_uuid), email, password,))
            mysql.connection.commit()
            
            if account_type == 'Astronaut':
                title = request.form.get('title')
                first_name = request.form.get('first_name')
                middle_name = request.form.get('middle_name', '')  # Optional field
                last_name = request.form.get('last_name')
                date_of_birth = request.form.get('date_of_birth')
                nationality = request.form.get('nationality')
                rank = request.form.get('rank')

                try:
                    cursor.execute('INSERT INTO Person VALUES (%s, %s, %s, %s, %s)', (str(random_uuid), title, first_name, middle_name, last_name,))
                    mysql.connection.commit()
                except Exception as e:
                    # Handle the exception here
                    print("Error executing SQL query 1:", e)
                #TODO COMPANY ID NEEDS TO BE SPECIFIED - NOW IT'S 1
                cursor.execute('INSERT INTO Astronaut VALUES (%s,1, %s, %s, %s, %s)', (str(random_uuid), date_of_birth, nationality, rank, 0,))
                mysql.connection.commit()

            elif account_type == 'Company':
                name = request.form.get('company_name')
                street = request.form.get('street', '')
                city = request.form.get('city')
                state = request.form.get('state')
                postal_code = request.form.get('postal_code')
                founding_date = request.form.get('founding_date')
                area_code = request.form.get('area_code')
                balance = 0
                phone_number = request.form.get('number')
                try:
                    cursor.execute('INSERT INTO Company (id, name, street, city, state, postal_code, founding_date, balance, area_code, phone_number) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',(random_uuid, name, street, city, state, postal_code, founding_date, balance, area_code, phone_number,))
                    mysql.connection.commit()
                except Exception as e:
                    print("Error executing SQL query 2:", e)

                if 'Bidder' in request.form:  
                    print("BIDDER")
                    specialization = request.form.get('specialization')
                    try:
                        cursor.execute('INSERT INTO Bidder (id, specialization) VALUES (%s, %s)', (str(random_uuid), specialization,))
                        mysql.connection.commit()
                    except Exception as e:
                        print("Error executing SQL query 3:", e)
                    
                if 'Employer' in request.form: 
                    industry = request.form.get('industry')
                    try:
                        cursor.execute('INSERT INTO Employer ( id, industry) VALUES (%s, %s)', (str(random_uuid), industry,))
                        mysql.connection.commit()
                    except Exception as e:
                        print("Error executing SQL query 4:", e)
                    message = 'User successfully created!'
                
            return redirect(url_for('main'))

    return render_template('register.html', message = message)


@app.route("/create_mission", methods=["GET", "POST"])
def createMission():

    return render_template("create_mission.html")

@app.route("/manage_astronauts", methods=["GET", "POST"])
def manageAstronauts():
    # if 'loggedin' in session:
    #     if request.method == "GET":
    #         companyId = session['userid']
    #         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    #         #Filters are not included in the query rn. Needs to be implemented
    #         cursor.execute('''
    #             SELECT 
    #             A.id AS astronaut_id,
    #             P.title,
    #             P.first_name,
    #             P.middle_name,
    #             P.last_name,
    #             (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
    #             JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
    #             JOIN Mission M ON MAB.mission_id = M.mission_id
    #             WHERE BHA.id = A.id
    #             AND A.company_id = %s
    #             AND (M.launch_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) OR DATE_ADD(M.launch_date, INTERVAL M.duration DAY) >= CURDATE())
    #             ) AS filtered_missions_count,
    #             (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
    #             JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
    #             JOIN Mission M ON MAB.mission_id = M.mission_id
    #             WHERE BHA.id = A.id AND A.company_id = @company_id 
    #             AND DATE_ADD(M.launch_date, INTERVAL M.duration DAY) >= CURDATE()
    #             ) AS total_missions_count
    #             FROM Astronaut A NATURAL JOIN Person P
    #             WHERE
    #             A.company_id = %s ''', (companyId, companyId, ))
    #         astronauts = cursor.fetchall()
    #         return render_template("manage_astronauts.html", astronauts = astronauts)
    #return render_template("manage_astronauts.html", astronauts = astronauts)
    return render_template("manage_astronauts.html")
@app.route("/assign_trainings", methods=["GET", "POST"])
def assignTrainings():

    return render_template("assign_trainings.html")


@app.route("/bid_for_mission", methods=["GET", "POST"])
def bidForMission():

    return render_template("bid_for_mission.html")

@app.route("/admin_page", methods=["GET", "POST"])
def admin():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    report = None
    report_type = None

    if request.method == 'POST':
        if 'expensive_mission' in request.form:
            report_type = 'Most Expensive Missions'
            cursor.execute("INSERT INTO SystemReport (id, title, content) SELECT ?, ?, CONCAT('Mission ID: ', mission_id, ', Payload Weight: ', payload_weight, ', Title: ', title) FROM Mission ORDER BY payload_weight DESC LIMIT 1;", (str(uuid.uuid4()), report_type))
            mysql.connection.commit()

        elif 'duplicate_missions' in request.form:
            report_type = 'Duplicate Missions'
            cursor.execute("""
                INSERT INTO SystemReport (id, title, content)
                SELECT ?, ?, GROUP_CONCAT(CONCAT('Mission ID: ', mission_id))
                FROM (
                    SELECT mission_id
                    FROM Mission
                    GROUP BY title, description, launch_date
                    HAVING COUNT(*) > 1
                ) AS Duplicates;
            """, (str(uuid.uuid4()), report_type))
            mysql.connection.commit()

        # Retrieve the latest report
        cursor.execute("""
            SELECT content FROM SystemReport
            WHERE title = ?
            ORDER BY report_id DESC
            LIMIT 1;
        """, (report_type,))
        report = cursor.fetchone()

    cursor.close()


    return render_template('admin_page.html', report=report, report_type=report_type)





if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
