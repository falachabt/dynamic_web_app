from flask import Flask, render_template, session, redirect, url_for
from flask import request
from flask_mysqldb import MySQL
from utils.auth import Usersignup, Userlogin, check_user_exists


app = Flask(__name__)


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'PBLMIA11'
mysql = MySQL(app)

app.secret_key = '12345678'
 
admin_code = "board_123"
student_code = "2027" 

def database():
    # Create a cursor object
    cur = mysql.connection.cursor()

    # Execute the SQL query to select data from the table
    cur.execute("SELECT * FROM campus")
    # cur.execute("SELECT studentMail, campusName FROM mobilitywish JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus")

    # Fetch all the results
    rows = cur.fetchall()

    # Close the cursor
    cur.close()

    return rows

def custom_hash(data):
    # Using SHA-1 hashing algorithm
    hash_object = hashlib.sha1(data.encode())
    # Getting the hexadecimal representation of the hash and taking the first 20 characters
    return hash_object.hexdigest()[:20]

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
    return render_template("redirect.html", path = '<meta http-equiv="refresh" content="0; url=http://127.0.0.1:5000/admin" />')

@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/choices')
def choices():
    search_query = request.args.get('search')

    # Initialize the cursor before using it
    cur = mysql.connection.cursor()

    if search_query:
        # Use parameterized queries to prevent SQL injection
        query = '''
            SELECT studentMail, campusName 
            FROM mobilitywish 
            JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus 
            WHERE mobilitywish.studentMail LIKE %s 
            OR campus.campusName LIKE %s ORDER BY studentMail   
        '''
        search_term = '%' + search_query + '%'
        cur.execute(query, (search_term, search_term))
    else:
        cur.execute('''
            SELECT studentMail, campusName 
            FROM mobilitywish 
            JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus ORDER BY studentMail 
        ''')

    # Fetch the results after executing the query
    wishes = cur.fetchall()

    # Close the cursor after fetching the results
    cur.close()

    return render_template('choices.html', choices=wishes, search = search_query)


@app.route('/login')
def login(): 
    print(session.get("user"))
    if(session.get("user")):
       return redirect(url_for("list"))
        
    error = request.args.get('error')
    return render_template('login.html', error = error)

@app.route('/signup')
def signup(): 
    error = request.args.get('error')
    return render_template('signup.html', error = error)

@app.route('/logout')
def logout():
    if(session.get("user")):
        session.pop("user")
    return redirect(url_for("login"))



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

'''
API ROUTES
'''
@app.route('/api/signup', methods=['POST'])
def signup_api():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        [ exist, message ] = check_user_exists(mysql, email); 
        print(exist)
        print(message)
        if not exist:
            [ success, er_message ] =  Usersignup(mysql, email, password)
            print(success)
            print(er_message)
            return redirect(url_for("login"))
        else:
            return  redirect(url_for("signup", error = "User already exists" ))
    else:
        return redirect(url_for("signup", error = "Invalid request method" ))

@app.route('/api/login', methods=['POST'])
def login_api():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        [user, errormessage ] = Userlogin(mysql, email, password)
       
        if user != None:
            session['user'] = user[0]
            return redirect(url_for("list"))
        else:
            return redirect(url_for("login", error = "Invalid email or password"))
    else:
        return redirect(url_for("login", error = "Invalid request method"))

if __name__ == '__main__':
    app.run(debug=True)