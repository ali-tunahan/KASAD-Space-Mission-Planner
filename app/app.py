import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
from flask import Response
from datetime import datetime
import MySQLdb.cursors
import uuid
import datetime
from datetime import datetime



app = Flask(__name__)

app.secret_key = "abcdefgh"

app.config["MYSQL_HOST"] = "db"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = "dasak"
app.config["MYSQL_DB"] = "DASAK"
app.debug = True

mysql = MySQL(app)

def check_logged_in():
    print(session.get('loggedin'))
    if not session.get('loggedin'):
        print("Not logged in")
        return redirect(url_for('login'))
    return None

def save_admin_status():
    user_id = session.get('userid')
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT 1 FROM Admin WHERE id = %s;
    """, (user_id,))
    admin_exists = cursor.fetchone()

    if admin_exists:
       session['isAdmin'] = True
    else:
        session['isAdmin'] = False


def check_admin():
    redirect_if_not_logged_in = check_logged_in()
    
    if redirect_if_not_logged_in:
        return redirect_if_not_logged_in
    print(session.get('loggedin'))
    if not session.get('loggedin'):
        print("Not logged in")
        return redirect(url_for('login'))

    user_id = session.get('userid')
    if user_id is None:
        print("User ID not found")
        return redirect(url_for('login'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT 1 FROM Admin WHERE id = %s;
    """, (user_id,))
    admin_exists = cursor.fetchone()

    if admin_exists:
        print("User is an admin")
    else:
        print("User is not an admin")
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
    
    user_id = get_user_id()
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    type = check_account_type()
    
    #Init all passed parameter, else gives error
    company = None
    person = None
    astronaut = None
    
    if(type == "company"):
        cursor.execute("SELECT * FROM Company WHERE id = %s", (user_id,))
        company = cursor.fetchone()
    elif(type == 'astronaut'):
        cursor.execute("SELECT * FROM Person WHERE id = %s", (user_id,))
        person = cursor.fetchone()
    
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM Astronaut WHERE id = %s", (user_id,))
        astronaut = cursor.fetchone()
        print(astronaut)
        cursor.execute("SELECT * FROM Company WHERE id = %s", (astronaut['company_id'],))
        company = cursor.fetchone()
    
    return render_template("main.html", person = person, company=company, astronaut = astronaut)

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
            save_admin_status()
            
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
            flash(message, 'error')
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
            flash(message, 'error')
            return render_template('register.html', message = message)

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT email FROM User WHERE email =  %s', (email,))
        
        account = cursor.fetchone()

        if account:
            message = 'Choose a different email!'
            flash(message, 'error')
  
        elif not email or not password:
            message = 'Please fill out the form!'
            flash(message, 'error')

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
                session['accounttype'] = 'astronaut'

            elif account_type == 'Company':
                print("im here")
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
                    session['accounttype'] = 'company'
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
            session['loggedin'] = True
            session['userid'] = random_uuid
            session['email'] = email
            return redirect(url_for('main'))

    return render_template('register.html', message = message, companies =  companies)

