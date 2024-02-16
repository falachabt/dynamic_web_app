from flask import Flask, render_template, request
from flask_mysqldb import MySQL


app = Flask(__name__)


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
    return render_template('login.html')

@app.route("/list")
def list():
    return render_template("list.html", list=database())

@app.route("/add")
def add(): 
    return render_template("add.html")

if __name__ == '__main__':
    app.run(debug=True)