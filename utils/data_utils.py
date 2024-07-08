from openai import OpenAI
import json
import os
import anthropic
from docx import Document

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# Function to generate coding scheme using OpenAI API
def generate_coding_schema(reviews_text, num_codes, question_text, temperature, language):
    prompt = f"""As an expert data analyst, your task is to create a comprehensive coding schema for analyzing open-ended survey responses. The survey question was:

"{question_text}"

Based on the following sample of responses, develop a coding schema with {num_codes} distinct codes, including a mandatory "Sonstige" (Other) category. Your schema should capture the main themes and topics present in the responses.

Sample responses:
{reviews_text}

Instructions:
1. Analyze the responses carefully to identify recurring themes and topics.
2. Create {num_codes - 1} unique codes for specific themes, starting with the most frequently mentioned topic.
3. Always include "Sonstige" (Other) as the last code to capture any responses that don't fit into the specific categories.
4. Each code should be concise yet descriptive, capturing a distinct aspect of the responses.
5. Assign a numerical ID to each code, starting from 1, with "Sonstige" always being the last ID.
6. Present your coding schema in {language}.

Output your schema in the following JSON format:
{{
    "topics": [
        {{"id": 1, "code": "Brief description of the most common theme"}},
        {{"id": 2, "code": "Brief description of the second most common theme"}},
        ...
        {{"id": {num_codes - 1}, "code": "Brief description of the least common specific theme"}},
        {{"id": {num_codes}, "code": "Sonstige"}}
    ]
}}

Ensure that your specific codes collectively cover the major themes in the responses, with "Sonstige" capturing any outliers or less common themes."""


    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    
    return response.choices[0].message.content

def classify_review(review, topics):
    topics_str = ", ".join([f'{topic["id"]}: {topic["topic"]}' for topic in topics])
    prompt = f"""Based on the following topics: {topics_str}, classify the review below:
    
    Review: {review}
    
    Respond with the topic IDs that are relevant to this review in JSON format. The JSON format should look like this: {{"relevant_topics": [{{"id": 1}}, {{"id": 2}}]}} if topics with id 1 and 2 are relevant."""
    
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )
    return json.loads(response.choices[0].message.content)



def transcribe_audio_file(audio_file_path):
    with open(audio_file_path, 'rb') as audio_file:
        transcription = client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
        )
    return transcription.text 

def analyze_with_gpt(transcription, prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": "You are a highly skilled AI trained in language comprehension and summarization. Please follow the user's prompt to analyze the transcription."
            },
            {
                "role": "user",
                "content": f"{prompt}\n\nTranscript:\n{transcription}"
            }
        ]
    )
    return response.choices[0].message.content 

def analyze_with_claude(transcription, prompt):
    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}\n\nTranskript:\n{transcription}"
                    }
                ]
            }
        ]
    )
    return response.content[0].text

def analyze_transcription(transcription, model, prompt):
    if model == "GPT-4":
        return analyze_with_gpt(transcription, prompt)
    elif model == "Claude":
        return analyze_with_claude(transcription, prompt)

def save_analysis_to_docx(analysis, filename):
    doc = Document()
    doc.add_paragraph(analysis)
    doc.save(filename)