@app.route("/create_mission", methods=["GET", "POST"])
def createMission():
    user_id = get_user_id()
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT training_id, name FROM Training")
    trainings = cursor.fetchall()
    
    if request.method == "POST":
        title = request.form.get('title')
        description = request.form.get('description')
        objectives = request.form.get('objectives')
        launch_date = request.form.get('launch_date')
        duration = request.form.get('duration')
        num_of_astronauts = request.form.get('num_of_astronauts')
        payload_volume = request.form.get('payload_volume')
        payload_weight = request.form.get('payload_weight')
        required_trainings = request.form.getlist('required_trainings[]') 
 
        print(required_trainings)
        
        if not title or not description or not objectives or not launch_date or not duration or not num_of_astronauts or not payload_volume or not payload_weight:
   
            return render_template("create_mission.html", trainings=trainings)
        
        if datetime.strptime(launch_date, '%Y-%m-%d') < datetime.now():
            flash("Launch date must be in the future", 'error')
            return render_template("create_mission.html", trainings=trainings)
        mission_id = uuid.uuid4().hex
        cursor.execute('''
            INSERT INTO Mission (mission_id, employer_id, title, description, objectives, launch_date, duration, num_of_astronauts, payload_volume, payload_weight) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (mission_id, user_id, title, description, objectives, launch_date, duration, num_of_astronauts, payload_volume, payload_weight))
        for training_id in required_trainings:
            if training_id:  
                cursor.execute('''
                    INSERT INTO Mission_Requires_Training (mission_id, training_id)
                    VALUES (%s, %s)
                ''', (mission_id, training_id))
        mysql.connection.commit()
        return redirect(url_for('main'))

    return render_template("create_mission.html", trainings=trainings)

@app.route("/manage_astronauts", methods=["GET", "POST", "DELETE"])
def manageAstronauts():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    astronaut_id = request.args.get('astronaut_id')
    if request.method == "GET":
        if not astronaut_id:
            companyId = session['userid']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

            #Initial request without any filters
            if not bool(request.args):
                cursor.execute('''
                    SELECT 
                    A.id AS astronaut_id,
                    A.years_of_experience,
                    P.title,
                    P.first_name,
                    P.middle_name,
                    P.last_name,
                    AA.age,
                    A_stats.performance,
                    A_stats.experience,
                    (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
                    JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
                    JOIN Mission M ON MAB.mission_id = M.mission_id
                    WHERE BHA.id = A.id
                    AND A.company_id = %s
                    AND (M.launch_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) OR DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) >= CURDATE())
                    ) AS filtered_missions_count,
                    (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
                    JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
                    JOIN Mission M ON MAB.mission_id = M.mission_id
                    WHERE BHA.id = A.id AND A.company_id = %s
                    AND DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) >= CURDATE()
                    ) AS total_missions_count
                    FROM Astronaut A NATURAL JOIN Person P NATURAL JOIN Astronaut_Age AS AA JOIN Astronaut_Stats AS A_stats ON AA.id=A_stats.astronaut_id
                    WHERE
                    A.company_id = %s ''', (companyId, companyId, companyId))
            else:
                #Request with filters
                cursor.execute('''
                    SELECT 
                    A.id AS astronaut_id,
                    A.years_of_experience,
                    P.title,
                    P.first_name,
                    P.middle_name,
                    P.last_name,
                    AA.age,
                    A_stats.performance,
                    A_stats.experience,
                    (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
                    JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
                    JOIN Mission M ON MAB.mission_id = M.mission_id
                    WHERE BHA.id = A.id
                    AND A.company_id = %s
                    AND (M.launch_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH) OR DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) >= CURDATE())
                    ) AS filtered_missions_count,
                    (SELECT COUNT(*) FROM Bid_Has_Astronaut BHA
                    JOIN Mission_Accepted_Bid MAB ON BHA.bid_id = MAB.bid_id
                    JOIN Mission M ON MAB.mission_id = M.mission_id
                    WHERE BHA.id = A.id AND A.company_id = %s
                    AND DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) >= CURDATE()
                    ) AS total_missions_count
                    FROM Astronaut A NATURAL JOIN Person P NATURAL JOIN Astronaut_Age AA JOIN Astronaut_Stats AS A_stats ON AA.id=A_stats.astronaut_id
                    WHERE
                    (P.first_name LIKE %s AND P.middle_name LIKE %s AND P.last_name LIKE %s) AND            
                    A.company_id = %s AND          
                    (%s = '' OR A.date_of_birth >= %s) AND
                    (%s = '' OR A.date_of_birth <= %s) AND
                    (%s = '' OR A.nationality = %s) AND
                    (%s = '' OR A.rank = %s) AND
                    (%s = '' OR A.years_of_experience >= %s) AND
                    (%s = '' OR A.years_of_experience <= %s) ''', 
                    (companyId, companyId,'%%'+ request.args.get('name')+'%%', '%%'+ request.args.get('Mname')+'%%','%%'+ request.args.get('Lname')+'%%',companyId, request.args.get('dateOfBirthLower'), request.args.get('dateOfBirthLower'), 
                    request.args.get('dateOfBirthUpper'), request.args.get('dateOfBirthUpper'), 
                    request.args.get('nationalityFilter'), request.args.get('nationalityFilter'), 
                    request.args.get('rankFilter'), request.args.get('rankFilter'),
                    request.args.get('yearsOfExperienceLower'), request.args.get('yearsOfExperienceLower'), 
                    request.args.get('yearsOfExperienceUpper'), request.args.get('yearsOfExperienceUpper')))
            astronauts = cursor.fetchall()
            return render_template("manage_astronauts.html", astronauts = astronauts)
        else:
            companyId = session['userid']
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cursor.execute('''
                SELECT 
                A.id AS astronaut_id,
                P.title,
                P.first_name,
                P.middle_name,
                P.last_name,
                A.date_of_birth,
                A.nationality,
                A.rank,
                A.years_of_experience
                FROM Astronaut A NATURAL JOIN Person P
                WHERE A.id = %s AND A.company_id = %s
            ''', (astronaut_id, companyId))
            astronaut_data = cursor.fetchone()
            if astronaut_data:
                # Parse the date_of_birth into day, month, and year components
                date_of_birth = astronaut_data['date_of_birth']
                astronaut_data['day_of_birth'] = date_of_birth.day
                astronaut_data['month_of_birth'] = date_of_birth.month
                astronaut_data['year_of_birth'] = date_of_birth.year
                del astronaut_data['date_of_birth']

                return jsonify(astronaut_data)
            else:
                return jsonify({'error': 'Astronaut not found'}), 404
    elif request.method == "POST":
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
        UPDATE Person
        SET title=%s, first_name=%s, middle_name=%s, last_name=%s
        WHERE id=%s
        ''', (request.form.get('title'), request.form.get('fname'), request.form.get('mname'), request.form.get('lname'), astronaut_id))

        day = min(max(int(request.form.get('day')), 1), 31)
        month = min(max(int(request.form.get('month')), 1), 12)
        year = min(max(int(request.form.get('year')), 1900), 2005)
        date_of_birth = datetime(year, month, day).date()

        # Update the Astronaut table
        cursor.execute('''
            UPDATE Astronaut
            SET nationality=%s, rank=%s, years_of_experience=%s, date_of_birth=%s
            WHERE id=%s
            ''', (request.form.get('nationality'), request.form.get('rank'), request.form.get('exp'), date_of_birth, astronaut_id))
        mysql.connection.commit()
        return redirect(url_for('manageAstronauts'))
    elif request.method == "DELETE":
        print("DELETE ID:"+astronaut_id)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('''
            UPDATE Astronaut
            SET company_id=NULL
            WHERE id=%s
            ''',(astronaut_id,))
        mysql.connection.commit()
      
