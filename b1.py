import streamlit as st
from PIL import Image
import pandas as pd
import csv
import os
import pickle

# Loading the classification model
model = pickle.load(open('job_posting.pkl', 'rb'))

# Custom CSS styles
st.markdown(
    """
    <style>
    .btn-primary {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        border-radius: 5px;
        cursor: pointer;
    }
    .btn-primary:hover {
        background-color: #45A049;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Main layout
st.markdown('<h1 style="text-align: center;">Job Posting Classifier</h1>', unsafe_allow_html=True)

# Sidebar navigation
app_mode = st.sidebar.radio('Select Page', ['Login', 'Classifier', 'Feedback', 'Register'])

# Login page
if app_mode == 'Login':
    st.sidebar.title("Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_button = st.sidebar.button("Login", key="login_button", help="btn-primary")

    if login_button:
        if username == "admin" and password == "secret":
            st.success("Login successful!")
            app_mode = 'Feedback'  # Redirect to the feedback page on successful login
        else:
            st.error("Invalid username or password.")

# Registration page
elif app_mode == 'Register':
    st.title('User Registration')
    username = st.text_input("Username")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    retype_password = st.text_input("Retype Password", type="password")

    if st.button("Register", key="register_button", help="btn-primary"):
        if not (username and email and password and retype_password):
            st.error("Please fill in all the fields.")
        elif password != retype_password:
            st.error("Passwords do not match.")
        else:
            with open('user_data.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([username, email, password])
            st.success("Registration successful!")
            app_mode = 'Classifier'

# Feedback form
elif app_mode == 'Feedback':
    st.title('Feedback Form')
    company_name = st.text_input("Enter Company Name")
    reference_link = st.text_input("Enter Reference Link")
    is_real_posting = st.radio("Was this a real job posting?", ("Yes", "No", "Unsure"))

    if st.button('Submit Feedback', key="feedback_button", help="btn-primary"):
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

# Classifier page
elif app_mode == 'Classifier':
    st.title("Job Posting Classifier: Real/Fake")
    user_input = st.text_input("Enter Job Posting Source Link or Upload Image")

    if user_input:
        st.subheader('Enter the details:')
        telecommuting = st.radio('Is work from home or remote work allowed?', options=['Yes', 'No'])
        has_company_logo = st.radio('Does the job posting have a company logo?', options=['Yes', 'No'])
        has_questions = st.radio('Does the job posting have questions?', options=['Yes', 'No'])
        employment_type = st.selectbox('What is the employment type?', ('Not Specified', 'Other', 'Part-time', 'Contract', 'Temporary', 'Full-time'))
        required_experience = st.selectbox('What is the required experience?', ('Not Applicable', 'Internship', 'Entry level', 'Mid-Senior level', 'Associate',  'Executive', 'Director'))
        required_education = st.selectbox('What is the required education?', ('Unspecified', 'Vocational - HS Diploma', 'Some High School Coursework', 'High School or equivalent', 'Some College Coursework Completed', 'Certification', 'Vocational', 'Vocational - Degree', "Bachelor's Degree", "Master's Degree", 'Associate Degree', 'Professional', 'Doctorate'))
        industry = st.selectbox('Please choose which industry the job posting is relevant to', ('Not Specified', 'Marketing and Advertising', 'Computer Software', 'Hospital & Health Care', 'Online Media', 'Information Technology and Services', 'Financial Services', 'Management Consulting', 'Internet', 'Telecommunications', 'Consumer Services', 'Construction', 'Oil & Energy', 'Education Management', 'Health, Wellness and Fitness', 'Insurance', 'E-Learning', 'Staffing and Recruiting', 'Human Resources', 'Real Estate', 'Automotive', 'Logistics and Supply Chain', 'Design', 'Accounting', 'Retail','Others'))
        function = st.selectbox('Please choose which umbrella term matches job\'s functionality?', ('Not Specified', 'Marketing', 'Customer Service', 'Sales', 'Health Care Provider', 'Management', 'Information Technology', 'Engineering', 'Administrative', 'Design', 'Production', 'Education', 'Business Development', 'Product Management', 'Consulting', 'Human Resources', 'Project Management', 'Finance', 'Accounting/Auditing', 'Art/Creative', 'Quality Assurance', 'Writing/Editing', 'Other'))

        if st.button('Get Your Prediction', key="prediction_button", help="btn-primary"):
            no_count = (telecommuting == 'No') + (has_company_logo == 'No') + (has_questions == 'No') + (employment_type == 'Not Specified') + (required_experience == 'Not Applicable') + (required_education == 'Unspecified') + (industry == 'Not Specified') + (function == 'Not Specified')
            result = "Fake" if no_count >= 2 else "Real"
            st.write(f"The given job posting is {result}")
