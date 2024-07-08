import streamlit as st
import os
from openai import OpenAI

# Fetch the API key from environment variables
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_linkedin_post(insight, hashtags, use_emojis, temperature, considerations, style, language, occasion, post_length, link_url, bold_words):
    emoji_text = " Use appropriate emojis." if use_emojis else ""
    hashtags_text = f"Include these hashtags: {', '.join(hashtags)}." if hashtags else "Create appropriate hashtags."
    
    # Make words bold
    for word in bold_words:
        insight = insight.replace(word, f"**{word}**")

    if link_url:
        insight += f" [Read more]({link_url})"

    prompt = f"""Write a professional and engaging LinkedIn post based on the following insight: '{insight}'.
    {hashtags_text}{emoji_text}
    Occasion: {occasion}
    Style: {style}
    Considerations: {considerations}
    Length: {post_length}
    Please write in {language}.
    """
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert in creating LinkedIn posts."},
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )
    
    return response.choices[0].message.content


def goethe_page():
    st.image("img/goethe.png")
    st.title("✍️ goethe")

    st.write("""Goethe empowers professionals to craft tailored LinkedIn posts with precision. 
    Define your post's purpose, choose your style, language, and customization options, 
    then input your content to generate impactful posts that resonate with your audience.""")

    col1, col2, col3 = st.columns(3)
    with col1:
        occasion = st.selectbox("Select the occasion", options=["Insight", "Event"])
    with col2:
        style = st.selectbox("Select a style", options=["The Economist", "Die Zeit", "McKinsey / BCG"])
    with col3:
        language = st.selectbox("Select language", options=["German", "French", "English"])

    col4, col5, col6 = st.columns(3)
    with col4:
        use_emojis = st.checkbox("Use emojis")
    with col5:
        temperature = st.slider("Select temperature", min_value=0.0, max_value=1.0, value=0.5, step=0.1)
    with col6:
        post_length = st.selectbox("Select post length", options=["Short", "Medium", "Long"])

    insight = st.text_area("Enter your insight here", "", height=2,)
    link_url = st.text_input("Enter a URL to include in the post (optional)")
    bold_words = st.text_input("Enter words to make bold, separated by commas").split(',')

    col7, col8 = st.columns([2, 1])
    with col7:
        hashtags = st.text_input("Enter hashtags separated by commas", "")
    with col8:
        auto_hashtags = st.checkbox("Let AI generate hashtags", value=False)
    considerations = st.text_area("Additional considerations", "")

    if st.button("Generate LinkedIn Post"):
        if insight:
            hashtags_list = [] if auto_hashtags else [tag.strip() for tag in hashtags.split(",")]
            bold_words_list = [word.strip() for word in bold_words if word.strip()]
            with st.spinner('Generating LinkedIn post...'):
                linkedin_post = generate_linkedin_post(insight, hashtags_list, use_emojis, temperature, considerations, style, language, occasion, post_length, link_url, bold_words_list)
                st.write("### Generated LinkedIn Post:")
                st.write(linkedin_post)