@app.route('/logout')
def logout():
    """Log out the user by clearing the session and redirecting to the login page."""
    session.pop('loggedin', None)  # Remove 'loggedin' from session
    session.pop('userid', None)    # Optional: clear other session variables
    session.pop('email', None)     # Optional: clear other session variables
    session.pop('isAdmin', None)
    session.pop('accounttype', None)
    
    flash("Logged out successfully!", 'success')
    return redirect(url_for('login'))


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
        cursor.execute('SELECT * FROM Astronaut A, Person P,Company C WHERE A.id=P.id AND A.company_id=C.id AND A.company_id = %s',(session['userid'],))
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
                cursor.execute('SELECT * FROM Person WHERE id = %s', (astronaut_id,))
                astro_name_result = cursor.fetchone()
                astro_name = astro_name_result['first_name'] +' '+astro_name_result['middle_name'] +' '+ astro_name_result['last_name']
                astronauts_cant_take.append(astro_name)
            cursor.execute('SELECT name FROM Training WHERE training_id = %s', (training_id,))
            training_name_result = cursor.fetchone()
            training_name = training_name_result['name']
            if not astronauts_cant_take:
                flash(f'All selected astronauts have been assigned to training {training_name}', 'success')
            else:
                flash(f'Astronaut(s) {", ".join(astronauts_cant_take)} can not be assigned', 'danger')

        except Exception as e:
            print("Error executing SQL query:", e)

        return redirect(url_for('assignTrainings'))  # Redirect to the same page after processing
    
