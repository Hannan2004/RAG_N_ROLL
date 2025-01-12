import streamlit as st
from snowflake.snowpark import Session
from snowflake.snowpark.context import get_active_session
from snowflake.cortex import Complete
from snowflake.core import Root
import pandas as pd
from datetime import datetime

# Set pandas options
pd.set_option("max_colwidth", None)

# Configuration
NUM_CHUNKS = 3
SLIDE_WINDOW = 7
CORTEX_SEARCH_DATABASE = st.secrets["connections"]["snowflake"]["database"]
CORTEX_SEARCH_SCHEMA = st.secrets["connections"]["snowflake"]["schema"]
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"  # Update if needed
MODEL_NAME = "mistral-large2"
COLUMNS = ["chunk", "relative_path", "category"]

# Snowflake session initialization
def create_session():
    """Create or reuse a Snowflake session."""
    if "snowflake_session" not in st.session_state:
        connection_parameters = {
            "account": st.secrets["connections"]["snowflake"]["account"],
            "user": st.secrets["connections"]["snowflake"]["user"],
            "password": st.secrets["connections"]["snowflake"]["password"],
            "role": st.secrets["connections"]["snowflake"]["role"],
            "warehouse": st.secrets["connections"]["snowflake"]["warehouse"],
            "database": st.secrets["connections"]["snowflake"]["database"],
            "schema": st.secrets["connections"]["snowflake"]["schema"],
        }
        st.session_state.snowflake_session = Session.builder.configs(connection_parameters).create()
    return st.session_state.snowflake_session

# Initialize Snowflake Root
session = create_session()
root = Root(session)
svc = root.databases[CORTEX_SEARCH_DATABASE].schemas[CORTEX_SEARCH_SCHEMA].cortex_search_services[CORTEX_SEARCH_SERVICE]

# Enhanced Functions
def init_session_state():
    """Initialize all session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    if "feedback" not in st.session_state:
        st.session_state.feedback = {}
    if "selected_country" not in st.session_state:
        st.session_state.selected_country = None
    if "business_type" not in st.session_state:
        st.session_state.business_type = None

def get_similar_chunks_search_service(query):
    """Fetch similar chunks with error handling."""
    try:
        response = svc.search(query, COLUMNS, limit=NUM_CHUNKS)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching similar chunks: {str(e)}")
        return []

def get_chat_history():
    """Retrieve recent chat history."""
    chat_history = []
    start_index = max(0, len(st.session_state.messages) - SLIDE_WINDOW)
    for i in range(start_index, len(st.session_state.messages) - 1):
        chat_history.append(st.session_state.messages[i])
    return chat_history

def create_prompt(myquestion, country=None, business_type=None):
    """Create an enhanced prompt with business context."""
    chat_history = get_chat_history()
    prompt_context = get_similar_chunks_search_service(myquestion)

    context_info = ""
    if country:
        context_info += f"\nCountry: {country}"
    if business_type:
        context_info += f"\nBusiness Type: {business_type}"

    prompt = f"""
    You are a highly intelligent business assistant specializing in providing concise and accurate answers about setting up businesses internationally.
    {context_info}

    Use the information between <context> tags to address the user's question and offer actionable insights.
    If the information isn't in the context, you can provide general guidance based on common business practices.
    Focus on practical, step-by-step advice when applicable.

    <chat_history>
    {chat_history}
    </chat_history>

    <context>
    {prompt_context}
    </context>

    <question>
    {myquestion}
    </question>

    Answer:
    """
    return prompt

def answer_question(myquestion, country=None, business_type=None):
    """Generate an answer for the user's question with enhanced context."""
    try:
        prompt = create_prompt(myquestion, country, business_type)
        response = Complete('mistral-large2', prompt)
        return response
    except Exception as e:
        error_message = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
        return error_message

def display_chat_interface():
    """Display an enhanced chat interface with message timestamps."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            col1, col2 = st.columns([6, 1])
            with col2:
                if message["role"] == "assistant":
                    if st.button("👍", key=f"like_{len(st.session_state.messages)}"):
                        st.session_state.feedback[len(st.session_state.messages)] = "positive"
                        st.toast("Thank you for your feedback!")
                    if st.button("👎", key=f"dislike_{len(st.session_state.messages)}"):
                        st.session_state.feedback[len(st.session_state.messages)] = "negative"
                        st.toast("Thank you for your feedback. We'll work on improving.")

def main():
    st.set_page_config(
        page_title="International Business Setup Assistant",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Initialize session state
    init_session_state()

    # Sidebar for business context
    with st.sidebar:
        st.header("Business Context")
        countries = ["India", "United States", "United Kingdom", "Singapore", "Spain", "Philippines", "Russia", "Other"]
        selected_country = st.selectbox("Select Country", countries)

        business_types = ["LLC", "Corporation", "Sole Proprietorship", "Partnership", "Other"]
        selected_business_type = st.selectbox("Business Type", business_types)

        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.rerun()

    # Main chat interface
    st.title("🌐 International Business Setup Assistant")
    st.markdown("""
    Welcome! I'm here to help you establish your business internationally. 
    Select your target country and business type in the sidebar, then ask specific questions about:
    - Registration processes
    - Legal requirements
    - Tax considerations
    - Licensing needs
    - Cost estimates
    """)

    # Display chat interface
    display_chat_interface()

    # Chat input
    if question := st.chat_input("Ask about setting up your business..."):
        # Add user message
        st.session_state.messages.append({
            "role": "user",
            "content": question,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

        # Display user message
        with st.chat_message("user"):
            st.markdown(question)

        # Generate response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            with st.spinner(f"Researching..."):
                response = answer_question(
                    question,
                    country=selected_country,
                    business_type=selected_business_type
                )
                message_placeholder.markdown(response)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

if __name__ == "__main__":
    main()
