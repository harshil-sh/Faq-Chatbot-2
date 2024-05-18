import pandas as pd
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from flask import Flask, session, request, jsonify
from flask_cors import CORS
from utilities.db_utils import DatabaseUtility

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


# Function to get the best matching answer
def get_answer(query):
    query_processed = preprocess(query)
    query_vector = vectorizer.transform([query_processed])
    similarities = cosine_similarity(query_vector, X)
    best_match_idx = similarities.argmax()
    return df.iloc[best_match_idx]['Answer']

def fetch_employee_details():
    with DatabaseUtility() as db:
        query_result = db.execute_query("Select CustomerID,FullName from CustomerData where Email=?",(email))
        custid = 0
        fullname = ''
        if query_result is not None:
            for row in query_result:
                custid=row['CustomerID']
                fullname=row['FullName']
    if custid:
        session['custid'] = custid
    if fullname:
        session['fullname'] = fullname                
    return custid,fullname


# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super_secret_key'
CORS(app)  # Enable CORS

# Define the route for the FAQ chatbot
@app.route('/get_answer', methods=['POST'])
def handle_get_answer():
    data = request.json
    query = data.get('query', '')
    if not query:
        return jsonify({'error': 'No query provided'}), 400
    answer = get_answer(query)
    
    
    return jsonify({'answer': answer})

if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000, debug=True)