@app.route("/bid_for_mission", methods=["GET", "POST"])
def bidForMission():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_company = company_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_company:
        return redirect_if_not_logged_in
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    if request.method == "GET":

        # Fetch min and max values for filters
        cursor.execute("SELECT MIN(launch_date) as min_date, MAX(launch_date) as max_date FROM Mission")
        launch_date_range = cursor.fetchone()
        
        cursor.execute("SELECT MIN(duration) as min_duration, MAX(duration) as max_duration FROM Mission")
        duration_range = cursor.fetchone()
        
        cursor.execute("SELECT MIN(payload_volume) as min_volume, MAX(payload_volume) as max_volume FROM Mission")
        volume_range = cursor.fetchone()
        
        cursor.execute("SELECT MIN(payload_weight) as min_weight, MAX(payload_weight) as max_weight FROM Mission")
        weight_range = cursor.fetchone()

        # Prepare query based on filters
        filter_params = request.args
        
        query = """ SELECT M.*, GROUP_CONCAT(DISTINCT T.name SEPARATOR ', ') AS training_names
            FROM Mission M
            LEFT JOIN Mission_Accepted_Bid MAB ON M.mission_id = MAB.mission_id
            LEFT JOIN Mission_Requires_Training MRT on M.mission_id = MRT.mission_id
            LEFT JOIN Training T on MRT.training_id = T.training_id
            WHERE MAB.bid_id IS NULL
        """
        params = []
        
        if 'launch_date' in filter_params and filter_params['launch_date']:
            query += " AND M.launch_date = %s"
            params.append(filter_params['launch_date'])
        if 'duration' in filter_params and filter_params['duration']:
            query += " AND M.duration <= %s"
            params.append(filter_params['duration'])
        if 'volume' in filter_params and filter_params['volume']:
            query += " AND M.payload_volume <= %s"
            params.append(filter_params['volume'])
        if 'weight' in filter_params and filter_params['weight']:
            query += " AND M.payload_weight <= %s"
            params.append(filter_params['weight'])
        query += " GROUP BY M.mission_id"

        cursor.execute(query, params)
        missions = cursor.fetchall()
        company_id = get_user_id()
        cursor.execute("SELECT * FROM Astronaut JOIN Person ON Astronaut.id = Person.id WHERE company_id = %s ", (company_id,))
        astronauts = cursor.fetchall()
        num_available_astronauts = len(astronauts)
        
        print(astronauts)

        return render_template("bid_for_mission.html", missions=missions, launch_date_range=launch_date_range, duration_range=duration_range, volume_range=volume_range, weight_range=weight_range, astronauts=astronauts, num_available_astronauts=num_available_astronauts)

    elif request.method == "POST":
        bid_amount = request.form.get("bid_amount")
        astronaut_ids = request.form.getlist("astronaut_ids")
        mission_id = request.form.get("mission_id")
        user_id = get_user_id()
        
        print("MISSION ID IS", mission_id)
        
        cursor.execute("SELECT num_of_astronauts FROM Mission WHERE mission_id = %s", (mission_id,))
        mission = cursor.fetchone()
        required_astronauts = mission['num_of_astronauts'] if mission else 0
        
        print(f"Required astronauts: {required_astronauts}, Selected astronauts: {len(astronaut_ids)}")

        # Check if enough astronauts have been selected
        if len(astronaut_ids) < required_astronauts:
            flash(f"At least {required_astronauts} astronauts are required for this mission.", "error")
            return redirect(url_for("bidForMission"))
    
        try:
            bid_amount = float(bid_amount)
            if bid_amount <= 0:
                flash("Bid amount must be greater than $0.", "error")
                return redirect(url_for("bidForMission"))
    
            # Check for scheduling conflicts before inserting the bid
            cursor.execute("SELECT * FROM Mission where mission_id = %s", (mission_id,))
            current_mission = cursor.fetchone()
            
            conflicts = []
            for astronaut_id in astronaut_ids:
                cursor.execute("""
            SELECT M.title
            FROM Mission_Accepted_Bid MAB
            JOIN Mission M ON MAB.mission_id = M.mission_id
            JOIN Bid_Has_Astronaut BHA ON MAB.bid_id = BHA.bid_id
            JOIN Person ON Person.id = BHA.id
            WHERE BHA.id = %s AND (
                (M.launch_date BETWEEN %s AND DATE_ADD(%s, INTERVAL %s MONTH)) OR 
                (DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) BETWEEN %s AND DATE_ADD(%s, INTERVAL %s MONTH))
            )
        """, (astronaut_id, current_mission['launch_date'], current_mission['launch_date'], current_mission['duration'], current_mission['launch_date'], current_mission['launch_date'], current_mission['duration']))
                result = cursor.fetchone()
                if result:
                    name =  result['title'] + " " + result['rank'] + " " + result['first_name'] + " " + result['last_name']
                    conflicts.append((name, result['title']))  # Append astronaut ID and mission title

                if conflicts:
                    for conflict in conflicts:
                        flash(f"Astronaut Name {conflict[0]} has a scheduling conflict with mission '{conflict[1]}'.", "error")
                    return redirect(url_for("bidForMission"))

            # If no conflicts, proceed to insert the bid
            bid_id = uuid.uuid4().hex
            cursor.execute("INSERT INTO Bid (bid_id, mission_id, bidder_id, amount, bid_date, status) VALUES (%s, %s, %s, %s, CURDATE(), 'Open')", (bid_id, mission_id, user_id, bid_amount))
            mysql.connection.commit()
            
            for astronaut_id in astronaut_ids:
                cursor.execute("INSERT INTO Bid_Has_Astronaut (bid_id, id) VALUES (%s, %s)", (bid_id, astronaut_id))
            mysql.connection.commit()
            return redirect(url_for("bidForMission"))
                
        except ValueError as e:
            mysql.connection.rollback()  # Rollback in case of any error
            flash(f"An error occurred: {str(e)}", "error")
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
    
    current_company_id = get_user_id()
    cursor.execute('''
        SELECT Bid.bid_id, Bid.amount, Bid.bid_date, Bid.status, Mission.title AS mission_title, Company.name AS company_name, employer_id
        FROM Bid
        INNER JOIN Mission ON Bid.mission_id = Mission.mission_id
        INNER JOIN Bidder ON Bid.bidder_id = Bidder.id
        INNER JOIN Company ON Bidder.id = Company.id
        WHERE Mission.employer_id = %s
        ORDER BY Bid.amount DESC
    ''',(current_company_id,))
    bids = cursor.fetchall()
    return render_template("view_bids.html", bids=bids)

