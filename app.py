import os  
import streamlit as st  
import pandas as pd  
import matplotlib.pyplot as plt  
import datetime  
import base64   
import sqlite3    
  
# -------------------------------    
# 1. Page Config & Data Directory    
# -------------------------------    
st.set_page_config(    
    page_title="Employee Records Tool",    
    page_icon="👥",    
    layout="wide",    
    initial_sidebar_state="expanded"    
)    
    
DATA_DIR = 'data'    
if not os.path.exists(DATA_DIR):    
    os.makedirs(DATA_DIR)    
  
# -------------------------------  
# SQLite Database Initialization  
# -------------------------------  
def init_sqlite_db():  
    """Initialize SQLite database with required tables"""  
    conn = sqlite3.connect('employee_database.db')  
    cursor = conn.cursor()  
      
    # Create the employees table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS employees (  
        employee_id TEXT PRIMARY KEY,  
        first_name TEXT,  
        last_name TEXT,  
        department TEXT,  
        job_title TEXT,  
        email TEXT,  
        phone TEXT,  
        employment_status TEXT  
    )  
    """)  
      
    # Create the meetings table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS meetings (  
        meeting_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        meeting_date TEXT,  
        meeting_time TEXT,  
        MeetingAgenda TEXT,  
        action_items TEXT,  
        notes TEXT,  
        next_meeting_date TEXT  
    )  
    """)  
      
    # Create the disciplinary table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS disciplinary (  
        disciplinary_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        type TEXT,  
        date TEXT,  
        description TEXT  
    )  
    """)  
      
    # Create the performance table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS performance (  
        review_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        review_date TEXT,  
        reviewer TEXT,  
        score TEXT,  
        comments TEXT  
    )  
    """)  
      
    # Create the training table  
    cursor.execute("""  
    CREATE TABLE IF NOT EXISTS training (  
        training_id TEXT PRIMARY KEY,  
        employee_id TEXT,  
        course_name TEXT,  
        start_date TEXT,  
        end_date TEXT,  
        status TEXT,  
        certification TEXT  
    )  
    """)  
      
    conn.commit()  
    conn.close()  
  
# Initialize SQLite database immediately  
init_sqlite_db()  
  
# -------------------------------  
# 2. CSV Download Helper Function  
# -------------------------------  
def get_csv_download_link(df, filename, label='Download CSV file'):  
    csv = df.to_csv(index=False)  
    b64 = base64.b64encode(csv.encode()).decode()  
    return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{label}</a>'  

# -------------------------------  
# 3. Data Persistence Functions  
# -------------------------------  
def load_table(table_name, columns):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    if os.path.exists(path):  
        return pd.read_csv(path)  
    else:  
        return pd.DataFrame({col: [] for col in columns})  
  
def save_table(table_name, df):  
    path = os.path.join(DATA_DIR, f'{table_name}.csv')  
    df.to_csv(path, index=False)  
    st.success(f"{table_name.capitalize()} data saved successfully!")  
  
def get_employee_display_name(employee_id):  
    if employee_id is None or pd.isna(employee_id):  
        return "N/A"  
    employee = st.session_state.employees[st.session_state.employees['employee_id'] == employee_id]  
    if not employee.empty:  
        return f"{employee['first_name'].values[0]} {employee['last_name'].values[0]}"  
    return "Unknown"  
  
def load_from_uploaded_file(uploaded_file, columns):  
    try:  
        df = pd.read_csv(uploaded_file)  
        # Ensure all required columns exist  
        for col in columns:  
            if col not in df.columns:  
                df[col] = ""  
        return df  
    except Exception as e:  
        st.error(f"Error loading file: {e}")  
        return pd.DataFrame({col: [] for col in columns})  

# -------------------------------  
# 4. SQLite Data Persistence Functions  
# -------------------------------  
def load_table_from_sqlite(table_name):  
    """Load a table from SQLite database"""  
    try:  
        conn = sqlite3.connect('employee_database.db')  
        df = pd.read_sql(f"SELECT * FROM {table_name}", conn)  
        conn.close()  
        return df  
    except Exception as e:  
        print(f"Error loading {table_name} from SQLite: " + str(e))  
        # Return empty DataFrame with appropriate columns  
        if table_name == "employees":  
            return pd.DataFrame(columns=employee_columns)  
        elif table_name == "meetings":  
            return pd.DataFrame(columns=meeting_columns)  
        elif table_name == "disciplinary":  
            return pd.DataFrame(columns=disciplinary_columns)  
        elif table_name == "performance":  
            return pd.DataFrame(columns=performance_columns)  
        elif table_name == "training":  
            return pd.DataFrame(columns=training_columns)  
        else:  
            return pd.DataFrame()  
  
