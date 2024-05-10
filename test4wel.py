import numpy as np
import pickle
import pandas as pd
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os
import csv

# Loading up the Classification model we created
model = pickle.load(open('job_posting.pkl', 'rb'))

# Create a SessionState class to store session-specific data
class SessionState:
    def __init__(self):
        self.logged_in = False
        self.image = None
        self.registered = False  # Initialize registered attribute

# Initialize SessionState object
session_state = SessionState()

# Function to handle login logic
def login(username, password):
    if username == "admin" and password == "secret":
        session_state.logged_in = True
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")

# Function to handle user registration logic
def register(username, email, password, retype_password):
    # Add registration validation logic
    if password != retype_password:
        st.error("Passwords do not match.")
        return
    
    # Store registration details in a CSV file
    with open('user_data.csv', 'a', newline='') as csvfile:
        fieldnames = ['Username', 'Email', 'Password']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        # Write header if file is empty
        if os.stat('user_data.csv').st_size == 0:
            writer.writeheader()

        # Write registration data to CSV
        writer.writerow({'Username': username, 'Email': email, 'Password': password})

    # Set registered status to True
    session_state.registered = True
    st.success("Registration successful!")

# Function to handle feedback form submission
def store_feedback(company_name, reference_link, is_real_posting):
    if company_name and reference_link and is_real_posting:
        feedback_data = {
            'Company Name': company_name,
            'Reference Link': reference_link,
            'Is Real Posting': is_real_posting
        }
        feedback_df = pd.DataFrame(feedback_data, index=[0])
        feedback_df.to_csv('job_posting_feedback.csv', mode='a', header=not os.path.exists('job_posting_feedback.csv'), index=False)
        st.success("Thanks for your feedback! We continue to improve our model.")
    else:
        st.error("Please fill in all the fields.")

# Creating Front end of application
st.markdown(
    """
    <style>
    .welcome-text {
        background-image: url('https://image.freepik.com/free-vector/jobs-background-design_1200-196.jpg');
        background-size: cover;
        padding: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.markdown('<div class="welcome-text"><h1>Welcome to Job Posting Classifier!</h1><p>To provide feedback, please log in. For testing the classifier, go to the Classifier option in the sidebar. Thank you!</p></div>', unsafe_allow_html=True)

app_mode = st.sidebar.radio('Select Page', ['Login', 'Classifier', 'Feedback', 'Register'])

# Login page
if app_mode == 'Login':
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login")

    if login_button:
        login(username, password)
        if session_state.logged_in:
            app_mode = 'Feedback'

# Registration form page
if app_mode == 'Register':
    st.title('User Registration')

    # Check if already registered
    if getattr(session_state, 'registered', False):
        st.info("Already registered. You can now login.")
        app_mode = 'Login'
    else:
        # Registration form inputs
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        retype_password = st.text_input("Retype Password", type="password")

        # Submit button
        if st.button("Register"):
            register(username, email, password, retype_password)
            if session_state.registered:
                app_mode = 'Classifier'  # Automatically move to Classifier page after successful registration

# Feedback form page
if app_mode == 'Feedback':
    st.title('Feedback Form')

    # Check if logged in
    if getattr(session_state, 'logged_in', False):
        st.write("Enter the details for job posting feedback:")
        company_name = st.text_input("Enter Company Name")
        reference_link = st.text_input("Enter Reference Link")
        is_real_posting = st.radio("Was this a real job posting?", ("Yes", "No", "Unsure"))

        feedback_submitted = st.button('Submit Feedback')
        if feedback_submitted:
            store_feedback(company_name, reference_link, is_real_posting)

# Classifier page
if app_mode == 'Classifier':
    st.title("Job Posting Classifier: Real/Fake")
    st.write("Enter a link to the job posting and answer the following questions to get the prediction.")

    user_input = st.text_input("Enter Job Posting Source Link or Upload Image")

    if user_input:
        if user_input.startswith(('http://', 'https://')):
            response = requests.get(user_input)
            if response.status_code == 200:
                # Check if response content is an image
                content_type = response.headers['content-type']
                if 'image' in content_type:
                    session_state.image = Image.open(BytesIO(response.content))
                    st.image(session_state.image, caption='Job Posting Image', use_column_width=True)
                else:
                # Display classifier questions directly
                 st.subheader('Enter the details:')

                # Questions and options for the classifier
                telecommuting = st.radio('Is work from home or remote work allowed?', options=['Yes', 'No'])
                has_company_logo = st.radio('Does the job posting have a company logo?', options=['Yes', 'No'])
                has_questions = st.radio('Does the job posting have questions?', options=['Yes', 'No'])
                employment_type = st.selectbox('What is the employment type?', ('Not Specified', 'Other', 'Part-time', 'Contract', 'Temporary', 'Full-time'))
                required_experience = st.selectbox('What is the required experience?', ('Not Applicable', 'Internship', 'Entry level', 'Mid-Senior level', 'Associate',  'Executive', 'Director'))
                required_education = st.selectbox('What is the required education?', ('Unspecified', 'Vocational - HS Diploma', 'Some High School Coursework', 'High School or equivalent', 'Some College Coursework Completed', 'Certification', 'Vocational', 'Vocational - Degree', "Bachelor's Degree", "Master's Degree", 'Associate Degree', 'Professional', 'Doctorate'))
                industry = st.selectbox('Please choose which industry the job posting is relevant to', ('Not Specified', 'Marketing and Advertising', 'Computer Software', 'Hospital & Health Care', 'Online Media', 'Information Technology and Services', 'Financial Services', 'Management Consulting', 'Internet', 'Telecommunications', 'Consumer Services', 'Construction', 'Oil & Energy', 'Education Management', 'Health, Wellness and Fitness', 'Insurance', 'E-Learning', 'Staffing and Recruiting', 'Human Resources', 'Real Estate', 'Automotive', 'Logistics and Supply Chain', 'Design', 'Accounting', 'Retail','Others'))
                function = st.selectbox('Please choose which umbrella term matches job\'s functionality?', ('Not Specified', 'Marketing', 'Customer Service', 'Sales', 'Health Care Provider', 'Management', 'Information Technology', 'Engineering', 'Administrative', 'Design', 'Production', 'Education', 'Business Development', 'Product Management', 'Consulting', 'Human Resources', 'Project Management', 'Finance', 'Accounting/Auditing', 'Art/Creative', 'Quality Assurance', 'Writing/Editing', 'Other'))

                if st.button('Get Your Prediction'):
                    no_count = (telecommuting == 'No') + (has_company_logo == 'No') + (has_questions == 'No') + (employment_type == 'Not Specified') + (required_experience == 'Not Applicable') + (required_education == 'Unspecified') + (industry == 'Not Specified') + (function == 'Not Specified')
                    result = "Fake" if no_count >= 2 else "Real"
                    st.write(f"The given job posting is {result}")
    else:
        # Directly displaying classifier questions if it's not a URL
        st.subheader('Enter the details:')

            # Questions and options for the classifier
        telecommuting = st.radio('Is work from home or remote work allowed?', options=['Yes', 'No'])
        has_company_logo = st.radio('Does the job posting have a company logo?', options=['Yes', 'No'])
        has_questions = st.radio('Does the job posting have questions?', options=['Yes', 'No'])
        employment_type = st.selectbox('What is the employment type?', ('Not Specified', 'Other', 'Part-time', 'Contract', 'Temporary', 'Full-time'))
        required_experience = st.selectbox('What is the required experience?', ('Not Applicable', 'Internship', 'Entry level', 'Mid-Senior level', 'Associate',  'Executive', 'Director'))
        required_education = st.selectbox('What is the required education?', ('Unspecified', 'Vocational - HS Diploma', 'Some High School Coursework', 'High School or equivalent', 'Some College Coursework Completed', 'Certification', 'Vocational', 'Vocational - Degree', "Bachelor's Degree", "Master's Degree", 'Associate Degree', 'Professional', 'Doctorate'))
        industry = st.selectbox('Please choose which industry the job posting is relevant to', ('Not Specified', 'Marketing and Advertising', 'Computer Software', 'Hospital & Health Care', 'Online Media', 'Information Technology and Services', 'Financial Services', 'Management Consulting', 'Internet', 'Telecommunications', 'Consumer Services', 'Construction', 'Oil & Energy', 'Education Management', 'Health, Wellness and Fitness', 'Insurance', 'E-Learning', 'Staffing and Recruiting', 'Human Resources', 'Real Estate', 'Automotive', 'Logistics and Supply Chain', 'Design', 'Accounting', 'Retail','Others'))
        function = st.selectbox('Please choose which umbrella term matches job\'s functionality?', ('Not Specified', 'Marketing', 'Customer Service', 'Sales', 'Health Care Provider', 'Management', 'Information Technology', 'Engineering', 'Administrative', 'Design', 'Production', 'Education', 'Business Development', 'Product Management', 'Consulting', 'Human Resources', 'Project Management', 'Finance', 'Accounting/Auditing', 'Art/Creative', 'Quality Assurance', 'Writing/Editing', 'Other'))

        if st.button('Get Your Prediction'):
                no_count = (telecommuting == 'No') + (has_company_logo == 'No') + (has_questions == 'No') + (employment_type == 'Not Specified') + (required_experience == 'Not Applicable') + (required_education == 'Unspecified') + (industry == 'Not Specified') + (function == 'Not Specified')
                result = "Fake" if no_count >= 2 else "Real"
                st.write(f"The given job posting is {result}")

# Display login page until successful login
if not getattr(session_state, 'logged_in', False) and app_mode != 'Login':
    st.sidebar.radio('Select Page', ['Login'])