@app.route("/admin_page", methods=["GET", "POST"])
def admin():
    redirect_if_not_logged_in = check_logged_in()
    isAdmin= session.get('isAdmin')
    
    if redirect_if_not_logged_in :
        return redirect_if_not_logged_in
    
    if not isAdmin:
        return redirect(url_for('main'))
  
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    admin_id = get_user_id()

    if request.method == 'POST':
        
            if 'delete_reports' in request.form:
                cursor.execute("DELETE FROM SystemReport;")
                mysql.connection.commit()
            
            if 'expensive_mission' in request.form:
                cursor.execute("""
                    INSERT INTO SystemReport (report_id, id, title, content) 
                    SELECT UUID(), %s, 'Most Expensive Missions', CONCAT('Mission ID: ', mission_id, ', Payload Weight: ', payload_weight, ', Title: ', title) 
                    FROM Mission 
                    ORDER BY payload_weight DESC 
                    LIMIT 1;
                """, (admin_id,))
            elif 'mission_status' in request.form:
                cursor.execute("""
                    INSERT INTO SystemReport (report_id, id, title, content)
                    SELECT UUID(), %s, 'Mission Status', 
                    GROUP_CONCAT(
                        CONCAT_WS(', ', 
                            CONCAT('Mission ID: ', M.mission_id),
                            CONCAT('Title: ', M.title),
                            CONCAT('Launch Date: ', M.launch_date),
                            CONCAT('Duration: ', M.duration),
                            CONCAT('Payload Volume: ', M.payload_volume),
                            CONCAT('Payload Weight: ', M.payload_weight),
                            CONCAT('Number of Astronauts: ', M.num_of_astronauts),
                            CONCAT('Status: ', 
                                CASE 
                                    WHEN M.launch_date > CURRENT_DATE THEN 'Upcoming'
                                    WHEN CURRENT_DATE BETWEEN M.launch_date AND DATE_ADD(M.launch_date, INTERVAL M.duration MONTH) THEN 'Ongoing'
                                    ELSE 'Completed'
                                END)
                        ) SEPARATOR ' | '
                    ) AS MissionDetails
                    FROM Mission M;
                """, (admin_id,))

            elif 'astronaut_utilization' in request.form:
                cursor.execute("""
                    INSERT INTO SystemReport (report_id, id, title, content)
                    SELECT UUID(), %s, 'Astronaut Utilization', 
                    GROUP_CONCAT(
                        CONCAT_WS('; ',
                            CONCAT('Astronaut ID: ', A.id),
                            CONCAT('First Name: ', P.first_name),
                            CONCAT('Last Name: ', P.last_name),
                            CONCAT('Missions Assigned: ', AggData.MissionsCount),
                            CONCAT('Trainings Completed: ', AggData.TrainingsCount)
                        ) SEPARATOR ' | '
                    )
                    FROM Astronaut A
                    JOIN Person P ON A.id = P.id
                    LEFT JOIN (
                        SELECT MA.bid_id, COUNT(DISTINCT MA.mission_id) AS MissionsCount,
                            COUNT(DISTINCT AT.training_id) AS TrainingsCount
                        FROM Mission_Accepted_Bid MA
                        LEFT JOIN Astronaut_Completes_Training AT ON MA.bid_id = AT.astronaut_id AND AT.status = 1
                        GROUP BY MA.bid_id
                    ) AggData ON A.id = AggData.bid_id;
                """, (admin_id,))


            elif 'financial_overview' in request.form:
                cursor.execute("""
                    INSERT INTO SystemReport (report_id, id, title, content)
                    SELECT UUID(), %s, 'Financial Overview', 
                    GROUP_CONCAT(
                        CONCAT_WS(', ',
                            CONCAT('Company Name: ', CompanyDetails.name),
                            CONCAT('Total Bids: ', CompanyDetails.TotalBids),
                            CONCAT('Number of Bids: ', CompanyDetails.BidCount),
                            CONCAT('Transactions Amount: ', CompanyDetails.TotalTransactions),
                            CONCAT('Number of Transactions: ', CompanyDetails.TransactionCount)
                        ) SEPARATOR ' | '
                    )
                    FROM (
                        SELECT C.name,
                            SUM(B.amount) AS TotalBids,
                            COUNT(DISTINCT B.bid_id) AS BidCount,
                            SUM(T.amount) AS TotalTransactions,
                            COUNT(DISTINCT T.transaction_id) AS TransactionCount
                        FROM Company C
                        LEFT JOIN Bidder BD ON C.id = BD.id
                        LEFT JOIN Bid B ON BD.id = B.bidder_id
                        LEFT JOIN Transaction T ON BD.id = T.bidder_id
                        GROUP BY C.id
                    ) AS CompanyDetails;
                """, (admin_id,))

            mysql.connection.commit()
        # except MySQLdb.IntegrityError as e:
        #     print(f"Error: {e}")
        #     cursor.close()
        #     flash("Failed to create report. Please ensure you're authorized as an admin.", "error")
        #     return redirect(url_for('admin'))  # Redirect back to admin page with error



    # Retrieve the latest reports for display
    cursor.execute("SELECT report_id, title, content FROM SystemReport")
    reports = cursor.fetchall()
    cursor.close()
    return render_template('admin_page.html', reports=reports)

@app.route("/download_report/<report_id>")
def download_report(report_id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT title, content FROM SystemReport WHERE report_id = %s", (report_id,))
    report = cursor.fetchone()
    cursor.close()
    return Response(report['content'], mimetype="text/plain",
                    headers={"Content-disposition": f"attachment; filename={report['title']}.txt"})

@app.route('/dashboard')
def dashboard():
    redirect_if_not_logged_in = check_logged_in()
    redirect_if_not_astronaut = astronaut_pageguard()
    
    if redirect_if_not_logged_in or redirect_if_not_astronaut:
        print("Not logged in or astronaut")
        return redirect_if_not_logged_in
    
    user_id = get_user_id()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT * FROM Person WHERE id = %s", (user_id,))
    person = cursor.fetchone()
    
    print("CU:",user_id,person)
    
    current_trainings, past_trainings = get_trainings(user_id)
    upcoming_missions, past_missions = get_missions(user_id)

    return render_template('dashboard.html', current_trainings=current_trainings, past_trainings=past_trainings,
                           upcoming_missions=upcoming_missions, past_missions=past_missions, person=person)
    
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
