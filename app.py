from flask import Flask, render_template, session, redirect, url_for, flash
from flask import request
from flask_mysqldb import MySQL
from utils.auth import Usersignup, Userlogin, check_user_exists
import os

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

def hash(data):
    # Using SHA-1 hashing algorithm
    hash_object = hashlib.sha1(data.encode())
    # Getting the hexadecimal representation of the hash and taking the first 20 characters
    return hash_object.hexdigest()[:20]

def studentList(dev):
    # Create a cursor object
    cur = mysql.connection.cursor()

    htmlCode = ""

    if dev:
        args = 'idMobilityWish, studentMail, campus.campusName'
    else:
        args = 'studentMail, campus.campusName'

    cur.execute("SELECT " + args + " FROM mobilitywish JOIN campus ON mobilitywish.Campus_idCampus = campus.idCampus ORDER BY idMobilityWish")
    for rows in cur.fetchall():
        if not dev:
            htmlCode += "<tr><td><a href='mailto:" + str(rows[0]) +"'>" + str(rows[0]) +"</a></td><td>" + str(rows[1]) + '</td>'
        elif dev:
            htmlCode += "<tr>"
            for col in rows:
                htmlCode += "<td>" + str(col) + '</td>'
            htmlCode += '<td style="text-align:end"><a type = "submit" href = "/api/deleteStudent?mid=' + str(rows[0]) + '" ><img src="static/glyphs/cross.png" class="glyph" alt=""></a></td>'
        htmlCode += '</tr>'

    cur.close()
    
    return htmlCode

def campusList(arg, dev):
    try:
        cur = mysql.connection.cursor()
        htmlCode = ""
        cur.execute("SELECT " + arg + " FROM Campus ORDER BY idCampus")
        for rows in cur.fetchall():
            htmlCode += "<tr>"
            for col in rows:
                htmlCode += "<td>" + str(col) + '</td>'
            if dev:
                htmlCode += '<td style="text-align:end"><a type = "submit" href = "/api/deleteCampus?cid=' + str(rows[0]) + '" ><img src="static/glyphs/cross.png" class="glyph" alt=""></a></td>'
            htmlCode += '</tr>'
        cur.close()
        return htmlCode
    except Exception as e:
        error_message = str(e)
        return  error_message

@app.route('/addCampus', methods =['POST'])
def addCampus():
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(idCampus) FROM Campus")
    campusCount = cur.fetchall()[0][0] + 1
    sql = "INSERT INTO Campus(idCampus, campusName) VALUES (%s, %s)"
    val = (campusCount, request.values['campusName'])
    cur.execute(sql,val)
    mysql.connection.commit()
    return redirect(url_for('admin'))

@app.route('/addStudent', methods =['POST'])
def addStudent():
    cur = mysql.connection.cursor()
    cur.execute("SELECT MAX(idmobilitywish) FROM mobilitywish")
    studentCount = cur.fetchall()[0][0] + 1
    sql = "INSERT INTO mobilitywish(idmobilitywish, studentmail, Campus_idCampus) VALUES (%s, %s, %s)"
    val = (studentCount, request.values['studentMail'], request.values['idCampus'])
    cur.execute(sql,val)
    mysql.connection.commit()
    userType = session.get("userType")
    match userType:
        case "amdin":
            return redirect(url_for('admin'))
        case "student":
            return redirect(url_for('choices'))
      
            
@app.route('/addStudent1', methods =['POST'])
def addStudent1():
    try:
        cur = mysql.connection.cursor()
        
        email = session.get("email")
        
        tesql = '''SELECT * FROM mobilitywish WHERE studentmail = %s '''
        cur.execute(tesql, (email,))
        exist = None
        data = cur.fetchall()
        if(len(data) != 0):
            exist = data[0][0]  
        
        if exist is None:
            cur.execute("SELECT MAX(idmobilitywish) FROM mobilitywish")
            sql = "INSERT INTO mobilitywish(idmobilitywish, studentmail, Campus_idCampus) VALUES (%s, %s, %s)"
            idMobi = cur.fetchall()[0][0] + 1
            val = (idMobi, email, request.values['idCampus'])
            cur.execute(sql,val)
            mysql.connection.commit()
        else : 
            return redirect(url_for("apply", error = "you have already apply"))
            
        userType = session.get("userType")
        match userType:
            case "amdin":
                return redirect(url_for('admin'))
            case "student":
                return redirect(url_for('choices'))
    except Exception as e:
        message = str(e)
        print(message)
        # print("Duplicata" in message)
        flash("")
        return redirect(url_for("apply"))
            

@app.route('/')
def hello():
    return render_template('index.html', campusList = campusList('campusName', False))

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
       return redirect(url_for("choices"))
        
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
        session.pop("userType")
    return redirect(url_for("login"))

@app.route('/redirectPage')
def redirectPage():
    return render_template("redirect.html", lastPage = admin())

@app.route("/list")
def list():
    return render_template("list.html", list = studentList(False))

@app.route("/admin")
def admin():
    userType = session.get("userType")
    if(userType != "admin"):
        return render_template("login.html")
    else:
        return render_template("admin.html", campusList = campusList('*', True), studentList = studentList(True))

@app.route("/apply")
def apply(): 
    cur = mysql.connection.cursor()
    query = '''SELECT * FROM campus'''
    cur.execute(query)
    campuses = cur.fetchall()
    error = request.args.get('error')
    
    return render_template("apply.html", campuses = campuses, error = error)

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
        secret = request.form.get("secret")
        [ exist, message ] = check_user_exists(mysql, email); 

        if not exist:
            [ success, er_message ] =  Usersignup(mysql, email, password, secret)
            if success is False:
                return redirect(url_for("signup",error = "wrong secret" ), ) 
            
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
            session["userType"] = user[3]
            session['user'] = user[0]
            session['email'] = email
            return redirect(url_for("choices"))
        else:
            return redirect(url_for("login", error = "Invalid email or password"))
    else:
        return redirect(url_for("login", error = "Invalid request method"))

@app.route('/api/deleteCampus')
def deleteCampus():
    try:
        cur = mysql.connection.cursor()
        query = 'DELETE FROM Campus WHERE idCampus=' + str(request.values.get('cid'))
        print(query)
        cur.execute(query)
        mysql.connection.commit()
        cur.close()
        return redirect(url_for("admin"))
    except Exception as e:
        message = e
        if "FOREIGN" in str(e):
            message = "Cannot delete, students have already applied for this campus."
        flash(message)
        return redirect(url_for("admin", message = e))



@app.route("/upload", methods=["POST"])
def upload_file():
    uploaded_file = request.files["file"]
    if uploaded_file.filename != "":
        # Save the file to a temporary location
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], uploaded_file.filename)
        uploaded_file.save(file_path)

        # Insert the file content into the database
        conn = mysql.connection
        cursor = conn.cursor()
        with open(file_path, "rb") as file:
            file_content = file.read()
            cursor.execute("INSERT INTO files (file_content) VALUES (%s)", (file_content,))
        conn.commit()
        cursor.close()

        return "File uploaded and saved successfully!"
    else:
        return "No file selected."
@app.route('/api/deleteStudent')
def deleteStudent():
    cur = mysql.connection.cursor()
    query = 'DELETE FROM mobilityWish WHERE idMobilityWish=' + str(request.values.get('mid'))
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return redirect(url_for("admin"))

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    app.run(debug=True)