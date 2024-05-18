import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
import MySQLdb.cursors
import uuid

app = Flask(__name__)

app.secret_key = "abcdefgh"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "dasak"
app.config["MYSQL_DB"] = "DASAK"

mysql = MySQL(app)

def check_logged_in():
    print(session.get('loggedin'))
    if not session.get('loggedin'):
        print("Not logged in")
        return redirect(url_for('login'))
    return None

def check_account_type():
    print(session.get('accounttype'))
    if not session.get('accounttype'):
        print("Not logged in")
        return redirect(url_for('login'))
    return session.get('accounttype')

def company_pageguard():
    type = check_account_type()
    if(type == "company"):
        return None
    return redirect(url_for('login'))

def astronaut_pageguard():
    type = check_account_type()
    if(type == "astronaut"):
        return None
    return redirect(url_for('login'))

def get_user_id():
    user_id = session.get('userid')
    if not session.get('userid'):
        print("No User Id")
        return None
    return user_id
    

@app.route("/")
@app.route("/main", methods=["GET", "POST"])
def main():
    redirect_if_not_logged_in = check_logged_in()
    if redirect_if_not_logged_in:
        return redirect_if_not_logged_in
    
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
            cursor.execute('SELECT * FROM Company WHERE id = %s', (user['id'],))
            company = cursor.fetchone()
            cursor.execute('SELECT * FROM Astronaut WHERE id = %s', (user['id'],))
            astronaut = cursor.fetchone()
            if(company):
                session['accounttype'] = 'company'
            elif(astronaut):
                session['accounttype'] = 'astronaut'
            else:
                session['accounttype'] = 'None'
            message = 'Logged in successfully!'
            return redirect(url_for('main'))
        else:
            message = 'Please enter correct email / password !'
    return render_template('login.html', message = message)

#TODO CHECK IF USER IS INSERTED EVEN THOUGH UNSUCCESFUL CREATION
@app.route('/register', methods =['GET', 'POST'])
def register():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id, name FROM Company")
    companies = cursor.fetchall()
    print(companies)
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
                company_id = request.form.get('company_id')
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
                cursor.execute('INSERT INTO Astronaut VALUES (%s, %s, %s, %s, %s, %s)', (str(random_uuid),company_id, date_of_birth, nationality, rank, 0,))
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

    return render_template('register.html', message = message, companies =  companies)


