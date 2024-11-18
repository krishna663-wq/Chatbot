from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
)
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema.output_parser import StrOutputParser
import streamlit as st
import time
from datetime import datetime

# Streamlit app configuration
st.set_page_config(
    page_title="AI Text Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
    
    .stApp {
        font-family: 'Poppins', sans-serif;
    }
    
    .main-title {
        background: linear-gradient(45deg, #2E3192, #1BFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
        text-align: center;
    }
    
    .chat-container {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        animation: fadeIn 0.5s ease;
    }
    
    .user-message {
        background: rgba(46, 49, 146, 0.1);
        margin-left: 2rem;
    }
    
    .assistant-message {
        background: rgba(27, 255, 255, 0.1);
        margin-right: 2rem;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .status-bar {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 0.5rem;
        background: rgba(0, 0, 0, 0.8);
        color: white;
        text-align: center;
        font-size: 0.8rem;
    }
    
    .loader {
        width: 20px;
        height: 20px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto;
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

# Sidebar Configuration
with st.sidebar:
    st.markdown("### 🎮 Control Center")
    
    temperature = st.slider(
        "🌡️ Creativity Level",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1,
    )
    
    if temperature < 0.3:
        st.info("🧊 Conservative responses")
    elif temperature < 0.7:
        st.success("🌟 Balanced responses")
    else:
        st.warning("🔥 Creative responses")
    
    model_name = st.radio(
        "Choose your AI model:",
        ["gemini-1.5-flash", "gemini-1.5-pro"]
    )
    
    if st.button("🗑️ Clear Chat History"):
        StreamlitChatMessageHistory(key="langchain_messages").clear()
        st.session_state.messages = []
        st.session_state.chat_cleared = True
        st.success("Chat cleared!")

# Main Content
st.markdown('<h1 class="main-title">🤖 AI Genius Chat</h1>', unsafe_allow_html=True)

# Welcome message
st.markdown("""
    <div class="chat-container">
        <h3>👋 Welcome to AI Genius!</h3>
        <p>I'm your advanced AI assistant, powered by state-of-the-art language models.</p>
    </div>
""", unsafe_allow_html=True)

# Function to get API key
def get_api_key():
    if "api_key" not in st.session_state:
        st.session_state["api_key"] = "AIzaSyCHC8isbg40fjG_GpQhhat-wD2soflKYyY"
    return st.text_input(
        "🔑 Enter your Google API Key:",
        type="password",
        key="api_key"
    )

# Get API key
api_key = get_api_key()

# Main chat interface
if api_key:
    # Create prompt template
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                """You are AI Genius, an advanced AI assistant with a friendly personality.
                Provide detailed, accurate responses while maintaining a conversational tone."""
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

    # Display chat history if not cleared
    if not st.session_state.chat_cleared:
        for message in msgs.messages:
            role = "assistant" if message.type == "ai" else "human"
            with st.chat_message(role):
                st.markdown(f'<div class="chat-message {role}-message">{message.content}</div>', 
                           unsafe_allow_html=True)

    # Reset chat cleared flag
    st.session_state.chat_cleared = False

    # Chat input
    user_input = st.chat_input("💭 Ask me anything...")

    if user_input:
        # Display user message
        with st.chat_message("human"):
            st.markdown(f'<div class="chat-message user-message">{user_input}</div>',
                       unsafe_allow_html=True)

        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            # Show typing indicator
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
                st.error(f"🚨 Error: {str(e)}")
                st.info("🔄 Please try again or check your API key.")

    # Status bar
    st.markdown(
        f'<div class="status-bar">🔵 Online | Model: {model_name} | Temperature: {temperature:.1f} | {datetime.now().strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

else:
    st.warning("Please enter your API Key to continue.")

