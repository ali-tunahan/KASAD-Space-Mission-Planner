import re
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import uuid
from flask import Response


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
            print("im here")
            
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
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT name, training_id, code, description, duration, IFNULL(GROUP_CONCAT(prereq_id), Null) AS prereq_ids FROM Training LEFT JOIN Training_Prerequisite_Training ON training_id = train_id GROUP BY training_id')
    trainings = cursor.fetchall()   
    cursor.execute('SELECT * FROM Astronaut')
    astronauts = cursor.fetchall()
    return render_template("assign_trainings.html", trainings = trainings,astronauts=astronauts)


@app.route("/bid_for_mission", methods=["GET", "POST"])
def bidForMission():

    return render_template("bid_for_mission.html")

@app.route("/admin_page", methods=["GET", "POST"])
def admin():
    admin_id = session['userid']  # Assuming the admin's user ID is stored in session
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)

    if request.method == 'POST':
        
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
                                    WHEN CURRENT_DATE BETWEEN M.launch_date AND DATE_ADD(M.launch_date, INTERVAL M.duration DAY) THEN 'Ongoing'
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
                        )
                    )
                    FROM Astronaut A
                    JOIN Person P ON A.id = P.id
                    LEFT JOIN (
                        SELECT MA.bid_id, COUNT(DISTINCT MA.mission_id) as MissionsCount,
                            COUNT(DISTINCT AT.training_id) as TrainingsCount
                        FROM Mission_Accepted_Bid MA
                        LEFT JOIN Astronaut_Completes_Training AT ON MA.bid_id = AT.astronaut_id AND AT.status = 1
                        GROUP BY MA.bid_id
                    ) AggData ON A.id = AggData.bid_id
                    GROUP BY A.id;
                """, (admin_id,))

            elif 'financial_overview' in request.form:
                cursor.execute("""
                    INSERT INTO SystemReport (report_id, id, title, content)
                    SELECT UUID(), %s, 'Financial Overview', 
                    CONCAT_WS(', ',
                            CONCAT('Company Name: ', C.name),
                            CONCAT('Total Bids: ', SUM(B.amount)),
                            CONCAT('Number of Bids: ', COUNT(DISTINCT B.bid_id)),
                            CONCAT('Transactions Amount: ', SUM(T.amount)),
                            CONCAT('Number of Transactions: ', COUNT(DISTINCT T.transaction_id)))
                    FROM Company C
                    LEFT JOIN Bidder BD ON C.id = BD.id
                    LEFT JOIN Bid B ON BD.id = B.bidder_id
                    LEFT JOIN Transaction T ON BD.id = T.bidder_id
                    GROUP BY C.id;
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


@app.errorhandler(404)
def page_not_found(e):
    # Note 'e' is the error object
    return render_template('error_page.html'), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(debug=True, host="0.0.0.0", port=port)
