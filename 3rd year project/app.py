from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import re


# APP SETUP

app = Flask(__name__)
CORS(app)


# DATABASE CONNECTION


def get_connection():

    return pymysql.connect(
        host="mysql-3d71e7bc-studybuddy-alphatech.l.aivencloud.com",
        port=22178,
        user="avnadmin",
        password="AVNS__Is6wf6lEEqmzrAtPwN",
        database="defaultdb",
        cursorclass=pymysql.cursors.DictCursor
    )


# VALIDATION 


def valid_email(email):

    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    return re.match(pattern, email)



def valid_password(password):

    # Password must be between 8 and 10 characters

    if len(password) < 8 or len(password) > 10:
        return False

    # Must contain at least one number

    if not any(char.isdigit() for char in password):
        return False

    return True

# HOME TEST ROUTE

@app.route('/')
def home():

    return jsonify({
        "message": "Study Buddy API Running"
    })


# REGISTER

@app.route('/api/register', methods=['POST'])
def register():

    try:

        data = request.get_json()

        first_name = data.get('first_name', '').strip()
        last_name = data.get('last_name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

       

        
        # VALIDATION

        if len(first_name) > 30:

         return jsonify({
        "message": "First name cannot exceed 30 characters"
    }), 400

        if len(last_name) > 30:

         return jsonify({
        "message": "Last name cannot exceed 30 characters"
    }), 400
        

        if not first_name:

            return jsonify({
                "message": "First name is required"
            }), 400

        if not last_name:

            return jsonify({
                "message": "Last name is required"
            }), 400

        if not email:

            return jsonify({
                "message": "Email is required"
            }), 400

        if not valid_email(email):

            return jsonify({
                "message": "Invalid email address"
            }), 400

        if not valid_password(password):

           return jsonify({
    "message":
    "Password must be 8 to 10 characters long and contain at least one number"
            }), 400
        

        connection = get_connection()

        with connection.cursor() as cursor:

            # Check if email already exists

            cursor.execute(
                """
                SELECT *
                FROM Users
                WHERE Email = %s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                connection.close()

                return jsonify({
                    "message": "Email already exists"
                }), 400

            # Inserts a user

            cursor.execute(
                """
                INSERT INTO Users
                (
                    First_Name,
                    Last_Name,
                    Password,
                    Email,
                    course,
                    Acedemic_year
                )
                VALUES
                (%s,%s,%s,%s,%s,%s)
                """,
                (
                    first_name,
                    last_name,
                    password,
                    email,
                    "General",
                    1
                )
            )

            connection.commit()

        connection.close()

        return jsonify({
            "status": "success",
            "message": "Registration successful"
        }), 201

    except Exception as e:

        print("REGISTER ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Database error"
        }), 500


# LOGIN


@app.route('/api/login', methods=['POST'])
def login():

    try:

        data = request.get_json()

        email = data.get('email', '').strip()
        password = data.get('password', '')

        if len(password) > 10:

         return jsonify({
        "message": "Password cannot exceed 10 characters"
    }), 400

        

        if not email or not password:

            return jsonify({
                "message": "Email and password required"
            }), 400

        connection = get_connection()

        with connection.cursor() as cursor:

            cursor.execute(
                """
                SELECT *
                FROM Users
                WHERE Email = %s
                AND Password = %s
                """,
                (
                    email,
                    password
                )
            )

            user = cursor.fetchone()

        connection.close()

        if user:

            return jsonify({
                "status": "success",
                "message": "Login successful",
                "user_id": user["User_id"],
                "first_name": user["First_Name"],
                "last_name": user["Last_Name"]
            }), 200

        return jsonify({
            "status": "error",
            "message": "Invalid email or password"
        }), 401

    except Exception as e:

        print("LOGIN ERROR:", e)

        return jsonify({
            "status": "error",
            "message": "Database error"
        }), 500


# TEST API


@app.route('/api/data', methods=['POST'])
def handle_api_request():

    incoming_data = request.get_json()

    username = incoming_data.get('user')

    print(f"Saving {username} to the database...")

    return jsonify({
        "status": "success",
        "message": f"Data for {username} received!",
        "code": 201
    })


# RUN SERVER


if __name__ == '__main__':

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )