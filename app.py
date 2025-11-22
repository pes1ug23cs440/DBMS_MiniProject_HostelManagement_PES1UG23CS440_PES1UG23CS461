from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Database Configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Praneet@2004',  
    'database': 'hostel_management'
}

def get_db_connection():
    """Create and return a database connection"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def init_database():
    """Initialize the database with the schema (runs multi-statement SQL including triggers)."""
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()

        # Create database if not exists
        cursor.execute("CREATE DATABASE IF NOT EXISTS hostel_management")
        cursor.execute("USE hostel_management")

        # Read entire SQL file (schema + triggers/functions)
        sql_path = 'schema.sql'
        if not os.path.exists(sql_path):
            print(f"schema.sql not found at {sql_path}. Skipping initialization.")
            return

        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_commands = f.read()

        # mysql.connector supports multi statement execution via cursor.execute(..., multi=True)
        for result in cursor.execute(sql_commands, multi=True):
            # consume results to ensure all statements run
            pass

        connection.commit()
        print("Database initialized successfully!")

    except Error as e:
        print(f"Error initializing database: {e}")
    finally:
        try:
            if connection.is_connected():
                cursor.close()
                connection.close()
        except Exception:
            pass

# Routes for serving HTML pages
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students')
def students_page():
    return render_template('students.html')

@app.route('/rooms')
def rooms_page():
    return render_template('rooms.html')

@app.route('/mess')
def mess_page():
    return render_template('mess.html')

@app.route('/wardens')
def wardens_page():
    return render_template('wardens.html')

@app.route('/laundry')
def laundry_page():
    return render_template('laundry.html')

# -----------------
# API Endpoints
# -----------------

# Students API
@app.route('/api/students', methods=['GET'])
def get_students():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, 
                   srf.r_no, 
                   f.amount as fees_paid, 
                   f.p_date,
                   f.p_method,
                   m.m_name as mess_name,
                   lg.name as guardian_name,
                   lg.p_no as guardian_phone
            FROM student s
            LEFT JOIN student_room_fees srf ON s.s_id = srf.s_id
            LEFT JOIN fees f ON srf.p_id = f.p_id
            LEFT JOIN books_mess bm ON s.s_id = bm.s_id
            LEFT JOIN mess m ON bm.m_no = m.m_no
            LEFT JOIN local_guardian lg ON s.s_id = lg.s_id
        """)
        students = cursor.fetchall()
        return jsonify(students)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/students/<student_id>', methods=['GET'])
