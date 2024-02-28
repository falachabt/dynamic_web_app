from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import hashlib

def Usersignup(mysql, email, password, secret):
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
                    role VARCHAR(50) NOT NULL
                )
            """)
            
        # issue with password hash
        # hashed_password = generate_password_hash(password)
        role = getRole(secret)
        
        if role is None:
            raise ValueError("Wrong secret")
            
        cur.execute("INSERT INTO users (email, password, role) VALUES (%s, %s, %s)", (email, hash(password), role))
        mysql.connection.commit()
        cur.close()
        return True, None
    except Exception as e:
        error_message = str(e)
        print(error_message)
        return False, error_message

def Userlogin(mysql : MySQL, email : str, password: str):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s AND password = %s " , (email,hash(password)))
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

def check_user_exists(mysql: MySQL, email: str):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user is not None, None
    except Exception as e:
        error_message = str(e)
        return False, error_message
    
    
def getRole(secret):
    match secret:
        case "board":
            return "admin"
        case "2027":
            return "student"
        case "other":
            return None

def hash(data):
    # Using SHA-1 hashing algorithm
    hash_object = hashlib.sha1(data.encode())
    # Getting the hexadecimal representation of the hash and taking the first 20 characters
    return hash_object.hexdigest()[:20]