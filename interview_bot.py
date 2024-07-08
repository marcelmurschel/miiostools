import os
import streamlit as st
import time
from openai import OpenAI

def interview_bot_page():
    # Set up OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Get assistant_id from environment variables
    assistant_id = os.getenv("ASSISTANT_ID")

    # Initialize session state variables
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "thread_id" not in st.session_state:
        st.session_state.thread_id = None

    # Always display the title at the top
    st.image("img/interviewerbot.jpg")
    st.title("🤖 Interview Bot")
    st.write("Willkommen bei Interview Bot! Wir freuen uns, dass Sie an diesem kleinen Interview teilnehmen möchten. Unser KI-gestützter Interviewer wird Ihnen einige Fragen stellen, um qualitative Daten zu sammeln. Ihre Antworten sind wertvoll für uns. Lassen Sie uns beginnen!")

    # Function to display messages
    def display_messages():
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Display existing messages
    display_messages()

    # Function to simulate typing effect
    def simulate_typing(placeholder, text):
        delay = 0.02  # Adjust this value to change typing speed
        for i in range(len(text)):
            placeholder.markdown(text[:i+1] + "▌")
            time.sleep(delay)
        placeholder.markdown(text)

    # Chat input
    if prompt := st.chat_input("Schreiben Sie hier Ihre Antwort hinein."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Create a thread if it doesn't exist
        if not st.session_state.thread_id:
            thread = client.beta.threads.create()
            st.session_state.thread_id = thread.id

        # Add the user's message to the thread
        client.beta.threads.messages.create(
            thread_id=st.session_state.thread_id,
            role="user",
            content=prompt
        )

        # Create a placeholder for the assistant's response
        assistant_placeholder = st.empty()

        with assistant_placeholder.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run the assistant
                run = client.beta.threads.runs.create(
                    thread_id=st.session_state.thread_id,
                    assistant_id=assistant_id
                )

                # Wait for the assistant to complete
                while run.status != "completed":
                    time.sleep(1)
                    run = client.beta.threads.runs.retrieve(
                        thread_id=st.session_state.thread_id,
                        run_id=run.id
                    )

                # Retrieve the assistant's messages
                messages = client.beta.threads.messages.list(
                    thread_id=st.session_state.thread_id
                )

                # Get the latest assistant message
                assistant_messages = [msg for msg in messages if msg.role == "assistant"]
                if assistant_messages:
                    latest_message = assistant_messages[0]
                    assistant_response = latest_message.content[0].text.value

                    # Add the assistant's response to the chat history
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})

                    # Display the assistant's response with typing effect
                    simulate_typing(st.empty(), assistant_response)

        # Clear the assistant placeholder to prevent redundant display
        assistant_placeholder.empty()

        # Rerun the app to update the display
        st.rerun()
