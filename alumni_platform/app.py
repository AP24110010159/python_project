import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'super_secret_key'
DB_FILE = 'database.db'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        role = request.form['role']
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        cursor = conn.cursor()
        
        try:
            cursor.execute("INSERT INTO users (role, fullname, email, password_hash) VALUES (?, ?, ?, ?)",
                           (role, fullname, email, generate_password_hash(password)))
            user_id = cursor.lastrowid
            
            # Create an empty profile
            cursor.execute("INSERT INTO profiles (user_id) VALUES (?)", (user_id,))
            conn.commit()
            
            flash('Registration successful. Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered.', 'error')
        finally:
            conn.close()
            
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()
        
        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['fullname'] = user['fullname']
            
            flash(f"Welcome back, {user['fullname']}!", 'success')
            if user['role'] == 'student':
                return redirect(url_for('student_dashboard'))
            elif user['role'] == 'alumni':
                return redirect(url_for('alumni_dashboard'))
            else:
                return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid email or password.', 'error')
            
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('index'))

@app.route('/student_dashboard')
def student_dashboard():
    if 'user_id' not in session or session['role'] != 'student':
        return redirect(url_for('login'))
    
    conn = get_db()
    # Get user profile
    profile = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (session['user_id'],)).fetchone()
    
    # Recommendation logic (Smart Matching based on same branch or skills overlap)
    branch = profile['branch'] if profile and profile['branch'] else ''
    
    query = """
        SELECT u.id, u.fullname, p.company, p.designation, p.skills, p.branch 
        FROM users u 
        JOIN profiles p ON u.id = p.user_id 
        WHERE u.role = 'alumni' AND p.mentor_willing = 1
    """
    params = []
    
    if branch:
        query += " AND p.branch = ? LIMIT 3"
        params.append(branch)
    else:
        query += " LIMIT 3"
        
    recommended_alumni = conn.execute(query, params).fetchall()
    
    # Recent Opportunities
    opportunities = conn.execute("SELECT * FROM opportunities ORDER BY id DESC LIMIT 3").fetchall()
    
    conn.close()
    return render_template('student_dashboard.html', recommended_alumni=recommended_alumni, opportunities=opportunities)

@app.route('/alumni_dashboard')
def alumni_dashboard():
    if 'user_id' not in session or session['role'] != 'alumni':
        return redirect(url_for('login'))
        
    conn = get_db()
    # Mentorship requests received
    requests = conn.execute("""
        SELECT m.id, m.status, u.fullname as student_name, p.branch, p.year
        FROM mentorship_requests m
        JOIN users u ON m.student_id = u.id
        JOIN profiles p ON u.id = p.user_id
        WHERE m.alumni_id = ?
    """, (session['user_id'],)).fetchall()
    
    # Opportunities posted by this alumni
    opportunities = conn.execute("SELECT * FROM opportunities WHERE posted_by_id = ?", (session['user_id'],)).fetchall()
    
    conn.close()
    return render_template('alumni_dashboard.html', mentorship_requests=requests, opportunities=opportunities)

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))
        
    conn = get_db()
    stats = {
        'students': conn.execute("SELECT count(*) FROM users WHERE role = 'student'").fetchone()[0],
        'alumni': conn.execute("SELECT count(*) FROM users WHERE role = 'alumni'").fetchone()[0],
        'events': conn.execute("SELECT count(*) FROM events").fetchone()[0],
        'opportunities': conn.execute("SELECT count(*) FROM opportunities").fetchone()[0]
    }
    conn.close()
    return render_template('admin_dashboard.html', stats=stats)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    if request.method == 'POST':
        # common
        department = request.form.get('department', '')
        branch = request.form.get('branch', '')
        year = request.form.get('year', '')
        skills = request.form.get('skills', '')
        
        # specific
        company = request.form.get('company', '')
        designation = request.form.get('designation', '')
        achievements = request.form.get('achievements', '')
        mentor_willing = 1 if request.form.get('mentor_willing') else 0
        interests = request.form.get('interests', '')
        resume = request.form.get('resume', '')
        
        conn.execute("""
            UPDATE profiles SET 
                department=?, branch=?, year=?, skills=?, 
                company=?, designation=?, achievements=?, mentor_willing=?,
                interests=?, resume=?
            WHERE user_id=?
        """, (department, branch, year, skills, company, designation, achievements, mentor_willing, interests, resume, session['user_id']))
        conn.commit()
        flash('Profile updated successfully!', 'success')
    
    profile = conn.execute("SELECT * FROM profiles WHERE user_id = ?", (session['user_id'],)).fetchone()
    conn.close()
    return render_template('profile.html', profile=profile)

@app.route('/mentorship')
def mentorship():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    if session['role'] == 'student':
        requests = conn.execute("""
            SELECT m.id, m.status, u.fullname as alumni_name, p.company, p.designation
            FROM mentorship_requests m
            JOIN users u ON m.alumni_id = u.id
            JOIN profiles p ON u.id = p.user_id
            WHERE m.student_id = ?
        """, (session['user_id'],)).fetchall()
        conn.close()
        return render_template('mentorship.html', requests=requests)
    else:
        conn.close()
        return redirect(url_for('alumni_dashboard'))