def save_table_to_sqlite(table_name, df):  
    """Save a table to SQLite database"""  
    if df is None or df.empty:  
        print(f"Not saving {table_name} - data is empty")  
        return  
    conn = sqlite3.connect('employee_database.db')  
    df.to_sql(table_name, conn, if_exists='replace', index=False)  
    conn.close()  
    print(f"{table_name.capitalize()} data saved successfully!")  
  
def load_all_data_sqlite():  
    """Load all data from SQLite database"""  
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]  
    for table_name in tables:  
        st.session_state[table_name] = load_table_from_sqlite(table_name)  
        print(f"Loaded {table_name} data: {len(st.session_state[table_name])} records")  
  
def save_all_data_sqlite():  
    """Save all data to SQLite database"""  
    tables = ["employees", "meetings", "disciplinary", "performance", "training"]  
    for table_name in tables:  
        if table_name in st.session_state and not st.session_state[table_name].empty:  
            save_table_to_sqlite(table_name, st.session_state[table_name])  
    st.success("All data saved successfully!")  
  
# -------------------------------  
# 5. Session State Initialization & File Uploaders  
# -------------------------------  
# (Assuming you have definitions like these somewhere in your original code)  
employee_columns = ['employee_id', 'first_name', 'last_name', 'department', 'job_title', 'email', 'phone', 'employment_status']  
meeting_columns = ['meeting_id', 'employee_id', 'meeting_date', 'meeting_time', 'MeetingAgenda', 'action_items', 'notes', 'next_meeting_date']  
disciplinary_columns = ['disciplinary_id', 'employee_id', 'type', 'date', 'description']  
performance_columns = ['review_id', 'employee_id', 'review_date', 'reviewer', 'score', 'comments']  
training_columns = ['training_id', 'employee_id', 'course_name', 'start_date', 'end_date', 'status', 'certification']  
  
# -------------------------------  
# Initialize session state data from SQLite if not already loaded  
# -------------------------------  
if "data_loaded" not in st.session_state:  
    st.session_state.data_loaded = False  
  
if not st.session_state.data_loaded:  
    load_all_data_sqlite()  
    st.session_state.data_loaded = True  
  
# -------------------------------  
# 6. Other Application Logic / Functions (Your original code remains untouched)  
# -------------------------------  
# ... (All your additional functions, routes, page logic, etc.)  
  
# -------------------------------  
# 7. Sidebar: Save Button for SQLite Persistence  
# -------------------------------  
st.sidebar.title("Data Management")  
if st.sidebar.button("💾 Save All Data"):  
    save_all_data_sqlite()  
  
# -------------------------------  
# 7. Initialize Session State  
# -------------------------------  
employee_columns = ["employee_id", "first_name", "last_name", "department", "job_title", "email", "phone", "employment_status"]  
meeting_columns = ["meeting_id", "employee_id", "meeting_date", "meeting_time", "Meeting Agenda", "action_items", "notes", "next_meeting_date"]  
disciplinary_columns = ["disciplinary_id", "employee_id", "type", "date", "description"]  
performance_columns = ["review_id", "employee_id", "review_date", "reviewer", "score", "comments"]  
training_columns = ["training_id", "employee_id", "course_name", "start_date", "end_date", "status", "certification"]  
  
if 'employees' not in st.session_state:  
    st.session_state.employees = load_table("employees", employee_columns)  
if 'meetings' not in st.session_state:  
    st.session_state.meetings = load_table("meetings", meeting_columns)  
if 'disciplinary' not in st.session_state:  
    st.session_state.disciplinary = load_table("disciplinary", disciplinary_columns)  
if 'performance' not in st.session_state:  
    st.session_state.performance = load_table("performance", performance_columns)  
if 'training' not in st.session_state:  
    st.session_state.training = load_table("training", training_columns)  
  
# -------------------------------  
# 8. Sidebar Navigation  
# -------------------------------  
st.sidebar.title("Employee Records Tool")  
module = st.sidebar.selectbox(  
    "Select Module",  
    ["Employee Management", "One-on-One Meetings", "Disciplinary Actions", "Performance Reviews", "Training Records", "Reports"]  
)  
  
