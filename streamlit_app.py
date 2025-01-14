import streamlit as st
from snowflake.snowpark import Session
from snowflake.cortex import Complete
from snowflake.core import Root
import pandas as pd
from datetime import datetime
import time
import re

st.set_page_config(
    page_title="Business Setup Assistant",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.example.com/help',
        'Report a bug': "https://www.example.com/bug",
        'About': "Business Setup Assistant v1.0"
    }
)
conn = st.connection("snowflake")

# Set pandas options
pd.set_option("max_colwidth", None)

# Configuration
NUM_CHUNKS = 3
SLIDE_WINDOW = 7
CORTEX_SEARCH_DATABASE = st.secrets["connections"]["snowflake"]["database"]
CORTEX_SEARCH_SCHEMA = st.secrets["connections"]["snowflake"]["schema"]
CORTEX_SEARCH_SERVICE = "CC_SEARCH_SERVICE_CS"
CORTEX_SEARCH_TABLE = "DOCS_CHUNKS_TABLE"
MODEL_NAME = "mistral-large2"
COLUMNS = ["chunk", "relative_path", "category"]

def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        "messages": [],
        "conversation_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "feedback": {},
        "selected_country": None,
        "business_type": None,
        "theme": "light"
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


@st.cache_data
def get_similar_chunks(query):
    """Fetch similar chunks using Snowpark session."""
    session = conn.session()  # Get the Snowpark session
    try:
        # Query Snowflake using Snowpark
        result_df = (
            session.table(CORTEX_SEARCH_TABLE)
            .filter(f"chunk LIKE '%{query}%'")  # Adjust query as needed
            .select(*COLUMNS)
            .limit(NUM_CHUNKS)
            .to_pandas()  # Convert Snowpark DataFrame to pandas DataFrame
        )
        return result_df
    except Exception as e:
        st.error(f"Error fetching similar chunks: {str(e)}")
        return pd.DataFrame(columns=COLUMNS)


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
    prompt_context = get_similar_chunks(myquestion)

    context_info = "\n".join(filter(None, [
        f"Country: {country}" if country else "",
        f"Business Type: {business_type}" if business_type else ""
    ]))

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
    {prompt_context.to_string(index=False)}
    </context>

    <question>
    {myquestion}
    </question>

    Answer:
    """
    return prompt


def format_markdown(text):
    """Pre-format markdown text into proper sections."""
    # Split text into paragraphs
    paragraphs = text.split('\n\n')
    formatted_paragraphs = []

    for para in paragraphs:
        # Handle headers
        para = re.sub(r'###\s+(.+)', r'### \1', para)
        # Handle bullet points
        para = re.sub(r'^\*\s+(.+)', r'* \1', para, flags=re.MULTILINE)
        # Handle numbered lists
        para = re.sub(r'^\d+\.\s+(.+)', r'1. \1', para, flags=re.MULTILINE)
        # Handle bold text
        para = re.sub(r'\*\*(.+?)\*\*', r'**\1**', para)

        formatted_paragraphs.append(para)

    return '\n\n'.join(formatted_paragraphs)


def stream_response(response, message_placeholder):
    """Stream the response with a typewriter effect while maintaining markdown formatting."""
    # Pre-format the entire response
    formatted_response = format_markdown(response)

    # Split into paragraphs to maintain structure
    paragraphs = formatted_response.split('\n\n')
    current_text = ""

    for paragraph in paragraphs:
        words = paragraph.split(' ')
        for word in words:
            current_text += word + " "
            # Update with proper markdown formatting
            message_placeholder.markdown(current_text + "▌")
            time.sleep(0.03)  # Slightly faster typing speed

        # Add paragraph break
        current_text += '\n\n'
        message_placeholder.markdown(current_text + "▌")
        time.sleep(0.1)  # Slightly longer pause between paragraphs

    # Final update without cursor
    message_placeholder.markdown(current_text.rstrip())
    return current_text.rstrip()

def answer_question(myquestion, country=None, business_type=None):
    """Generate an answer for the user's question with enhanced context."""
    try:
        prompt = create_prompt(myquestion, country, business_type)
        response = Complete('mistral-large2', prompt)
        return response
    except Exception as e:
        error_message = f"I apologize, but I encountered an error: {str(e)}. Please try rephrasing your question."
        return error_message


def display_feedback_buttons(message_idx):
    """Display feedback buttons in a horizontal layout."""
    cols = st.columns([0.9, 0.05, 0.05])

    # Empty first column for spacing
    cols[0].write("")

    # Thumbs up button
    if cols[1].button("👍", key=f"like_{message_idx}"):
        st.session_state.feedback[message_idx] = "positive"
        st.toast("Thank you for your positive feedback!", icon="✅")

    # Thumbs down button
    if cols[2].button("👎", key=f"dislike_{message_idx}"):
        st.session_state.feedback[message_idx] = "negative"
        st.toast("Thank you for your feedback. We'll work on improving.", icon="📝")


def display_chat_interface():
    """Display an enhanced chat interface with message timestamps."""
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Display timestamp in small, muted text
            st.caption(f"Sent at {message['timestamp']}")

            # Only show feedback buttons for assistant messages
            if message["role"] == "assistant":
                display_feedback_buttons(idx)


def main():
    # Custom CSS for better UI
    st.markdown("""
        <style>
        .stSelectbox {
            margin-bottom: 1rem;
        }
        .css-1d391kg {
            padding-top: 1rem;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    init_session_state()

    # Sidebar for business context
    with st.sidebar:
        st.header("Business Context")

        countries = [
            "India", "United States", "United Kingdom", "Singapore",
            "Spain", "Philippines", "Russia", "Other"
        ]
        selected_country = st.selectbox(
            "Select Country",
            countries,
            index=countries.index(
                st.session_state.selected_country) if st.session_state.selected_country in countries else 0
        )

        business_types = [
            "LLC", "Corporation", "Sole Proprietorship",
            "Partnership", "Other"
        ]
        selected_business_type = st.selectbox(
            "Business Type",
            business_types,
            index=business_types.index(
                st.session_state.business_type) if st.session_state.business_type in business_types else 0
        )

        if st.button("🗑️ Clear Conversation", type="primary"):
            st.session_state.messages = []
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.rerun()

        st.divider()
        st.caption("© 2024 Business Assistant")

    # Main chat interface
    st.title("🌐 Business Setup Assistant")

    # Welcome message with enhanced formatting
    if not st.session_state.messages:
        st.info("""
        👋 Welcome! I'm here to help you establish your business.

        Select your target country and business type in the sidebar, then ask specific questions about:
        * 📝 Registration processes
        * ⚖️ Legal requirements
        * 💰 Tax considerations
        * 🏢 Licensing needs
        * 💵 Cost estimates
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
            with st.spinner("Thinking... 🔍"):
                response = answer_question(
                    question,
                    country=selected_country,
                    business_type=selected_business_type
                )
                final_response = stream_response(response, message_placeholder)

        # Save assistant response
        st.session_state.messages.append({
            "role": "assistant",
            "content": final_response,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })

if __name__ == "__main__":
    main()