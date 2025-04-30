import streamlit as st
import requests
import pandas as pd
import os
import nltk
from nltk.tokenize import word_tokenize
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from textblob import TextBlob

nltk.data.path.append(os.path.abspath("nltk_data"))
nltk.download('punkt_tab')

# Google Custom Search API Config
API_KEY = "AIzaSyBGKiSPD8Aj1TWm1OqE9Cpn0laxzE1n0O0"  # Replace with your API key
SEARCH_ENGINE_ID = "57e4625115f494176"  # Replace with your CSE ID
CSV_FILE = "search_history.csv"  # File to store search history

# Apply Web Designing with Custom CSS
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg,lightgreen,rgb(119, 235, 108));
            color: #333;
        }
        .sidebar .sidebar-content {
            background: linear-gradient(135deg, #a1c4fd, #c2e9fb);
        }
        h1 {
            color: black;
            text-align: center;
            font-size: 32px;
        }
        .stTextInput>div>div>input {
            background-color: white;
            color:darkblue;
            border: 2px solidrgb(73, 18, 20);
            border-radius: 8px;
        }
        .stButton>button {
            background-color: #ff758c;
            color: white;
            border-radius: 8px;
            padding: 10px;
        }
        @keyframes scrollText {
            from { transform: translateX(100%); }
            to { transform: translateX(-100%); }
        }
        .scrolling-title {
            font-size: 40px;
            font-weight: bold;
            color: green;
            white-space: nowrap;
            overflow: hidden;
            display: inline-block;
            animation: scrollText 10s linear infinite;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Sidebar Navigation
st.sidebar.title("🌾 AgriBot Menu")
page = st.sidebar.radio("Go to", ["Chatbot", "Search History"])

# NLP Functions
def search_google(query):
    """Fetches results from Google Custom Search API in Telugu"""
    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={SEARCH_ENGINE_ID}&hl=te"
    response = requests.get(url).json()
    
    results = []
    for item in response.get("items", []):
        # Translate title and snippet to Telugu
        title = translate_text(item["title"], target_lang="te")
        snippet = translate_text(item["snippet"], target_lang="te")
        results.append({"title": title, "link": item["link"], "snippet": snippet})
    
    return results

def preprocess_query(query):
    """Preprocesses user query using NLP (tokenization)"""
    tokens = word_tokenize(query.lower())
    return " ".join(tokens)

def summarize_text(text, sentences=2):
    """Summarizes text using LSA (Latent Semantic Analysis)"""
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences)
    return " ".join([str(sentence) for sentence in summary])

def translate_text(text, target_lang="te"):
    """Translates text to Telugu using TextBlob"""
    try:
        return str(TextBlob(text).translate(to=target_lang))
    except:
        return text  # Return original text if translation fails

def save_to_csv(query, results):
    """Saves search query and results to a CSV file"""
    data = []
    for result in results:
        summarized_snippet = summarize_text(result["snippet"])
        data.append([query, result["title"], result["link"], summarized_snippet])
    
    df = pd.DataFrame(data, columns=["Query", "Title", "Link", "Summary"])
    
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, mode='w', header=True, index=False)

def detect_greeting(query):
    """Detects if the user input is a greeting"""
    greetings_keywords = ['hello', 'hi', 'good morning', 'good afternoon', 'good evening', 'hey', 'hi there', 'bye', 'goodbye', 'take care']
    query = query.lower()
    return any(greeting in query for greeting in greetings_keywords)

# Page Selection
if page == "Chatbot":
    st.markdown("<div class='scrolling-title'>🌾 AgriBot - Your Smart Agricultural Assistant 🚜</div>", unsafe_allow_html=True)
    
    query = st.text_input(translate_text("Enter your query:", "te"))
    
    if query:
        if detect_greeting(query):
            st.markdown(f"<h1 style='color: #333333;'>{translate_text('Hello, Welcome to Agribot! How can I assist you today?', 'te')}</h1>", unsafe_allow_html=True)
        else:
            processed_query = preprocess_query(query)
            search_results = search_google(processed_query)
            
            if not search_results:
                st.warning(translate_text("No relevant results found. Try rephrasing your query.", "te"))
            else:
                st.subheader(translate_text("Top Results:", "te"))
                for result in search_results[:5]:
                    st.markdown(f"**[{result['title']}]({result['link']})**")
                    st.write(result['snippet'])
                    st.write("---")
                
                save_to_csv(query, search_results)
                st.success(translate_text("Your search history has been saved!", "te"))

elif page == "Search History":
    st.title(translate_text("📂 Search History", "te"))
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        st.dataframe(df)
    else:
        st.warning(translate_text("No search history found.", "te"))
