import pickle
import streamlit as st
import plotly.graph_objects as go

# Load the saved diabetes model
diabetes_model = pickle.load(open('saved_models/diabetes_model.sav', 'rb'))

# Main page
st.title('Diabetes Prediction using ML')

col1, col2, col3 = st.columns(3)

with col1:
    Pregnancies = st.text_input('Number of Pregnancies')
with col2:
    Glucose = st.text_input('Glucose Level')
with col3:
    BloodPressure = st.text_input('Blood Pressure value')
with col1:
    SkinThickness = st.text_input('Skin Thickness value')
with col2:
    Insulin = st.text_input('Insulin Level')
with col3:
    BMI = st.text_input('BMI value')
with col1:
    DiabetesPedigreeFunction = st.text_input('Diabetes Pedigree Function value')
with col2:
    Age = st.text_input('Age of the Person')

# Function to handle empty inputs and convert them to floats
def handle_empty_input(input_values):
    return [float(x) if x.strip() else 0.0 for x in input_values]

# Prediction button and result
if st.button('Diabetes Test Result'):
    try:
        # Handle empty inputs
        user_input = handle_empty_input([Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age])
        
        # Prediction
        diab_prediction = diabetes_model.predict([user_input])
        result = 'The person is diabetic' if diab_prediction[0] == 1 else 'The person is not diabetic'
        st.success(result)
        
        # Data for plotting
        features = ['Pregnancies', 'Glucose', 'BloodPressure', 'SkinThickness', 'Insulin', 'BMI', 'DiabetesPedigreeFunction', 'Age']
        values = user_input
        
        # Interactive Bar Chart with Plotly
        fig = go.Figure()
        fig.add_trace(go.Bar(x=features, y=values, name='Feature Values'))
        fig.update_layout(title='Feature Values for Diabetes Prediction', xaxis_title='Features', yaxis_title='Values')
        st.plotly_chart(fig)
        
        # Interactive Pie Chart with Plotly
        fig = go.Figure()
        fig.add_trace(go.Pie(labels=features, values=values, hole=0.3))
        fig.update_layout(title='Feature Proportions for Diabetes Prediction')
        st.plotly_chart(fig)
        
    except ValueError:
        st.error("Please enter valid values for all fields.")
