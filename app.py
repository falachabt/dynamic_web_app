from flask import Flask, render_template, request, redirect, url_for, session
from flask_mysqldb import MySQL
from utils.auth import Usersignup, Userlogin, check_user_exists


app = Flask(__name__)
app.secret_key = '12345678'


app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'PBLMIA11'
mysql = MySQL(app)
 

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
    return render_template("list.html", list=database())

@app.route("/add")
def add(): 
    return render_template("add.html")




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