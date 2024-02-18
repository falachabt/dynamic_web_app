from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)


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
    # Create a cursor object
    cur = mysql.connection.cursor()

    htmlCode = ""

    cur.execute("SELECT " + arg + " FROM Campus ")
    for rows in cur.fetchall():
        htmlCode += "<tr>"
        for col in rows:
             htmlCode += "<td>" + str(col) + '</td>'
        htmlCode += '</tr>'

    cur.close()
    
    return htmlCode

@app.route('/')
def hello():
    return render_template('index.html', campusList = campusList('campusName'))

@app.route("/list")
def list():
    return render_template("list.html", list = studentList())

@app.route("/admin")
def admin():
    return render_template("admin.html", campusList = campusList('*'))

@app.route("/add")
def add(): 
    return render_template("add.html")

if __name__ == '__main__':
    app.run(debug=True)