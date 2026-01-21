 Work Log Management System

A Flask-based web application for managing employee work logs with admin approval workflow and progress tracking.

---

Features

Employee
- Add daily work logs
- Edit and delete logs
- View approval status
- Track personal progress with chart

Admin
- View all employee logs
- Approve pending logs
- Filter logs by status
- View employee progress chart
- Create new admins

Dashboard
- Clean UI with Bootstrap
- Interactive charts using Chart.js
- Professional admin panel layout

---

Tech Stack

- Backend: Python, Flask  
- Frontend: HTML, Bootstrap 5, Chart.js  
- Database: SQLite  
- Authentication: email  

---

Project Structure
```
work_log_system/
│
├── app.py
├── database.db
├── templates/
│ ├── layout.html
│ ├── login.html
│ ├── admin_dashboard.html
│ ├── employee_dashboard.html
│ └── ...
├── static/
│ ├── css/
│ └── js/
└── README.md
```
---

Installation

Clone the Repository
```bash
git clone https://github.com/yourusername/work-log-system.git
cd work-log-system
Create Virtual Environment
bash
Copy code
python -m venv venv
venv\Scripts\activate   ### Windows
#Install Dependencies
bash
Copy code
pip install flask flask-login flask-sqlalchemy
#Run the App
bash
Copy code
python app.py
Open in browser:

cpp
Copy code
http://127.0.0.1:5000
#Default Roles
Admin: Can approve logs and manage employees

Employee: Can submit daily work logs

#Charts
Admin dashboard shows employee progress

Employee dashboard shows personal approved vs pending logs

# Status Workflow
New log → Pending

Admin approval → Approved

Future Enhancements
Export reports (PDF/Excel)

Email notifications

Role-based permissions

Date range filters

#Developer
by Md Sadhik