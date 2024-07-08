import streamlit as st


def base_page():
    st.image("img/miios.jpg", use_column_width=True)
  
    st.title("ℹ️ Info")

    st.write("""
    Welcome to the MiiOS Toolbox. Here you will find a suite of tools designed to enhance efficiency and productivity in your day-to-day.
    """)

    st.subheader("Available Tools:")

    st.markdown("""
    📝 **SurveyBuilder:**
    Upload text documents (e.g., from Word) and receive an XML file ready for Forsta Surveys, streamlining your survey programming process.

    ✨ **betterDATA:**
    Enhance data quality by identifying and filtering out speeders, straightliners, and gibberish responses, ensuring more reliable survey results.

    🏷️ **autoCODE**
    Optimize the coding of open-ended responses and textual data through a blend of AI and human intelligence. Specify the column for analysis and obtain a refined coding schema for editing and finalization.

    ☢️ **Bad Ids:**
    Compares original datasets with cleaned datasets to identify and filter out poor quality responses, providing a clear distinction between good and bad data for further analysis.
                
    🎙️ **Whisper:**
    Leverage OpenAI Whisper to transcribe audio files accurately. Additionally, interrogate transcripts using OpenAI or Claude for deeper insights.

    🤖 **Interview Bot:**
    Automate qualitative interviews with an advanced AI-driven tool, saving time and resources in conducting market research interviews.

    ✍️ **goethe:**
    Generate professional LinkedIn, Instagram, or blog posts tailored to specific use cases, enabling efficient and effective content creation.

    📚 **Knowledge Manager (planned):**
    A comprehensive repository of all studies conducted by MiiOS, facilitating easy retrieval of information with detailed source references for employees.

    👤 **PersonaBot (planned):**
    Interact with personas derived from segmentation analysis of survey data, providing nuanced insights and engagement.

    🚀 **Onboarding (planned):**
    Support new employees at MiiOS with essential company information, aiding their quick integration and operational readiness.
    """)

