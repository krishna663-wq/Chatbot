# from langchain.prompts import (
#     ChatPromptTemplate,
#     HumanMessagePromptTemplate,
#     MessagesPlaceholder,
#     SystemMessagePromptTemplate,
# )
# from langchain_community.chat_message_histories import StreamlitChatMessageHistory
# from langchain_core.runnables.history import RunnableWithMessageHistory
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain.schema.output_parser import StrOutputParser
# import streamlit as st
# import time
# from datetime import datetime

# Modify imports
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    SystemMessagePromptTemplate
)
from langchain_core.messages import MessagesPlaceholder
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
import streamlit as st
import time
from datetime import datetime

# Streamlit app configuration
st.set_page_config(
    page_title="Professional AI Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced Custom CSS with professional styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(135deg, #24292e, #4A90E2);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.8rem !important;
        font-weight: 700 !important;
        margin-bottom: 0.5rem !important;
        text-align: center;
        padding: 1rem 0;
    }
    
    .creator-credit {
        text-align: center;
        color: #4A4A4A;
        font-size: 1rem;
        margin-bottom: 2rem;
        font-weight: 500;
    }
    
    .chat-container {
        padding: 2rem;
        border-radius: 12px;
        margin: 1.5rem 0;
        background: steelblue;
        box-shadow: blue;
    }
    
    .chat-message {
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.8rem 0;
        animation: slideIn 0.3s ease;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
        color: #FFFFFF;
    }
    
    .user-message {
        background: steelblue;
        margin-left: 2rem;
        border-left: 4px solid #2196F3;
    }
    
    .assistant-message {
        background: black;
        margin-right: 2rem;
        border-left: 4px solid #4A90E2;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 0.8rem;
        background: #24292e;
        color: white;
        text-align: center;
        font-size: 0.9rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        z-index: 1000;
    }
    
    .status-item {
        display: inline-flex;
        align-items: center;
        margin: 0 1rem;
    }
    
    .loader {
        width: 24px;
        height: 24px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #4A90E2;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
    }
    
    .sidebar-header {
        background: black;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
    
    .professional-input {
        border: 2px solid #E0E0E0;
        border-radius: 8px;
        padding: 0.8rem;
        transition: all 0.3s ease;
    }
    
    .professional-input:focus {
        border-color: #4A90E2;
        box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
    
if 'chat_cleared' not in st.session_state:
    st.session_state.chat_cleared = False

# Enhanced Sidebar Configuration
with st.sidebar:
    st.markdown('<div class="sidebar-header"><h2>⚙️ Configuration Panel</h2></div>', unsafe_allow_html=True)
    
    temperature = st.slider(
        "Intelligence Creativity Level",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
        help="Adjust the creativity level of responses"
    )
    
    if temperature < 0.3:
        st.info("🎯 Precise & Focused Responses")
    elif temperature < 0.7:
        st.success("⚖️ Balanced & Nuanced Responses")
    else:
        st.warning("💡 Creative & Exploratory Responses")
    
    model_name = st.radio(
        "Select AI Model:",
        ["gemini-1.5-pro", "gemini-1.5-flash"],
        help="Choose the AI model that best suits your needs"
    )
    
    if st.button("🔄 Clear Conversation", help="Erase all chat history"):
        StreamlitChatMessageHistory(key="langchain_messages").clear()
        st.session_state.messages = []
        st.session_state.chat_cleared = True
        st.success("Conversation history has been cleared!")

# Main Content with Enhanced Header
st.markdown('<h1 class="main-title">Professional AI Assistant</h1>', unsafe_allow_html=True)
st.markdown('<p class="creator-credit">Developed by Krishna Gopal Sharma | Advanced AI Solutions</p>', unsafe_allow_html=True)

# Welcome message with professional styling
st.markdown("""
    <div class="chat-container">
        <h3>Welcome to Your Professional AI Assistant</h3>
        <p>I'm your dedicated AI companion, engineered to provide expert assistance and insights. 
        How may I help you today?</p>
    </div>
""", unsafe_allow_html=True)

# Function to get API key with enhanced styling
def get_api_key():
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = "AIzaSyCHC8isbg40fjG_GpQhhat-wD2soflKYyY"
    return st.text_input(
        "Enter API Key:",
        type="password",
        key="api_key",
        help="Enter your Google API key to access the AI services"
    )

# Get API key
api_key = get_api_key()

# Main chat interface
if api_key:
    # Create enhanced prompt template
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """You are a Professional AI Assistant, engineered by Krishna Gopal Sharma.
                Deliver comprehensive, accurate, and professionally-toned responses while maintaining
                a balance between expertise and accessibility."""
            ),
            MessagesPlaceholder(variable_name="chat_history"),
            HumanMessagePromptTemplate.from_template("{question}"),
        ]
    )

    # Initialize message history
    msgs = StreamlitChatMessageHistory(key="langchain_messages")

    # Set up model
    model = ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=temperature
    )

    # Set up chain
    chain = prompt | model | StrOutputParser()
    chain_with_history = RunnableWithMessageHistory(
        chain,
        lambda session_id: msgs,
        input_messages_key="question",
        history_messages_key="chat_history",
    )

    # Display chat history
    if not st.session_state.chat_cleared:
        for message in msgs.messages:
            role = "assistant" if message.type == "ai" else "human"
            with st.chat_message(role):
                st.markdown(f'<div class="chat-message {role}-message">{message.content}</div>', 
                           unsafe_allow_html=True)

    # Reset chat cleared flag
    st.session_state.chat_cleared = False

    # Enhanced chat input
    user_input = st.chat_input("Type your message here...")

    if user_input:
        with st.chat_message("human"):
            st.markdown(f'<div class="chat-message user-message">{user_input}</div>',
                       unsafe_allow_html=True)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            message_placeholder.markdown('<div class="loader"></div>', unsafe_allow_html=True)

            try:
                config = {"configurable": {"session_id": "any"}}
                response = chain_with_history.stream({"question": user_input}, config)

                for res in response:
                    full_response += res or ""
                    time.sleep(0.02)
                    message_placeholder.markdown(
                        f'<div class="chat-message assistant-message">{full_response}▌</div>',
                        unsafe_allow_html=True
                    )

                message_placeholder.markdown(
                    f'<div class="chat-message assistant-message">{full_response}</div>',
                    unsafe_allow_html=True
                )

            except Exception as e:
                st.error(f"Error: {str(e)}")
                st.info("Please verify your API key and try again.")

    # Enhanced status bar
    st.markdown(
        f'''
        <div class="status-bar">
            <div class="status-item">🟢 System Active</div>
            <div class="status-item">📊 Model: {model_name}</div>
            <div class="status-item">🎯 Precision: {temperature:.1f}</div>
            <div class="status-item">⏰ {datetime.now().strftime("%H:%M:%S")}</div>
            <div class="status-item">👨‍💻 Krishna Gopal Sharma</div>
        </div>
        ''',
        unsafe_allow_html=True
    )

else:
    st.warning("Please provide your API Key to begin.")