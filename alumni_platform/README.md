# Go Connect - Alumni Platform

An Intelligent Platform to Interconnect Alumni and Students for the Technical Education Department, Govt. of Rajasthan (Smart India Hackathon Prototype).

## Features
- **Role-based Access**: Separate dashboards for Students, Alumni, and Admin.
- **Smart Matchmaking**: Students are matched with alumni based on shared branches and skills.
- **Mentorship System**: Students can request mentorship; alumni can manage accept/reject these requests.
- **Opportunities Board**: Alumni and admins can post and manage jobs, internships, and projects.
- **Event Management**: Platform events like webinars and meetups can be posted.
- **Search System**: Find alumni, opportunities, and events seamlessly.
- **Profile Management**: Custom dynamic profiles depending on user roles.

## Project Structure
```
alumni_platform/
├── app.py                  # Main Flask application
├── init_db.py              # SQLite database creation and sample data seed
├── requirements.txt        # Python dependencies
├── README.md               # Setup and run instructions
├── static/
│   └── css/
│       └── style.css       # Custom modern CSS styles
└── templates/
    ├── base.html           # Base Jinja layout
    ├── index.html          # Homepage
    ├── login.html          # User login
    ├── register.html       # User registration
    ├── student_dashboard.html
    ├── alumni_dashboard.html
    ├── admin_dashboard.html
    ├── profile.html        # Dynamic profile editor
    ├── mentorship.html     # Mentorship requests (student view)
    ├── opportunities.html  # Opportunities listing
    ├── create_opportunity.html
    ├── events.html         # Events listing
    ├── create_event.html
    └── search.html         # Alumni Search
```

## Step-by-Step Instructions to Run Locally

### 1. Prerequisites
Make sure you have Python 3.8+ installed on your computer.

### 2. Setup Virtual Environment (Optional but Recommended)
Open a terminal in the project directory and run:
`python -m venv venv`

Activate the virtual environment:
- For Mac/Linux: `source venv/bin/activate`
- For Windows: `venv\Scripts\activate`

### 3. Install Dependencies
Run the following command to install Flask:
`pip install -r requirements.txt`

### 4. Initialize the Database
Before running the application for the first time, you need to create the database schema and insert the sample accounts.
Run the initialization script:
`python init_db.py`

This will create a `database.db` file in your root folder and prepopulate it with testing data.

### 5. Run the Application
Start the Flask development server:
`python app.py`

You should see output indicating that the development server is running locally.

### 6. Access the Application
Open your web browser and go to:
`http://127.0.0.1:5000`

### Demo Credentials for Judges
You can use the following pre-created accounts to explore the different perspectives of the platform:

| Role | Email | Password |
|---|---|---|
| **Admin** | admin@example.com | admin123 |
| **Student** | student@example.com | student123 |
| **Alumni** | alumni@example.com | alumni123 |

*(You can also use the registration page to create your own brand new accounts)*