@app.route("/create_mission", methods=["GET", "POST"])
def createMission():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    if request.method == "POST":
        # Extract data from form
        title = request.form.get('title')
        description = request.form.get('description')
        objectives = request.form.get('objectives')
        launch_date = request.form.get('launch_date')
        duration = request.form.get('duration')
        num_of_astronauts = request.form.get('num_of_astronauts')
        payload_volume = request.form.get('payload_volume')
        payload_weight = request.form.get('payload_weight')
        
        # Data validation
        if not title or not description or not objectives or not launch_date or not duration or not num_of_astronauts or not payload_volume or not payload_weight:
            flash("Fill all the necessary fields.", 'error')
            return render_template("create_mission.html")
        
        # Check date is in the future
        if datetime.strptime(launch_date, '%Y-%m-%d') < datetime.now():
            flash("Launch date must be in the future.", 'error')
            return render_template("create_mission.html")

        # Insert data into the database
        try:
            cursor = mysql.connection.cursor()
            cursor.execute('''
                INSERT INTO Mission (mission_id, employer_id, title, description, objectives, launch_date, duration, num_of_astronauts, payload_volume, payload_weight) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (uuid.uuid4().hex, session.get('company_id'), title, description, objectives, launch_date, duration, num_of_astronauts, payload_volume, payload_weight))
            mysql.connection.commit()
            flash("Mission created successfully!", 'success')
            return redirect(url_for('main'))  # Redirect to the main page or a confirmation page
        
        except Exception as e:
            print("Error executing SQL query:", e)
            return render_template("create_mission.html")
    return render_template("create_mission.html")

@app.route('/logout')
def logout():
    """Log out the user by clearing the session and redirecting to the login page."""
    session.pop('loggedin', None)  # Remove 'loggedin' from session
    session.pop('userid', None)    # Optional: clear other session variables
    session.pop('email', None)     # Optional: clear other session variables
    return redirect(url_for('login'))


@app.route("/manage_astronauts", methods=["GET", "POST"])
def manageAstronauts():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
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
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    if request.method == 'GET':
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT T.name, T.training_id, T.code, T.description, T.duration, IFNULL(GROUP_CONCAT(P.code), Null) AS prereq_ids FROM Training T LEFT JOIN Training_Prerequisite_Training ON training_id = train_id LEFT JOIN Training P ON P.training_id = prereq_id GROUP BY T.training_id')
        trainings = cursor.fetchall()   
        cursor.execute('SELECT * FROM Astronaut')
        astronauts = cursor.fetchall()
        return render_template("assign_trainings.html", trainings=trainings, astronauts=astronauts)
    else:
        training_id = request.form['training_id']
        selected_ids = request.form.getlist('selected_ids')

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
            astronauts_cant_take = []
            for astronaut_id in selected_ids:
                # Check if the astronaut has completed all prerequisite trainings
                cursor.execute('SELECT prereq_id FROM Training_Prerequisite_Training WHERE train_id = %s', (training_id,))
                prerequisite_trainings = cursor.fetchall()

                cursor.execute('SELECT training_id FROM Astronaut_Completes_Training WHERE astronaut_id = %s AND status = 1', (astronaut_id,))
                completed_trainings = [row['training_id'] for row in cursor.fetchall()]
                cursor.execute('SELECT training_id FROM Astronaut_Completes_Training WHERE astronaut_id = %s', (astronaut_id,))
                completed_or_not_completed_trainings = [row['training_id'] for row in cursor.fetchall()]

                if all(prereq['prereq_id'] in completed_trainings for prereq in prerequisite_trainings) and training_id not in completed_or_not_completed_trainings:
                    cursor.execute('INSERT INTO Astronaut_Completes_Training (astronaut_id, training_id, status) VALUES (%s, %s, 0)', (astronaut_id, training_id))
                    mysql.connection.commit()
                else:
                    astronauts_cant_take.append(astronaut_id)
            
            if not astronauts_cant_take:
                flash(f'All selected astronauts have been assigned to training {training_id}', 'info')
            else:
                flash(f'Astronauts {", ".join(astronauts_cant_take)} can not be assigned', 'alert')

        except Exception as e:
            print("Error executing SQL query:", e)
            flash('An error occurred while processing the request', 'alert')

        return redirect(url_for('assignTrainings'))  # Redirect to the same page after processing
@app.route("/bid_for_mission", methods=["GET", "POST"])
def bidForMission():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    if request.method == "GET":
        cursor.execute("SELECT * FROM Mission")
        missions = cursor.fetchall()
        for mission in missions:
            if mission['launch_date']:
                mission['launch_date'] = mission['launch_date'].strftime('%Y-%m-%d')
        return render_template("bid_for_mission.html", missions=missions)
    
    elif request.method == "POST":
        bid_amount = request.form.get("bid_amount")
        astronaut_ids = request.form.getlist("astronaut_ids")  
        
        try:
            bid_amount = float(bid_amount) 
        except ValueError:
            flash("Invalid bid amount. Please enter a valid number.", "error")
            return redirect(url_for("bidForMission"))

        #TODO: Check requirements
        if bid_amount <= 0:
            flash("Bid amount must be greater than $0.", "error")
            return redirect(url_for("bidForMission"))
        
        cursor.execute("INSERT INTO Bid (bid_id, bidder_id, amount, bid_date, status) VALUES (%s, %s, %s, CURDATE(), 'Open')", (uuid.uuid4().hex, session.get('company_id'), bid_amount))
        for astronaut_id in astronaut_ids:
            cursor.execute("INSERT INTO Bid_Has_Astronaut (bid_id, id) VALUES (%s, %s)", (last_inserted_bid_id, astronaut_id))
        mysql.connection.commit()
        
        return redirect(url_for("bidForMission"))

@app.route("/view_bids", methods=["GET", "POST"])
def viewBids():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == "POST":
        bid_id = request.form.get('bid_id')
        if bid_id:
            try:
                cursor.execute("UPDATE Bid SET status = 'Accepted' WHERE bid_id = %s", (bid_id,))
                mysql.connection.commit()
                flash('Bid accepted successfully!', 'success')
                #TODO: Accept only one bid
            except Exception as e:
                flash(f'Error accepting bid: {str(e)}', 'error')
        return redirect(url_for('viewBids'))

    cursor.execute('''
        SELECT Bid.bid_id, Bid.amount, Bid.bid_date, Bid.status, Mission.title AS mission_title, Company.name AS company_name
        FROM Bid
        INNER JOIN Mission_Accepted_Bid ON Bid.bid_id = Mission_Accepted_Bid.bid_id
        INNER JOIN Mission ON Mission_Accepted_Bid.mission_id = Mission.mission_id
        INNER JOIN Bidder ON Bid.bidder_id = Bidder.id
        INNER JOIN Company ON Bidder.id = Company.id
        ORDER BY Bid.amount DESC
    ''')
    bids = cursor.fetchall()
    return render_template("view_bids.html", bids=bids)

@app.route("/admin_page", methods=["GET", "POST"])
def admin():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_admin = None # TODO check if admin
    
    if redirect_if_not_logged_in or redirect_if_not_admin:
        return redirect_if_not_logged_in
    
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

@app.route('/dashboard')
def dashboard():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_astronaut = astronaut_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_astronaut:
        return redirect_if_not_logged_in
    
    user_id = get_user_id()
    
    current_trainings, past_trainings = get_trainings(user_id)
    upcoming_missions, past_missions = get_missions(user_id)

    return render_template('dashboard.html', current_trainings=current_trainings, past_trainings=past_trainings,
                           upcoming_missions=upcoming_missions, past_missions=past_missions)
    
def get_trainings(astronaut_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    cursor.execute("""
    SELECT T.*, ACT.status, ACT.training_id
    FROM Training T
    JOIN Astronaut_Completes_Training ACT ON T.training_id = ACT.training_id
    WHERE ACT.astronaut_id = %s
    """, (astronaut_id,))

    trainings = cursor.fetchall()
    current, past = [], []
    for training in trainings:
        if training['status'] == 1: # TODO assuming status 1 is complete
            past.append(training)
        else:
            current.append(training)
    return current, past

def get_missions(astronaut_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    today = datetime.now().date()

    cursor.execute("""
    SELECT M.*, AM.mission_id
    FROM Mission M
    JOIN Astronaut_Accepted_Missions AM ON M.mission_id = AM.mission_id
    WHERE AM.astronaut_id = %s
    """, (astronaut_id,))

    missions = cursor.fetchall()
    upcoming, past = [], []
    for mission in missions:
        if mission['launch_date'] > today:
            upcoming.append(mission)
        else:
            past.append(mission)
    return upcoming, past


@app.errorhandler(404)
def page_not_found(e):
    # Note 'e' is the error object
    return render_template('error_page.html'), 404



if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