@app.route('/request_mentorship/<int:alumni_id>', methods=['POST'])
def request_mentorship(alumni_id):
    if 'user_id' not in session or session['role'] != 'student': return redirect(url_for('login'))
    conn = get_db()
    
    # Check if already requested
    existing = conn.execute("SELECT * FROM mentorship_requests WHERE student_id = ? AND alumni_id = ?", 
                            (session['user_id'], alumni_id)).fetchone()
    if existing:
        flash('Mentorship request already sent.', 'error')
    else:
        conn.execute("INSERT INTO mentorship_requests (student_id, alumni_id) VALUES (?, ?)", 
                     (session['user_id'], alumni_id))
        conn.commit()
        flash('Mentorship request sent successfully.', 'success')
        
    conn.close()
    return redirect(request.referrer or url_for('student_dashboard'))

@app.route('/handle_mentorship/<int:req_id>/<status>', methods=['POST'])
def handle_mentorship(req_id, status):
    if 'user_id' not in session or session['role'] != 'alumni': return redirect(url_for('login'))
    if status not in ['accepted', 'rejected']: return redirect(url_for('alumni_dashboard'))
    
    conn = get_db()
    conn.execute("UPDATE mentorship_requests SET status = ? WHERE id = ? AND alumni_id = ?", 
                 (status, req_id, session['user_id']))
    conn.commit()
    conn.close()
    flash(f'Request {status}.', 'success')
    return redirect(url_for('alumni_dashboard'))

@app.route('/opportunities')
def opportunities():
    conn = get_db()
    opps = conn.execute("""
        SELECT o.*, u.fullname as poster_name 
        FROM opportunities o
        JOIN users u ON o.posted_by_id = u.id
        ORDER BY o.deadline ASC
    """).fetchall()
    conn.close()
    return render_template('opportunities.html', opportunities=opps)

@app.route('/create_opportunity', methods=['GET', 'POST'])
def create_opportunity():
    if 'user_id' not in session or session['role'] not in ['alumni', 'admin']: 
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        company = request.form['company']
        description = request.form['description']
        skills = request.form['skills']
        deadline = request.form['deadline']
        
        conn = get_db()
        conn.execute("""
            INSERT INTO opportunities (title, company, description, skills, deadline, posted_by_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, company, description, skills, deadline, session['user_id']))
        conn.commit()
        conn.close()
        flash('Opportunity created successfully.', 'success')
        return redirect(url_for('opportunities'))
        
    return render_template('create_opportunity.html')

@app.route('/delete_opportunity/<int:id>', methods=['POST'])
def delete_opportunity(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    # Ensure they own it or are admin
    if session['role'] == 'admin':
        conn.execute("DELETE FROM opportunities WHERE id = ?", (id,))
    else:
        conn.execute("DELETE FROM opportunities WHERE id = ? AND posted_by_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Opportunity removed.', 'success')
    return redirect(url_for('opportunities'))

@app.route('/events')
def events():
    conn = get_db()
    evs = conn.execute("SELECT * FROM events ORDER BY date ASC").fetchall()
    conn.close()
    return render_template('events.html', events=evs)

@app.route('/create_event', methods=['GET', 'POST'])
def create_event():
    if 'user_id' not in session or session['role'] not in ['alumni', 'admin']: 
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        time = request.form['time']
        venue = request.form['venue']
        description = request.form['description']
        
        conn = get_db()
        conn.execute("""
            INSERT INTO events (title, date, time, venue, description, posted_by_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, date, time, venue, description, session['user_id']))
        conn.commit()
        conn.close()
        flash('Event created successfully.', 'success')
        return redirect(url_for('events'))
        
    return render_template('create_event.html')

@app.route('/delete_event/<int:id>', methods=['POST'])
def delete_event(id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db()
    if session['role'] == 'admin':
        conn.execute("DELETE FROM events WHERE id = ?", (id,))
    else:
        conn.execute("DELETE FROM events WHERE id = ? AND posted_by_id = ?", (id, session['user_id']))
    conn.commit()
    conn.close()
    flash('Event removed.', 'success')
    return redirect(url_for('events'))

@app.route('/search')
def search():
    q = request.args.get('q', '').lower()
    branch = request.args.get('branch', '').lower()
    
    conn = get_db()
    query = """
        SELECT u.id, u.fullname, p.department, p.branch, p.year, p.company, p.designation, p.skills, p.mentor_willing
        FROM users u
        JOIN profiles p ON u.id = p.user_id
        WHERE u.role = 'alumni'
    """
    params = []
    
    if q:
        query += " AND (LOWER(u.fullname) LIKE ? OR LOWER(p.company) LIKE ? OR LOWER(p.skills) LIKE ?)"
        params.extend([f'%{q}%', f'%{q}%', f'%{q}%'])
    if branch:
        query += " AND LOWER(p.branch) LIKE ?"
        params.append(f'%{branch}%')
        
    results = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('search.html', results=results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
