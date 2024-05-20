import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, session, request, jsonify
from flask_cors import CORS
from utilities.db_utils import DatabaseUtility
import smtplib
import random
import string

nltk.download('stopwords')

# Load and preprocess the data
df = pd.read_csv('c:\\Users\\Admin\\Documents\\Python\\Faq ChatBot 2\\BackEnd\\faqs.csv')

stop_words = set(stopwords.words('english'))
def preprocess(text):
    tokens = nltk.word_tokenize(text.lower())
    filtered_tokens = [word for word in tokens if word.isalnum() and word not in stop_words]
    return ' '.join(filtered_tokens)

df['Processed_Question'] = df['Question'].apply(preprocess)

# Vectorize the questions
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['Processed_Question'])

# Email setup (use your email credentials and settings)
SMTP_SERVER = 'smtp.your-email-provider.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'your-email@example.com'
EMAIL_PASSWORD = 'your-email-password'

def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))

def send_otp(email, otp):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            message = f"Subject: Your OTP Code\n\nYour OTP code is {otp}"
            server.sendmail(EMAIL_ADDRESS, email, message)
    except Exception as e:
        print(f"Error sending OTP email: {e}")


# Function to get the best matching answer
def get_answer(query):
    query_processed = preprocess(query)
    query_vector = vectorizer.transform([query_processed])
    similarities = cosine_similarity(query_vector, X)
    best_match_idx = similarities.argmax()
    return df.iloc[best_match_idx]['Answer']

# Function to fetch employee details
def fetch_employee_details(email):
    with DatabaseUtility() as db:
        query_result = db.execute_query("SELECT CustomerID, FullName FROM CustomerData WHERE Email=?", (email,))
        if query_result:
            for row in query_result:
                return row['CustomerID'], row['FullName']
    return None, None

def fetch_order_details(customer_id, order_number):
    with DatabaseUtility() as db:
        query_result = db.execute_stored_procedure("sp_FetchOrderDetails", customer_id, order_number)
        if not query_result:
            return "Invalid Order Number. Please Enter a valid Order Number"
        items = [f"{row['Quantity']} X {row['ProductName']}" for row in query_result[1]]
        return {"order_id": order_number, "status": query_result[0]["status"], "items": items}

def handle_user_query(data):
    query = data.get('query', '')
    email = data.get('email', '')
    otp = data.get('otp', '')
    order_number = data.get('order_number', '')
    
    if not query:
        return {'error': 'No query provided'}, 400

    if 'track' in query.lower() and 'order' in query.lower():
        if 'email' not in session:
            if not email:
                return {'prompt': 'Please provide your email address to track your order'}, 200
            otp_code = generate_otp()
            session['otp'] = otp_code
            session['email'] = email
            send_otp(email, otp_code)
            return {'prompt': 'An OTP has been sent to your email. Please provide the OTP to continue.'}, 200
        
        if not otp:
            return {'prompt': 'Please provide the OTP sent to your email'}, 200
        
        if otp != session.get('otp'):
            return {'error': 'Invalid OTP. Please try again.'}, 401
        
        if not order_number:
            return {'prompt': 'Please provide your order number'}, 200
        
        custid, fullname = fetch_employee_details(session['email'])
        if not custid:
            return {'error': 'No customer found with the provided email'}, 404
        
        order_details = fetch_order_details(custid, order_number)
        session.pop('otp', None)
        session.pop('email', None)
        return {'CustomerID': custid, 'FullName': fullname, 'OrderDetails': order_details}
    
    answer = get_answer(query)
    return {'answer': answer}


# Initialize Flask app
app = Flask(__name__)
app.secret_key = '6a0b79c8d64a1c3e5f3a7b9d4a2b1c6e7d8e9f7a6b8c9d1e2f3a4b5c6d7e8f9a'
CORS(app)  # Enable CORS

# Define the route for the FAQ chatbot
@app.route('/get_answer', methods=['POST'])
def get_answer():
    data = request.json
    response, status_code = handle_user_query(data)
    return jsonify(response), status_code

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
