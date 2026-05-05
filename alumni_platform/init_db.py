import sqlite3
import os
from werkzeug.security import generate_password_hash

DB_FILE = 'database.db'

def init_db():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL, -- 'student', 'alumni', 'admin'
            fullname TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Profiles table
    c.execute('''
        CREATE TABLE profiles (
            user_id INTEGER PRIMARY KEY,
            department TEXT,
            branch TEXT,
            year TEXT, -- passout year or current year
            company TEXT,
            designation TEXT,
            skills TEXT,
            interests TEXT,
            achievements TEXT,
            resume TEXT,
            mentor_willing INTEGER DEFAULT 1,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    # Mentorship requests
    c.execute('''
        CREATE TABLE mentorship_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            alumni_id INTEGER,
            status TEXT DEFAULT 'pending', -- 'pending', 'accepted', 'rejected'
            FOREIGN KEY(student_id) REFERENCES users(id),
            FOREIGN KEY(alumni_id) REFERENCES users(id)
        )
    ''')
    
    # Opportunities
    c.execute('''
        CREATE TABLE opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            description TEXT,
            skills TEXT,
            deadline TEXT,
            posted_by_id INTEGER,
            FOREIGN KEY(posted_by_id) REFERENCES users(id)
        )
    ''')
    
    # Events
    c.execute('''
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT,
            time TEXT,
            venue TEXT,
            description TEXT,
            posted_by_id INTEGER,
            FOREIGN KEY(posted_by_id) REFERENCES users(id)
        )
    ''')
    
    # Insert Demo Data
    admin_pw = generate_password_hash('admin123')
    student_pw = generate_password_hash('student123')
    alumni_pw = generate_password_hash('alumni123')
    
    c.execute("INSERT INTO users (role, fullname, email, password_hash) VALUES (?, ?, ?, ?)",
              ('admin', 'System Admin', 'admin@example.com', admin_pw))
              
    c.execute("INSERT INTO users (role, fullname, email, password_hash) VALUES (?, ?, ?, ?)",
              ('student', 'Ravi Kumar', 'student@example.com', student_pw))
    student_id = c.lastrowid
    
    c.execute("INSERT INTO profiles (user_id, department, branch, year, skills, interests) VALUES (?, ?, ?, ?, ?, ?)",
              (student_id, 'Engineering', 'Computer Science', '3rd Year', 'Python, React', 'AI, Web Dev'))
              
    c.execute("INSERT INTO users (role, fullname, email, password_hash) VALUES (?, ?, ?, ?)",
              ('alumni', 'Priya Sharma', 'alumni@example.com', alumni_pw))
    alumni_id = c.lastrowid
              
    c.execute("INSERT INTO profiles (user_id, department, branch, year, company, designation, skills, mentor_willing) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
              (alumni_id, 'Engineering', 'Computer Science', '2020', 'Google', 'Software Engineer', 'Python, Cloud', 1))
              
    c.execute("INSERT INTO opportunities (title, company, description, skills, deadline, posted_by_id) VALUES (?, ?, ?, ?, ?, ?)",
              ('Software Engineering Intern', 'Google', 'Looking for smart interns.', 'Python, DSA', '2026-08-01', alumni_id))
              
    c.execute("INSERT INTO events (title, date, time, venue, description, posted_by_id) VALUES (?, ?, ?, ?, ?, ?)",
              ('Tech Meetup 2026', '2026-06-15', '10:00 AM', 'Main Auditorium', 'Annual alumni and student tech meetup.', 1))
    
    conn.commit()
    conn.close()
    print("Database initialized successfully with demo data.")

if __name__ == '__main__':
    init_db()
