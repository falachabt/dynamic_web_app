from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

def Usersignup(mysql, email, password):
    try:
        cur = mysql.connection.cursor()
        # Check if users table exists
        cur.execute("SHOW TABLES LIKE 'users'")
        if cur.fetchone() is None:
            # Create users table if it doesn't exist
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(30) UNIQUE NOT NULL,  
                    password VARCHAR(90) NOT NULL,
                    role VARCHAR(50)
                )
            """)
            
        # issue with password hash
        # hashed_password = generate_password_hash(password)
        cur.execute("INSERT INTO users (email, password) VALUES (%s, %s)", (email, password))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        error_message = str(e)
        return False, error_message

def Userlogin(mysql : MySQL, email : str, password: str):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s " , (email,password))
        user = cur.fetchone()
        cur.close()
        
        # if pw_hash and check_password_hash(pw_hash, password):
        if user :
            return user, None
        else:
            return None, "Invalid email or password"
    except Exception as e:
        error_message = str(e)
        return None, error_message

def check_user_exists(mysql, email):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user is not None, None
    except Exception as e:
        error_message = str(e)
        return False, error_message