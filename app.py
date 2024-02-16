from flask import Flask, render_template
from flask_mysqldb import MySQL

app = Flask(__name__)


app.config['MYSQL_HOST'] = '127.0.0.1'
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

    # Generate HTML code to display the data in a table
    htmlCode = "<table border='1'>"
    htmlCode += "<tr>"
    htmlCode += "<th>Student Mail</th>"
    htmlCode += "<th>Campus Name</th>"
    htmlCode += "</tr>"

    for row in rows:
        htmlCode += "<tr>"
        htmlCode += "<td>" + str(row[0]) + "</td>"
        htmlCode += "<td>" + str(row[1]) + "</td>"
        htmlCode += "</tr>"

    htmlCode += "</table>"

    return htmlCode


@app.route('/')
def hello():
    return render_template('index.html')


@app.route("/list")
def list():
    return render_template("list.html", list=database())

@app.route("/add")
def add(): 
    return render_template("add.html")

if __name__ == '__main__':
    app.run(debug=True)