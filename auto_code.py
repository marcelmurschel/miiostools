import streamlit as st
import pandas as pd
import json
import time
import io
import matplotlib.pyplot as plt
from utils.data_utils import generate_coding_schema, classify_review

def auto_code_tool_page():
    st.image("img/autocode.png")
    st.title("🤖 autoCODE beta")

    st.write("""
    AutoCode streamlines the process of coding open-ended responses and text data, 
    offering a seamless integration of AI and human expertise. With AutoCode, users can 
    effortlessly convert unstructured data into actionable insights.
    """)

    if 'custom_var_name' not in st.session_state:
        st.session_state.custom_var_name = "Input a variable name"

    uploaded_file = st.file_uploader("Upload a CSV or XLSX file", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)

        st.write("First 5 rows of the uploaded DataFrame:")
        st.write(df.head())

        column_name = st.selectbox("Choose column for coding schema", options=df.columns)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            sample_size = st.number_input("Select sample size", min_value=1, max_value=len(df), value=20, step=1)
        with col2:
            num_codes = st.number_input("Select number of codes", min_value=1, max_value=20, value=7, step=1)
        with col3:
            temperature = st.slider("Select temperature", min_value=0.0, max_value=1.0, value=0.7, step=0.1)
        with col4:
            language = st.selectbox("Select language", options=["German", "French", "English"])

        question_text = st.text_input("Input the question from the questionnaire")

        sample_reviews = df[column_name].dropna().sample(n=sample_size).to_list()  # Filter out NaN values
        reviews_text = "\n\n".join([str(review) for review in sample_reviews])

        if st.button("Generate Coding Schema"):
            with st.spinner('Generating coding schema...'):
                schema_response = generate_coding_schema(reviews_text, num_codes, question_text, temperature, language)
            
            schema = json.loads(schema_response)
            schema_df = pd.DataFrame(schema['topics'])
            schema_df.columns = ['id', 'topic']
            st.session_state.schema_df = schema_df

    if 'schema_df' in st.session_state and not st.session_state.schema_df.empty:
        edited_df = st.data_editor(st.session_state.schema_df, num_rows="dynamic", use_container_width=True, hide_index=True)

        if st.button("Save Changes"):
            st.session_state.schema_df = edited_df
            st.write("Saved Edited Coding Schema:")
            st.write(st.session_state.schema_df)

    if uploaded_file is not None and 'schema_df' in st.session_state:
        if st.button("Classify Reviews"):
            with st.spinner('Classifying reviews...'):
                topics = st.session_state.schema_df.to_dict('records')
                results = []
                progress_bar = st.progress(0)
                df_filtered = df[column_name].dropna()  # Filter out NaN values
                total_reviews = len(df_filtered)
                start_time = time.time()
                time_placeholder = st.empty()

                for idx, review in enumerate(df_filtered):
                    classification = classify_review(str(review), topics)
                    result = {topic['id']: 0 for topic in topics}
                    for relevant_topic in classification['relevant_topics']:
                        result[relevant_topic['id']] = 1
                    result['Review'] = review
                    results.append(result)

                    progress_bar.progress((idx + 1) / total_reviews)

                    elapsed_time = time.time() - start_time
                    avg_time_per_review = elapsed_time / (idx + 1)
                    remaining_time = avg_time_per_review * (total_reviews - idx - 1)
                    time_placeholder.text(f"Estimated remaining time: {int(remaining_time // 60)} minutes and {int(remaining_time % 60)} seconds")

                results_df = pd.DataFrame(results)
                st.write(results_df)
                
                # Calculate the percentage share
                topic_counts = results_df.drop(columns=['Review']).sum()
                topic_percentages = (topic_counts / len(results_df)) * 100
                topic_percentages = topic_percentages.sort_values(ascending=True)

                # Map topic IDs to topic names
                topic_id_to_name = {row['id']: row['topic'] for row in topics}
                topic_labels = [topic_id_to_name[topic_id] for topic_id in topic_percentages.index]

                # Display the horizontal bar chart
                st.write("Percentage Share of Classified Topics:")
                fig, ax = plt.subplots()
                topic_percentages.plot(kind='barh', ax=ax)
                ax.set_xlabel("Percentage (%)")
                ax.set_ylabel("Topics")
                ax.set_title("Percentage Share of Classified Topics")
                
                # Adding text labels to the side
                ax.set_yticklabels(topic_labels)
                for i in ax.patches:
                    ax.text(i.get_width() + 0.5, i.get_y() + 0.5, f'{i.get_width():.2f}%', ha='center', va='center')

                st.pyplot(fig)

    custom_var_name = st.text_input("Enter the base name for the columns", st.session_state.custom_var_name)
    st.session_state.custom_var_name = custom_var_name

    if 'custom_var_name' in st.session_state and 'results_df' in locals():
        custom_var_name = st.session_state.custom_var_name
        topic_columns = [col for col in results_df.columns if col != 'Review']
        new_column_names = {col: f"{custom_var_name}r{idx+1}" for idx, col in enumerate(topic_columns)}
        results_df.rename(columns=new_column_names, inplace=True)

        st.write(results_df)

        csv = results_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name='classified_reviews.csv',
            mime='text/csv',
        )

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            results_df.to_excel(writer, index=False, sheet_name='Sheet1')
        excel_data = output.getvalue()
        st.download_button(
            label="Download Excel",
            data=excel_data,
            file_name='classified_reviews.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )