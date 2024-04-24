import numpy as np
import pickle
import pandas as pd
import streamlit as st
from PIL import Image
import requests
from io import BytesIO
import os

# Loading up the Classification model we created
model = pickle.load(open('job_posting.pkl', 'rb'))

# Create a SessionState class to store the image and user inputs
class SessionState:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

# Initialize SessionState
session_state = SessionState(image=None)

# Function to handle login logic
def login(username, password):
    if username == "admin" and password == "secret":
        session_state.logged_in = True
        st.success("Login successful!")
    else:
        st.error("Invalid username or password.")

# Feedback function to store feedback in CSV
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
app_mode = st.sidebar.radio('Select Page', ['Login', 'Classifier', 'Feedback'])  # three pages

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
    user_input = st.text_input("Enter Job Posting Source Link")
    
    # Store the uploaded image in session state
    if user_input:
        if user_input.startswith(('http://', 'https://')):
            response = requests.get(user_input)
            if response.status_code == 200:
                session_state.image = Image.open(BytesIO(response.content))
                st.image(session_state.image, caption='Job Posting Image', use_column_width=True)
            else:
                st.error("Error fetching image. Please check the URL.")
        else:
            st.error("Please provide a valid URL starting with http:// or https://")
    
    if st.button('Reset Input'):
        session_state.image = None

    if session_state.image:
        st.subheader('Enter the details:')
        
        # Question 1: Is work from home or remote work allowed?
        telecommuting = st.radio('Is work from home or remote work allowed?', options=['Yes', 'No'])
        
        # Question 2: Does the job posting have a company logo?
        has_company_logo = st.radio('Does the job posting have a company logo?', options=['Yes', 'No'])
        
        # Question 3: Does the job posting have questions?
        has_questions = st.radio('Does the job posting have questions?', options=['Yes', 'No'])
        
        # Question 4: What is the employment type?
        employment_type = st.selectbox('What is the employment type?',
                                       ('Not Specified', 'Other', 'Part-time', 'Contract', 'Temporary', 'Full-time'))
        
        # Question 5: What is the required experience?
        required_experience = st.selectbox('What is the required experience?',
                                           ('Not Applicable', 'Internship', 'Entry level', 'Mid-Senior level',
                                            'Associate',  'Executive', 'Director'))
        
        # Question 6: What is the required education?
        required_education = st.selectbox('What is the required education?',
                                          ('Unspecified', 'Vocational - HS Diploma', 'Some High School Coursework', 'High School or equivalent',
                                           'Some College Coursework Completed', 'Certification', 'Vocational', 'Vocational - Degree', "Bachelor's Degree",
                                           "Master's Degree", 'Associate Degree', 'Professional', 'Doctorate'))
        
        # Question 7: Please choose which industry the job posting is relevant to
        industry = st.selectbox('Please choose which industry the job posting is relevant to',
                                ('Not Specified', 'Marketing and Advertising', 'Computer Software',
                                 'Hospital & Health Care', 'Online Media',
                                 'Information Technology and Services', 'Financial Services',
                                 'Management Consulting', 'Internet',
                                 'Telecommunications', 'Consumer Services', 'Construction',
                                 'Oil & Energy', 'Education Management',
                                 'Health, Wellness and Fitness', 'Insurance', 'E-Learning',
                                 'Staffing and Recruiting', 'Human Resources', 'Real Estate',
                                 'Automotive', 'Logistics and Supply Chain', 'Design', 'Accounting',
                                 'Retail','Others'))
        
        # Question 8: Please choose which umbrella term matches job's functionality?
        function = st.selectbox('Please choose which umbrella term matches job\'s functionality?',
                                ('Not Specified', 'Marketing', 'Customer Service', 'Sales',
                                 'Health Care Provider', 'Management', 'Information Technology',
                                 'Engineering', 'Administrative', 'Design', 'Production',
                                 'Education', 'Business Development', 'Product Management',
                                 'Consulting', 'Human Resources', 'Project Management', 'Finance',
                                 'Accounting/Auditing', 'Art/Creative', 'Quality Assurance',
                                 'Writing/Editing', 'Other'))

        if st.button('Get Your Prediction'):
            # Count 'No' and 'Unspecified' answers
            no_count = (telecommuting == 'No') + (has_company_logo == 'No') + (has_questions == 'No') + (employment_type == 'Not Specified') + \
                       (required_experience == 'Not Applicable') + (required_education == 'Unspecified') + (industry == 'Not Specified') + \
                       (function == 'Not Specified')
            
            # Set result based on the count
            result = "Fake" if no_count >= 2 else "Real"
            
            # Display the result
            st.write(f"The given job posting is {result}")

# Display login page until successful login
if not getattr(session_state, 'logged_in', False) and app_mode != 'Login':
    st.sidebar.radio('Select Page', ['Login'])