def get_student(student_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, 
                   srf.r_no, 
                   f.amount as fees_paid, 
                   f.p_date,
                   m.m_name as mess_name
            FROM student s
            LEFT JOIN student_room_fees srf ON s.s_id = srf.s_id
            LEFT JOIN fees f ON srf.p_id = f.p_id
            LEFT JOIN books_mess bm ON s.s_id = bm.s_id
            LEFT JOIN mess m ON bm.m_no = m.m_no
            WHERE s.s_id = %s
        """, (student_id,))
        student = cursor.fetchone()
        if student:
            return jsonify(student)
        return jsonify({'error': 'Student not found'}), 404
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/students', methods=['POST'])
def add_student():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()

        # Insert student
        cursor.execute("""
            INSERT INTO student (s_id, f_name, m_name, l_name, p_no, leader_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data['s_id'], data['f_name'], data.get('m_name'),
              data['l_name'], data['p_no'], data.get('leader_id')))

        # Insert local guardian if provided
        if 'guardian_name' in data and 'guardian_phone' in data:
            cursor.execute("""
                INSERT INTO local_guardian (s_id, name, p_no)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE name = VALUES(name)
            """, (data['s_id'], data['guardian_name'], data['guardian_phone']))

        connection.commit()
        return jsonify({'message': 'Student added successfully'}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()

        cursor.execute("""
            UPDATE student 
            SET f_name = %s, m_name = %s, l_name = %s, p_no = %s, leader_id = %s
            WHERE s_id = %s
        """, (data['f_name'], data.get('m_name'), data['l_name'],
              data['p_no'], data.get('leader_id'), student_id))

        connection.commit()
        return jsonify({'message': 'Student updated successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor()
        cursor.execute("DELETE FROM student WHERE s_id = %s", (student_id,))
        connection.commit()
        return jsonify({'message': 'Student deleted successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Rooms API
@app.route('/api/rooms', methods=['GET'])
def get_rooms():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM room ORDER BY r_no")
        rooms = cursor.fetchall()
        return jsonify(rooms)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/rooms/<room_no>/students', methods=['GET'])
def get_room_students(room_no):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.s_id, s.f_name, s.m_name, s.l_name, s.p_no, srf.allotment_date
            FROM student s
            JOIN student_room_fees srf ON s.s_id = srf.s_id
            WHERE srf.r_no = %s
        """, (room_no,))
        students = cursor.fetchall()
        return jsonify(students)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/rooms/<room_no>/available', methods=['GET'])
def get_room_available_slots(room_no):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT room_available_slots(%s) as available", (room_no,))
        row = cursor.fetchone()
        available = row[0] if row else 0
        return jsonify({'r_no': room_no, 'available_slots': int(available)})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/rooms/allocate', methods=['POST'])
def allocate_room():
    """
    Allocates a room to a student:
    - creates a fees record
    - inserts student_room_fees row (triggers will update room occupancy and validate)
    NOTE: trigger will reject allocation if room is full or student already allocated.
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()

        # Compose a unique fee id
        from uuid import uuid4
        fee_id = f"F{uuid4().hex[:18].upper()}"


        # Start transaction
        cursor.execute("START TRANSACTION")

        # Create fee record
        cursor.execute("""
            INSERT INTO fees (p_id, p_date, p_method, amount)
            VALUES (%s, %s, %s, %s)
        """, (fee_id, datetime.now().date(), data['p_method'], data['amount']))

        # Allocate room (insert triggers will update occupancy and validate capacity/student allocation)
        cursor.execute("""
            INSERT INTO student_room_fees (s_id, r_no, p_id, allotment_date)
            VALUES (%s, %s, %s, %s)
        """, (data['s_id'], data['r_no'], fee_id, datetime.now().date()))

        connection.commit()
        return jsonify({'message': 'Room allocated successfully'}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/rooms/deallocate', methods=['POST'])
def deallocate_room():
    """
    Deallocate a student from a room by deleting the student_room_fees entry.
    The AFTER DELETE trigger will decrement room.no_of_people.
    Request body: { "s_id": "...", "r_no": "..." }
    """
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()
        cursor.execute("START TRANSACTION")

        # Delete the allocation row (will cascade if fees is set to CASCADE; triggers will update room occupancy)
        cursor.execute("""
            DELETE FROM student_room_fees
            WHERE s_id = %s AND r_no = %s
        """, (data['s_id'], data['r_no']))

        if cursor.rowcount == 0:
            connection.rollback()
            return jsonify({'error': 'Allocation not found'}), 404

        connection.commit()
        return jsonify({'message': 'Deallocated successfully'})
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Mess API
@app.route('/api/mess', methods=['GET'])
def get_mess():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM mess")
        mess = cursor.fetchall()
        return jsonify(mess)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/mess/book', methods=['POST'])
def book_mess():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO books_mess (s_id, m_no, booking_date)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE m_no = %s, booking_date = %s
        """, (data['s_id'], data['m_no'], datetime.now().date(),
              data['m_no'], datetime.now().date()))

        connection.commit()
        return jsonify({'message': 'Mess booked successfully'}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Wardens API
@app.route('/api/wardens', methods=['GET'])
def get_wardens():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT w.*, COUNT(m.s_id) as student_count
            FROM warden w
            LEFT JOIN monitors m ON w.w_id = m.w_id
            GROUP BY w.w_id
        """)
        wardens = cursor.fetchall()
        return jsonify(wardens)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/wardens/<warden_id>/students', methods=['GET'])
def get_warden_students(warden_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT s.*, m.assigned_date
            FROM student s
            JOIN monitors m ON s.s_id = m.s_id
            WHERE m.w_id = %s
        """, (warden_id,))
        students = cursor.fetchall()
        return jsonify(students)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Laundry API
@app.route('/api/laundry', methods=['GET'])
def get_laundry():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM laundry")
        laundry = cursor.fetchall()
        return jsonify(laundry)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

@app.route('/api/laundry/submit', methods=['POST'])
def submit_laundry():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        data = request.json
        cursor = connection.cursor()

        cursor.execute("""
            INSERT INTO gives_laundry (s_id, l_no, submission_date)
            VALUES (%s, %s, %s)
        """, (data['s_id'], data['l_no'], datetime.now().date()))

        connection.commit()
        return jsonify({'message': 'Laundry submitted successfully'}), 201
    except Error as e:
        connection.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# New endpoint: student total payments using stored function
@app.route('/api/students/<student_id>/payments', methods=['GET'])
def get_student_payments(student_id):
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT student_total_paid(%s) as total", (student_id,))
        row = cursor.fetchone()
        total = float(row[0]) if row and row[0] is not None else 0.0
        return jsonify({'s_id': student_id, 'total_paid': total})
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

# Dashboard Statistics
@app.route('/api/dashboard/stats', methods=['GET'])
def get_dashboard_stats():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection failed'}), 500

    try:
        cursor = connection.cursor(dictionary=True)

        stats = {}

        # Total students
        cursor.execute("SELECT COUNT(*) as count FROM student")
        stats['total_students'] = cursor.fetchone()['count']

        # Total rooms
        cursor.execute("SELECT COUNT(*) as count FROM room")
        stats['total_rooms'] = cursor.fetchone()['count']

        # Occupied rooms
        cursor.execute("SELECT COUNT(*) as count FROM room WHERE no_of_people > 0")
        stats['occupied_rooms'] = cursor.fetchone()['count']

        # Total revenue
        cursor.execute("SELECT SUM(amount) as total FROM fees")
        result = cursor.fetchone()
        stats['total_revenue'] = float(result['total']) if result['total'] else 0

        # Mess bookings
        cursor.execute("SELECT COUNT(*) as count FROM books_mess")
        stats['mess_bookings'] = cursor.fetchone()['count']

        return jsonify(stats)
    except Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        connection.close()

if __name__ == '__main__':
    # Uncomment the line below to initialize database on first run
    #init_database()
    app.run(debug=True, host='0.0.0.0', port=5000)
