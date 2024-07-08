import streamlit as st
import tempfile
import os
from utils.data_utils import transcribe_audio_file, analyze_transcription, save_analysis_to_docx
from docx import Document

def whisper_page():
    st.image("img/whisper.jpg")
    st.title("🎙️ Whisper")

    # Introduction text
    st.write("""Verwandeln Sie Audiodateien mühelos in Text! Laden Sie Ihre Audiodateien (bis 25 MB) hoch und erhalten Sie präzise 
             Transkripte. Ideal für die Analyse von Interviews, Fokusgruppen oder anderen gesprochenen Inhalten. Hier können Sie das Audiofile ggf. komprimieren.
             
             https://www.onlineconverter.com/compress-mp3""")

    # Step 1: Transcription
    st.header("📝 Transcribe Audio")
    uploaded_file = st.file_uploader("Upload an MP3 file", type="mp3")

    if st.button("📝 Transcribe"):
        if uploaded_file is not None:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_file:
                temp_file.write(uploaded_file.read())
                temp_file_path = temp_file.name

            try:
                with st.spinner("Transcribing..."):
                    transcription = transcribe_audio_file(temp_file_path)
                    st.subheader("Transcript")
                    st.write(transcription)

                    docx_file_path = os.path.join(tempfile.gettempdir(), "transcription.docx")
                    save_analysis_to_docx(transcription, docx_file_path)

                    with open(docx_file_path, "rb") as f:
                        st.download_button("Download Transcription as DOCX", f, file_name="transcription.docx")
            except Exception as e:
                st.error(f"An error occurred: {e}")
            finally:
                os.remove(temp_file_path)

    # Step 2: Analysis (optional)
    st.header("🔍Interrogate Transcript")
    uploaded_transcription_file = st.file_uploader("Upload a Transcription DOCX file", type="docx", key="transcription_file")
    
    # Increased height of the text area for the prompt
    prompt = st.text_area("Enter your prompt for analyzing the transcript", height=100)
    model = st.selectbox("Choose a model for analysis", ["GPT-4", "Claude"])

    if st.button("🔍 Interrogate"):
        if uploaded_transcription_file is not None and prompt:
            try:
                with st.spinner("Analyzing..."):
                    doc = Document(uploaded_transcription_file)
                    transcription_text = "\n".join([para.text for para in doc.paragraphs])

                    analysis = analyze_transcription(transcription_text, model, prompt)
                    st.subheader("Analysis")
                    st.write(analysis)

                    docx_analysis_file_path = os.path.join(tempfile.gettempdir(), "analysis.docx")
                    save_analysis_to_docx(analysis, docx_analysis_file_path)

                    with open(docx_analysis_file_path, "rb") as f:
                        st.download_button("Download Analysis as DOCX", f, file_name="analysis.docx")
            except Exception as e:
                st.error(f"An error occurred: {e}")