# -------------------------------  
# 6. Module: Employee Management  
# -------------------------------  
if module == "Employee Management":  
    st.header("Employee Management")  
      
    # CSV Upload option  
    uploaded_employees = st.file_uploader("Upload Employees CSV", type="csv", key="employee_upload")  
    if uploaded_employees is not None:  
        st.session_state.employees = load_from_uploaded_file(uploaded_employees, employee_columns)  
        st.success("Employee data uploaded successfully!")  
      
    with st.form("employee_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
            last_name = st.text_input("Last Name")  
            department = st.text_input("Department")  
        with col2:  
            job_title = st.text_input("Job Title")  
            email = st.text_input("Email")  
            phone = st.text_input("Phone")  
            employment_status = st.selectbox("Employment Status", ["Active", "Inactive", "On Leave", "Terminated"])  
          
        submitted_employee = st.form_submit_button("Add/Update Employee")  
        if submitted_employee:  
            if employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_employee = pd.DataFrame({  
                    "employee_id": [employee_id],  
                    "first_name": [first_name],  
                    "last_name": [last_name],  
                    "department": [department],  
                    "job_title": [job_title],  
                    "email": [email],  
                    "phone": [phone],  
                    "employment_status": [employment_status],  
                })  
                  
                # Check if employee already exists  
                if int(employee_id) in st.session_state.employees['employee_id'].values:  
                    st.session_state.employees = st.session_state.employees[st.session_state.employees['employee_id'] != int(employee_id)]  
                  
                st.session_state.employees = pd.concat([st.session_state.employees, new_employee], ignore_index=True)  
                st.success("Employee added/updated successfully!")  
      
    st.subheader("Employees Table")  
    st.dataframe(st.session_state.employees)  
    st.markdown(get_csv_download_link(st.session_state.employees, "employees.csv", "Download Employees CSV"), unsafe_allow_html=True)  
    if st.button("Save Employee Data"):  
        save_table("employees", st.session_state.employees)  
  
# -------------------------------  
# 9. Module: One-on-One Meetings  
# -------------------------------  
elif module == "One-on-One Meetings":  
    st.header("One-on-One Meetings")  
      
    # CSV Upload option  
    uploaded_meetings = st.file_uploader("Upload Meetings CSV", type="csv", key="meetings_upload")  
    if uploaded_meetings is not None:  
        st.session_state.meetings = load_from_uploaded_file(uploaded_meetings, meeting_columns)  
        st.success("Meetings data uploaded successfully!")  
      
    with st.form("meeting_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            meeting_id = st.text_input("Meeting ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            meeting_date = st.date_input("Meeting Date", datetime.date.today())  
            meeting_time = st.time_input("Meeting Time", datetime.time(9, 0))  
        with col2:  
            meeting_agenda = st.text_area("Meeting Agenda")  
            action_items = st.text_area("Action Items")  
            notes = st.text_area("Notes")  
            next_meeting_date = st.date_input("Next Meeting Date", datetime.date.today())  
        submitted_meeting = st.form_submit_button("Record Meeting")  
        if submitted_meeting:  
            if meeting_id == "" or not meeting_id.isdigit():  
                st.error("Please enter a valid numeric Meeting ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_meeting = pd.DataFrame({  
                    "meeting_id": [meeting_id],  
                    "employee_id": [employee_id],  
                    "meeting_date": [meeting_date.strftime('%Y-%m-%d')],  
                    "meeting_time": [meeting_time.strftime('%H:%M:%S')],  
                    "Meeting Agenda": [meeting_agenda],  
                    "action_items": [action_items],  
                    "notes": [notes],  
                    "next_meeting_date": [next_meeting_date.strftime('%Y-%m-%d')]  
                })  
                st.session_state.meetings = pd.concat([st.session_state.meetings, new_meeting], ignore_index=True)  
                st.success("Meeting recorded successfully!")  
      
    st.subheader("Meetings Table")  
    st.dataframe(st.session_state.meetings)  
    st.markdown(get_csv_download_link(st.session_state.meetings, "meetings.csv", "Download Meetings CSV"), unsafe_allow_html=True)  
    if st.button("Save Meetings Data"):  
        save_table("meetings", st.session_state.meetings)  
  
# -------------------------------  
# 10. Module: Disciplinary Actions  
# -------------------------------  
elif module == "Disciplinary Actions":  
    st.header("Disciplinary Actions")  
    # Updated column structure for disciplinary actions:  
    # ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name", "Job Title",  
    #  "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
      
    # CSV Upload option  
    uploaded_disciplinary = st.file_uploader("Upload Disciplinary CSV", type="csv", key="disciplinary_upload")  
    if uploaded_disciplinary is not None:  
        # When uploading, ensure the file has at least the required columns (if missing, fill with empty string)  
        required_cols = ["Period (Date)", "disciplinary_id", "ID", "First Name", "Last Name",  
                         "Job Title", "Violation", "Interview Date", "Reason", "Comments", "Interviewer", "Decision"]  
        st.session_state.disciplinary = load_from_uploaded_file(uploaded_disciplinary, required_cols)  
        st.success("Disciplinary data uploaded successfully!")  
      
    # Updated Form for Disciplinary Actions  
    with st.form("disciplinary_form"):  
        st.subheader("Record Disciplinary Action")  
          
        col1, col2, col3 = st.columns(3)  
        with col1:  
            period_date = st.date_input("Period (Date)", datetime.date.today())  
            disciplinary_id = st.text_input("Disciplinary ID (max 6 digits)", max_chars=6)  
            emp_id = st.text_input("ID (Employee ID - max 6 digits)", max_chars=6)  
            first_name = st.text_input("First Name")  
        with col2:  
            last_name = st.text_input("Last Name")  
            job_title = st.text_input("Job Title")  
            violation = st.text_input("Violation")  
            interview_date = st.date_input("Interview Date", datetime.date.today())  
        with col3:  
            reason = st.text_area("Reason")  
            comments = st.text_area("Comments")  
            interviewer = st.text_input("Interviewer")  
            decision = st.text_input("Decision")  
          
        submitted_disc = st.form_submit_button("Record Disciplinary Action")  
        if submitted_disc:  
            # Validate numeric inputs for IDs  
            if disciplinary_id == "" or not disciplinary_id.isdigit():  
                st.error("Please enter a valid numeric Disciplinary ID (up to 6 digits).")  
            elif emp_id == "" or not emp_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_disc = pd.DataFrame({  
                    "Period (Date)": [period_date.strftime('%Y-%m-%d')],  
                    "disciplinary_id": [disciplinary_id],  
                    "ID": [emp_id],  
                    "First Name": [first_name],  
                    "Last Name": [last_name],  
                    "Job Title": [job_title],  
                    "Violation": [violation],  
                    "Interview Date": [interview_date.strftime('%Y-%m-%d')],  
                    "Reason": [reason],  
                    "Comments": [comments],  
                    "Interviewer": [interviewer],  
                    "Decision": [decision]  
                })  
                st.session_state.disciplinary = pd.concat([st.session_state.disciplinary, new_disc], ignore_index=True)  
                st.success("Disciplinary action recorded successfully!")  
      
    st.subheader("Disciplinary Actions Table")  
    st.dataframe(st.session_state.disciplinary)  
    st.markdown(get_csv_download_link(st.session_state.disciplinary, "disciplinary.csv", "Download Disciplinary CSV"), unsafe_allow_html=True)  
    if st.button("Save Disciplinary Data"):  
        save_table("disciplinary", st.session_state.disciplinary)  
# -------------------------------  
# 11. Module: Performance Reviews  
# -------------------------------  
elif module == "Performance Reviews":  
    st.header("Performance Reviews")  
      
    # CSV Upload option  
    uploaded_performance = st.file_uploader("Upload Performance CSV", type="csv", key="performance_upload")  
    if uploaded_performance is not None:  
        st.session_state.performance = load_from_uploaded_file(uploaded_performance, performance_columns)  
        st.success("Performance data uploaded successfully!")  
      
    with st.form("performance_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            review_id = st.text_input("Review ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            review_date = st.date_input("Review Date", datetime.date.today())  
        with col2:  
            reviewer = st.text_input("Reviewer")  
            score = st.slider("Score", 1, 5, 3)  
            comments = st.text_area("Comments")  
        submitted_review = st.form_submit_button("Record Performance Review")  
        if submitted_review:  
            if review_id == "" or not review_id.isdigit():  
                st.error("Please enter a valid numeric Review ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_review = pd.DataFrame({  
                    "review_id": [review_id],  
                    "employee_id": [employee_id],  
                    "review_date": [review_date.strftime('%Y-%m-%d')],  
                    "reviewer": [reviewer],  
                    "score": [score],  
                    "comments": [comments]  
                })  
                st.session_state.performance = pd.concat([st.session_state.performance, new_review], ignore_index=True)  
                st.success("Performance review recorded successfully!")  
      
    st.subheader("Performance Reviews Table")  
    st.dataframe(st.session_state.performance)  
    st.markdown(get_csv_download_link(st.session_state.performance, "performance.csv", "Download Performance CSV"), unsafe_allow_html=True)  
    if st.button("Save Performance Data"):  
        save_table("performance", st.session_state.performance)  
  
# -------------------------------  
# 12. Module: Training Records  
# -------------------------------  
elif module == "Training Records":  
    st.header("Training Records")  
      
    # CSV Upload option  
    uploaded_training = st.file_uploader("Upload Training CSV", type="csv", key="training_upload")  
    if uploaded_training is not None:  
        st.session_state.training = load_from_uploaded_file(uploaded_training, training_columns)  
        st.success("Training data uploaded successfully!")  
      
    with st.form("training_form"):  
        col1, col2 = st.columns(2)  
        with col1:  
            training_id = st.text_input("Training ID (max 6 digits)", max_chars=6)  
            employee_id = st.text_input("Employee ID (max 6 digits)", max_chars=6)  
            course_name = st.text_input("Course Name")  
        with col2:  
            start_date = st.date_input("Start Date", datetime.date.today())  
            end_date = st.date_input("End Date", datetime.date.today() + datetime.timedelta(days=30))  
            status = st.selectbox("Status", ["Not Started", "In Progress", "Completed", "Failed"])  
            certification = st.text_input("Certification")  
        submitted_training = st.form_submit_button("Record Training")  
        if submitted_training:  
            if training_id == "" or not training_id.isdigit():  
                st.error("Please enter a valid numeric Training ID (up to 6 digits).")  
            elif employee_id == "" or not employee_id.isdigit():  
                st.error("Please enter a valid numeric Employee ID (up to 6 digits).")  
            else:  
                new_training = pd.DataFrame({  
                    "training_id": [training_id],  
                    "employee_id": [employee_id],  
                    "course_name": [course_name],  
                    "start_date": [start_date.strftime('%Y-%m-%d')],  
                    "end_date": [end_date.strftime('%Y-%m-%d')],  
                    "status": [status],  
                    "certification": [certification]  
                })  
                st.session_state.training = pd.concat([st.session_state.training, new_training], ignore_index=True)  
                st.success("Training record added successfully!")  
      
    st.subheader("Training Records Table")  
    st.dataframe(st.session_state.training)  
    st.markdown(get_csv_download_link(st.session_state.training, "training.csv", "Download Training CSV"), unsafe_allow_html=True)  
    if st.button("Save Training Data"):  
        save_table("training", st.session_state.training)  
  
# -------------------------------  
# 13. Module: Reports  
# -------------------------------  
# -------------------------------  
# Reports Module  
# -------------------------------  
elif module == "Reports":  
    st.title("Reports")  
  
    # Date range selection  
    st.subheader("Select Date Range")  
    col1, col2 = st.columns(2)  
    with col1:  
        date_from = st.date_input("From", datetime.date.today() - datetime.timedelta(days=30))  
    with col2:  
        date_to = st.date_input("To", datetime.date.today())  
  
    # Report type selection with new options  
    report_type = st.selectbox(  
        "Select Report Type",  
        ["Employee Activity", "Department Performance", "Training Completion", "Meeting Frequency",  
         "Employees by Employment Status", "Disciplinary Actions by Violations",   
         "Disciplinary Actions per Employee", "Training per Employee",   
         "Training Completion Status", "Performance per Employee"]  
    )  
  
    # Grouping options (for applicable types)  
    grouping_options = st.multiselect(  
        "Group By",  
        ["Employee", "Department", "Job Title"],  
        default=["Employee"]  
    )  
  
    report_df = None  # This will hold the generated report  
  
    if st.button("Generate Report"):  
        if "employees" not in st.session_state or st.session_state.employees.empty:  
            st.error("No employee data available.")  
            st.stop()  
  
        # Filter data by date range  
        date_from_dt = pd.to_datetime(date_from)  
        date_to_dt = pd.to_datetime(date_to)  
  
        # Original report types  
        if report_type == "Employee Activity":  
            if "activity" in st.session_state and not st.session_state.activity.empty:  
                activity_df = st.session_state.activity.copy()  
                activity_df['date'] = pd.to_datetime(activity_df['date'], errors='coerce')  
                activity_df = activity_df[(activity_df['date'] >= date_from_dt) & (activity_df['date'] <= date_to_dt)]  
      
                if not activity_df.empty:  
                    activity_with_emp = activity_df.merge(  
                        st.session_state.employees[['employee_id', 'first_name', 'last_name', 'department', 'job_title']],  
                        on='employee_id', how='left'  
                    )  
                    activity_with_emp['employee'] = activity_with_emp['first_name'] + " " + activity_with_emp['last_name']  
                    report_df = activity_with_emp  
                    st.dataframe(report_df)  
                      
                    # Simple bar chart: count of activities per employee  
                    counts = report_df['employee'].value_counts().reset_index()  
                    counts.columns = ['employee', 'Count']  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(counts['employee'], counts['Count'], color='#2563EB')  
                    ax.set_xlabel("Employee", labelpad=10)  
                    ax.set_ylabel("Activity Count", labelpad=10)  
                    ax.set_title("Employee Activity Report", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("No employee activity data available for the selected date range.")  
            else:  
                st.info("No employee activity data available.")  
      
        elif report_type == "Department Performance":  
            if "performance" in st.session_state and not st.session_state.performance.empty:  
                perf_df = st.session_state.performance.copy()  
                perf_df['date'] = pd.to_datetime(perf_df['date'], errors='coerce')  
                perf_df = perf_df[(perf_df['date'] >= date_from_dt) & (perf_df['date'] <= date_to_dt)]  
                  
                if not perf_df.empty:  
                    perf_with_emp = perf_df.merge(  
                        st.session_state.employees[['employee_id', 'first_name', 'last_name', 'department']],  
                        on='employee_id', how='left'  
                    )  
                      
                    # Assuming there's a numeric performance metric column  
                    numeric_cols = perf_with_emp.select_dtypes(include=['number']).columns.tolist()  
                    if 'employee_id' in numeric_cols:  
                        numeric_cols.remove('employee_id')  
                      
                    if numeric_cols:  
                        dept_perf = perf_with_emp.groupby('department')[numeric_cols].mean().reset_index()  
                        report_df = dept_perf  
                        st.dataframe(report_df)  
                          
                        # Plot  
                        fig, ax = plt.subplots(figsize=(12, 8))  
                        ax.bar(dept_perf['department'], dept_perf[numeric_cols[0]], color='#2563EB')  
                        ax.set_xlabel("Department", labelpad=10)  
                        ax.set_ylabel(numeric_cols[0], labelpad=10)  
                        ax.set_title("Department Performance", pad=15)  
                        ax.set_axisbelow(True)  
                        plt.xticks(rotation=45, ha='right')  
                        plt.tight_layout()  
                        st.pyplot(fig)  
                    else:  
                        st.info("No numeric performance metrics found in the data.")  
                else:  
                    st.info("No performance data found for the selected date range.")  
            else:  
                st.info("No performance data available.")  
      
        elif report_type == "Training Completion":  
            if "training" in st.session_state and not st.session_state.training.empty:  
                training_df = st.session_state.training.copy()  
                training_df['date'] = pd.to_datetime(training_df['date'], errors='coerce')  
                training_df = training_df[(training_df['date'] >= date_from_dt) & (training_df['date'] <= date_to_dt)]  
                  
                if not training_df.empty:  
                    # Assuming there's a completion status column  
                    if 'completion_status' in training_df.columns:  
                        completion_counts = training_df['completion_status'].value_counts().reset_index()  
                        completion_counts.columns = ['Status', 'Count']  
                        report_df = completion_counts  
                        st.dataframe(report_df)  
                          
                        # Plot  
                        fig, ax = plt.subplots(figsize=(12, 8))  
                        ax.bar(completion_counts['Status'], completion_counts['Count'], color='#2563EB')  
                        ax.set_xlabel("Completion Status", labelpad=10)  
                        ax.set_ylabel("Count", labelpad=10)  
                        ax.set_title("Training Completion Status", pad=15)  
                        ax.set_axisbelow(True)  
                        plt.xticks(rotation=45, ha='right')  
                        plt.tight_layout()  
                        st.pyplot(fig)  
                    else:  
                        st.info("Completion status column not found in training data.")  
                else:  
                    st.info("No training data found for the selected date range.")  
            else:  
                st.info("No training data available.")  
      
        elif report_type == "Meeting Frequency":  
            if "meetings" in st.session_state and not st.session_state.meetings.empty:  
                meetings_df = st.session_state.meetings.copy()  
                meetings_df['meeting_date'] = pd.to_datetime(meetings_df['meeting_date'], errors='coerce')  
                meetings_df = meetings_df[(meetings_df['meeting_date'] >= date_from_dt) & (meetings_df['meeting_date'] <= date_to_dt)]  
                  
                if not meetings_df.empty:  
                    # Add month column for grouping  
                    meetings_df['month'] = meetings_df['meeting_date'].dt.strftime('%Y-%m')  
                      
                    meeting_freq = meetings_df.groupby('month').size().reset_index(name='Count')  
                    report_df = meeting_freq  
                    st.dataframe(report_df)  
                      
                    # Plot  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(meeting_freq['month'], meeting_freq['Count'], color='#2563EB')  
                    ax.set_xlabel("Month", labelpad=10)  
                    ax.set_ylabel("Number of Meetings", labelpad=10)  
                    ax.set_title("Meeting Frequency by Month", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("No meetings found for the selected date range.")  
            else:  
                st.info("No meeting data available.")  
                  
        # New report types  
        elif report_type == "Employees by Employment Status":  
            if "employees" in st.session_state and not st.session_state.employees.empty:  
                emp_df = st.session_state.employees.copy()  
                # We assume employment status is stored in a column named 'employment_status'  
                if "employment_status" in emp_df.columns:  
                    status_counts = emp_df['employment_status'].value_counts().reset_index()  
                    status_counts.columns = ['Employment Status', 'Count']  
                    report_df = status_counts  
                    st.dataframe(report_df)  
                      
                    # Plot  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(report_df['Employment Status'], report_df['Count'], color='#2563EB')  
                    ax.set_xlabel("Employment Status", labelpad=10)  
                    ax.set_ylabel("Number of Employees", labelpad=10)  
                    ax.set_title("Employees by Employment Status", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("Employment status column not found in employee data.")  
            else:  
                st.info("No employee data available.")  
                  
        elif report_type == "Disciplinary Actions by Violations":  
            if "disciplinary" in st.session_state and not st.session_state.disciplinary.empty:  
                disc_df = st.session_state.disciplinary.copy()  
                disc_df['date'] = pd.to_datetime(disc_df['date'], errors='coerce')  
                disc_df = disc_df[(disc_df['date'] >= date_from_dt) & (disc_df['date'] <= date_to_dt)]  
                  
                if not disc_df.empty:  
                    # Count violations by type  
                    violation_counts = disc_df['violation_type'].value_counts().reset_index()  
                    violation_counts.columns = ['Violation Type', 'Count']  
                    report_df = violation_counts  
                    st.dataframe(report_df)  
                      
                    # Plot  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(report_df['Violation Type'], report_df['Count'], color='#2563EB')  
                    ax.set_xlabel("Violation Type", labelpad=10)  
                    ax.set_ylabel("Number of Incidents", labelpad=10)  
                    ax.set_title("Disciplinary Actions by Violation Type", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("No disciplinary actions found for the selected date range.")  
            else:  
                st.info("No disciplinary data available.")  
                  
        elif report_type == "Disciplinary Actions per Employee":  
            if "disciplinary" in st.session_state and not st.session_state.disciplinary.empty:  
                disc_df = st.session_state.disciplinary.copy()  
                disc_df['date'] = pd.to_datetime(disc_df['date'], errors='coerce')  
                disc_df = disc_df[(disc_df['date'] >= date_from_dt) & (disc_df['date'] <= date_to_dt)]  
                  
                if not disc_df.empty:  
                    # Merge with employee data  
                    disc_with_emp = disc_df.merge(  
                        st.session_state.employees[['employee_id', 'first_name', 'last_name']],  
                        on='employee_id', how='left'  
                    )  
                    disc_with_emp['employee'] = disc_with_emp['first_name'] + " " + disc_with_emp['last_name']  
                      
                    # Count actions per employee  
                    emp_counts = disc_with_emp['employee'].value_counts().reset_index()  
                    emp_counts.columns = ['Employee', 'Count']  
                    report_df = emp_counts  
                    st.dataframe(report_df)  
                      
                    # Plot  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(report_df['Employee'], report_df['Count'], color='#2563EB')  
                    ax.set_xlabel("Employee", labelpad=10)  
                    ax.set_ylabel("Number of Disciplinary Actions", labelpad=10)  
                    ax.set_title("Disciplinary Actions per Employee", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("No disciplinary actions found for the selected date range.")  
            else:  
                st.info("No disciplinary data available.")  
                  
        elif report_type == "Training per Employee":  
            if "training" in st.session_state and not st.session_state.training.empty:  
                train_df = st.session_state.training.copy()  
                train_df['date'] = pd.to_datetime(train_df['date'], errors='coerce')  
                train_df = train_df[(train_df['date'] >= date_from_dt) & (train_df['date'] <= date_to_dt)]  
                  
                if not train_df.empty:  
                    # Merge with employee data  
                    train_with_emp = train_df.merge(  
                        st.session_state.employees[['employee_id', 'first_name', 'last_name']],  
                        on='employee_id', how='left'  
                    )  
                    train_with_emp['employee'] = train_with_emp['first_name'] + " " + train_with_emp['last_name']  
                      
                    # Count trainings per employee  
                    emp_counts = train_with_emp['employee'].value_counts().reset_index()  
                    emp_counts.columns = ['Employee', 'Count']  
                    report_df = emp_counts  
                    st.dataframe(report_df)  
                      
                    # Plot  
                    fig, ax = plt.subplots(figsize=(12, 8))  
                    ax.bar(report_df['Employee'], report_df['Count'], color='#2563EB')  
                    ax.set_xlabel("Employee", labelpad=10)  
                    ax.set_ylabel("Number of Trainings", labelpad=10)  
                    ax.set_title("Training per Employee", pad=15)  
                    ax.set_axisbelow(True)  
                    plt.xticks(rotation=45, ha='right')  
                    plt.tight_layout()  
                    st.pyplot(fig)  
                else:  
                    st.info("No training data found for the selected date range.")  
            else:  
                st.info("No training data available.")  
                  
        elif report_type == "Training Completion Status":  
            if "training" in st.session_state and not st.session_state.training.empty:  
                train_df = st.session_state.training.copy()  
                train_df['date'] = pd.to_datetime(train_df['date'], errors='coerce')  
                train_df = train_df[(train_df['date'] >= date_from_dt) & (train_df['date'] <= date_to_dt)]  
                  
                if not train_df.empty:  
                    # Expecting a column 'completion_status' in training data indicating completion status  
                    if "completion_status" in train_df.columns:  
                        status_counts = train_df['completion_status'].value_counts().reset_index()  
                        status_counts.columns = ['Completion Status', 'Count']  
                        report_df = status_counts  
                        st.dataframe(report_df)  
                          
                        # Plot  
                        fig, ax = plt.subplots(figsize=(12, 8))  
                        ax.bar(report_df['Completion Status'], report_df['Count'], color='#2563EB')  
                        ax.set_xlabel("Completion Status", labelpad=10)  
                        ax.set_ylabel("Count", labelpad=10)  
                        ax.set_title("Training Completion Status", pad=15)  
                        ax.set_axisbelow(True)  
                        plt.xticks(rotation=45, ha='right')  
                        plt.tight_layout()  
                        st.pyplot(fig)  
                    else:  
                        st.info("Completion status column not found in training data.")  
                else:  
                    st.info("No training data found for the selected date range.")  
            else:  
                st.info("No training data available.")  
                  
        elif report_type == "Performance per Employee":  
            if "performance" in st.session_state and not st.session_state.performance.empty:  
                perf_df = st.session_state.performance.copy()  
                perf_df['date'] = pd.to_datetime(perf_df['date'], errors='coerce')  
                perf_df = perf_df[(perf_df['date'] >= date_from_dt) & (perf_df['date'] <= date_to_dt)]  
                  
                if not perf_df.empty:  
                    # Merge with employee data  
                    perf_with_emp = perf_df.merge(  
                        st.session_state.employees[['employee_id', 'first_name', 'last_name']],  
                        on='employee_id', how='left'  
                    )  
                    perf_with_emp['employee'] = perf_with_emp['first_name'] + " " + perf_with_emp['last_name']  
                      
                    # Find numeric performance metrics  
                    numeric_cols = perf_with_emp.select_dtypes(include=['number']).columns.tolist()  
                    if 'employee_id' in numeric_cols:  
                        numeric_cols.remove('employee_id')  
                      
                    if numeric_cols:  
                        # Calculate average performance metrics per employee  
                        report_df = perf_with_emp.groupby('employee')[numeric_cols].mean().reset_index()  
                        st.dataframe(report_df)  
                          
                        # Plot  
                        fig, ax = plt.subplots(figsize=(12, 8))  
                        ax.bar(report_df['employee'], report_df[numeric_cols[0]], color='#2563EB')  
                        ax.set_xlabel("Employee", labelpad=10)  
                        ax.set_ylabel(numeric_cols[0], labelpad=10)  
                        ax.set_title("Performance per Employee", pad=15)  
                        ax.set_axisbelow(True)  
                        plt.xticks(rotation=45, ha='right')  
                        plt.tight_layout()  
                        st.pyplot(fig)  
                    else:  
                        st.info("No numeric performance metrics found in the data.")  
                else:  
                    st.info("No performance data found for the selected date range.")  
            else:  
                st.info("No performance data available.")  
  
    # Export options  
    st.subheader("Export Report")  
    if st.button("Export to CSV"):  
        if 'report_df' in locals() and report_df is not None:  
            csv = report_df.to_csv(index=False)  
            b64 = base64.b64encode(csv.encode()).decode()  
            href = f'<a href="data:file/csv;base64,{b64}" download="report.csv">Download CSV File</a>'  
            st.markdown(href, unsafe_allow_html=True)  
        else:  
            st.error("No report data to export.")  
