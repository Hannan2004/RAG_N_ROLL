# 🌐 International Business Setup Assistant

The International Business Setup Assistant is an AI-driven Streamlit application designed to assist users in establishing businesses internationally. By leveraging Snowflake's Snowpark and Cortex integration alongside a Mistral Large Language Model, this app delivers accurate, actionable, and context-aware business guidance.

## 🚀 Features

### 🌟 Interactive Chat Interface
- Intuitive, real-time chat with user and assistant messages displayed sequentially.
- Feedback buttons (👍 and 👎) for each assistant response to improve system performance.

### 🌟 Personalized Context
- **Target Country:** Choose from a predefined list (e.g., India, USA, UK, etc.).
- **Business Type:** Options like LLC, Corporation, Sole Proprietorship, and more.

### 🌟 Data-Driven Insights
- Utilizes Snowflake Cortex to search and retrieve relevant business information from a secure database.
- Processes data chunks for precise context matching.

### 🌟 Enhanced Response Generation
- Combines conversation history, user preferences, and retrieved data to generate insightful and tailored answers.

### 🌟 Feedback and Conversation Management
- Clear conversation history at the click of a button.
- Session management ensures secure and personalized interactions.

## 🛠️ Technologies Used

### Streamlit
- Simplifies the creation of an interactive, responsive web application.
- Integrates user inputs, chat interfaces, and visual elements seamlessly.

### Snowflake
- **Snowpark:** Powers the backend with a scalable, secure environment for querying and processing data.
- **Session Management:** Creates and manages secure connections.
- **Data Retrieval:** Fetches relevant chunks of business information for context.
- **Cortex:** Enables advanced search and retrieval capabilities.
  - Provides chunked data from a specialized database for accurate responses.

### Mistral Language Model
- Processes user queries and context to generate intelligent, human-like responses.
- Adapts to changing contexts, providing both generic and specific guidance.

## 🔧 How It Works

### User Interaction
- Users input their questions via a chat interface.
- Contextual options like country and business type are selected via the sidebar.

### Data Retrieval with Snowflake
- Cortex fetches relevant business-related data using the `get_similar_chunks_search_service` function.
- Snowpark manages sessions and queries efficiently.

### Intelligent Response Generation
- The Mistral model processes:
  - User input.
  - Chat history.
  - Contextual data fetched from Snowflake.
- Combines all elements into a tailored, insightful response.

### Feedback Mechanism
- Users rate responses to refine future answers.

## 📷 Screenshots

### Home Page and Sidebar
The app welcomes users with an introduction and a sidebar for entering business context.

### Chat Interface
Users interact with the assistant, receive responses, and provide feedback.

### Response Generation
The assistant processes questions and generates context-aware, step-by-step guidance.

## 🌐 How Snowflake and Mistral Enhance the Application

### Snowflake's Role
- **Centralized Data Storage:** Stores comprehensive information on global business requirements.
- **Efficient Querying:** Snowpark enables seamless data access and processing.
- **Advanced Search:** Cortex ensures precise and relevant data retrieval for context-building.

### Mistral's Role
- **Language Understanding:** Converts user queries into actionable insights.
- **Contextual Reasoning:** Uses retrieved data to create human-like, practical responses.
- **Scalable AI:** Handles diverse queries across multiple domains effectively.

## 🖥️ Installation & Setup

### **Set Up Environment**

#### Install dependencies:
```bash
 pip install streamlit snowflake-snowpark-python pandas
```
#### Configure secrets in Streamlit:
- account = "your_account".
- user = "your_user".
- password = "your_password".
- role = "your_role".
- warehouse = "your_warehouse".
- database = "your_database"
- schema = "your_schema"

# Run the App
```bash
 streamlit run streamlit_app.py
```
## 🎯 Future Enhancements

- **Expand Country Support:** Add support for more countries, enabling a truly global experience.
- **Advanced Business Recommendations:** Integrate additional AI models to provide personalized, region-specific insights.
- **Enhanced Visualizations:** Present key insights like tax rates and registration timelines using data-driven charts.
- **Language Support:** Introduce multilingual capabilities for non-English-speaking users.
- **Real-Time Collaboration:** Enable team collaboration while planning and setting up businesses.
- **User Analytics:** Use analytics to improve response accuracy based on user queries and feedback.




