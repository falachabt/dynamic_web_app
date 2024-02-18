from flask import Flask, render_template, session, redirect, url_for
from flask import request
from flask_mysqldb import MySQL

app = Flask(__name__)
app.secret_key = "123456789"


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'PBLMIA11'
mysql = MySQL(app)
 
#this function is called to generate the home page of your website

def database():
    # Create a cursor object
    cur = mysql.connection.cursor()

    # Execute the SQL query to select data from the table
    cur.execute("SELECT studentMail, campusName FROM mobilitywish JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus")

    # Fetch all the results
    rows = cur.fetchall()

    # Close the cursor
    cur.close()

    return rows

def studentList():
    # Create a cursor object
    cur = mysql.connection.cursor()

    htmlCode = ""

    cur.execute("SELECT studentMail, campusName FROM mobilitywish JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus")
    for rows in cur.fetchall():
        htmlCode += "<tr><td><a href='mailto:" + str(rows[0]) +"'>" + str(rows[0]) +"</a></td><td>" + str(rows[1]) + '</td></tr>'

    cur.close()
    
    return htmlCode

def campusList(arg):
    try:
        cur = mysql.connection.cursor()
        htmlCode = ""
        cur.execute("SELECT " + arg + " FROM Campus ORDER BY idCampus")
        for rows in cur.fetchall():
            htmlCode += "<tr>"
            for col in rows:
                htmlCode += "<td>" + str(col) + '</td>'
            htmlCode += '</tr>'
        cur.close()
        return htmlCode
    except Exception as e:
        error_message = str(e)
        print(error_message)
        return  error_message

@app.route('/addCampus', methods =['POST'])
def addCampus():
    cur = mysql.connection.cursor()
    sql = "INSERT INTO Campus(idCampus, campusName) VALUES (%s, %s)"
    val = (request.values['campusIndex'], request.values['campusName'])
    cur.execute(sql,val)
    mysql.connection.commit()
    return render_template("admin.html", campusList = campusList('*'))

@app.route('/')
def hello():
    return render_template('index.html', campusList = campusList('campusName'))

@app.route("/list")
def list():
    return render_template("list.html", list = studentList())

@app.route("/admin")
def admin():
    userType = session.get("userType")
    if(userType != "admin"):
        return render_template("login.html")
    else:
        return render_template("admin.html", campusList = campusList('*'))

@app.route("/apply")
def apply(): 
    return render_template("apply.html", resume = render_template('apply/resume.html'), coverLetter = render_template('apply/coverLetter.html'), destination = render_template('apply/destination.html'))

#api routes 
@app.route("/adminLogin", methods = ['POST'] )
def adminLogin(): 
    session["userType"] = "admin"
    return redirect(url_for("admin"))
    




if __name__ == '__main__':
    app.run(debug=True)