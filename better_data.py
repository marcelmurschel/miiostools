import streamlit as st
import pandas as pd
import re
from io import BytesIO
import matplotlib.pyplot as plt
import numpy as np

def identify_speeders(df, time_column, time_threshold):
    speeders = df[time_column] <= time_threshold
    return speeders.astype(int)

def identify_inconsistencies(df, age_column, birth_year_column, missing_values):
    current_year = pd.Timestamp.now().year
    inconsistencies = df.apply(
        lambda row: row[age_column] != (current_year - row[birth_year_column]) if row[age_column] not in missing_values and row[birth_year_column] not in missing_values else 0,
        axis=1
    )
    return inconsistencies.astype(int)

def identify_straightliners(df, questions, missing_values):
    def is_straightliner(row):
        unique_values = row[~row.isin(missing_values)].nunique()
        return unique_values == 1
    straightliners = df[questions].apply(is_straightliner, axis=1)
    return straightliners.astype(int)

def identify_gibberish(df, open_answer_column, missing_values):
    gibberish_pattern = re.compile(r'^[a-zA-Z]{8,}$')
    gibberish = df[open_answer_column].apply(lambda x: bool(gibberish_pattern.match(str(x))) if x not in missing_values else 0)
    return gibberish.astype(int)

def identify_gibberish_v2(df, open_answer_column, missing_values):
    return identify_gibberish(df, open_answer_column, missing_values)

def identify_straightliners_v2(df, questions, missing_values):
    return identify_straightliners(df, questions, missing_values)

def identify_duplicates(df, columns, missing_values):
    def is_duplicate(row):
        for col in columns:
            if row[col] in missing_values:
                return 0
        return 1
    duplicates = df.duplicated(subset=columns, keep=False) & df.apply(is_duplicate, axis=1).astype(bool)
    return duplicates.astype(int)

def better_data_page():
    st.image("img/betterdata.jpg")
    st.title('🧼betterDATA')
    st.write("""
    betterDATA betters your data by filtering out speeders, straightliners, and gibberish responses. 
             Ensure reliable, high-quality survey results and elevate your research outcomes effortlessly.
    """)

    uploaded_file = st.file_uploader("Choose an Excel or CSV file", type=["xlsx", "csv"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file)
        else:
            df = pd.read_csv(uploaded_file)
        
        original_columns = df.columns.tolist()  # Store the original order of columns
        st.write("Data Preview:", df.head())

        st.header('Quality Check Options')

        id_column = st.selectbox('Select ID column', df.columns)
        selected_columns = {id_column}

        check_speeders = st.checkbox('Check Speeders')
        if check_speeders:
            time_column = st.selectbox('Select time column', df.columns)
            selected_columns.add(time_column)
            if time_column:
                median_time = df[time_column].median()
                proposed_threshold = median_time / 2
                time_threshold = st.number_input('Speeder Threshold (in seconds)', value=proposed_threshold)
                speeders_weight = st.slider('Speeder Weight', min_value=0.0, max_value=3.0, value=1.0)
                num_speeders = identify_speeders(df, time_column, time_threshold).sum()
                st.write(f"Number of speeders: {num_speeders}")

        check_inconsistencies = st.checkbox('Check Inconsistencies')
        if check_inconsistencies:
            age_column = st.selectbox('Select age column', df.columns)
            birth_year_column = st.selectbox('Select birth year column', df.columns)
            selected_columns.add(age_column)
            selected_columns.add(birth_year_column)
            inconsistencies_weight = st.slider('Inconsistencies Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_inconsistencies = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_inconsistencies')
            missing_values_inconsistencies = [eval(value.strip()) for value in missing_values_inconsistencies.split(',')]
            num_inconsistencies = identify_inconsistencies(df, age_column, birth_year_column, missing_values_inconsistencies).sum()
            st.write(f"Number of inconsistencies: {num_inconsistencies}")

        check_straightliners = st.checkbox('Check Straightliners')
        if check_straightliners:
            question_columns = st.multiselect('Select columns for straightliners', df.columns)
            selected_columns.update(question_columns)
            straightliners_weight = st.slider('Straightliners Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_straightliners = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_straightliners')
            missing_values_straightliners = [eval(value.strip()) for value in missing_values_straightliners.split(',')]
            if question_columns:
                num_straightliners = identify_straightliners(df, question_columns, missing_values_straightliners).sum()
                st.write(f"Number of straightliners: {num_straightliners}")

        check_gibberish = st.checkbox('Check Gibberish')
        if check_gibberish:
            open_answer_column = st.selectbox('Select open answer column', df.columns)
            selected_columns.add(open_answer_column)
            gibberish_weight = st.slider('Gibberish Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_gibberish = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_gibberish')
            missing_values_gibberish = [eval(value.strip()) for value in missing_values_gibberish.split(',')]
            num_gibberish = identify_gibberish(df, open_answer_column, missing_values_gibberish).sum()
            st.write(f"Number of gibberish answers: {num_gibberish}")

        check_straightliners_v2 = st.checkbox('Check Straightliners v2')
        if check_straightliners_v2:
            question_columns_v2 = st.multiselect('Select columns for straightliners v2', df.columns)
            selected_columns.update(question_columns_v2)
            straightliners_v2_weight = st.slider('Straightliners v2 Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_straightliners_v2 = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_straightliners_v2')
            missing_values_straightliners_v2 = [eval(value.strip()) for value in missing_values_straightliners_v2.split(',')]
            if question_columns_v2:
                num_straightliners_v2 = identify_straightliners_v2(df, question_columns_v2, missing_values_straightliners_v2).sum()
                st.write(f"Number of straightliners v2: {num_straightliners_v2}")

        check_gibberish_v2 = st.checkbox('Check Gibberish v2')
        if check_gibberish_v2:
            open_answer_column_v2 = st.selectbox('Select open answer column v2', df.columns)
            selected_columns.add(open_answer_column_v2)
            gibberish_v2_weight = st.slider('Gibberish v2 Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_gibberish_v2 = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_gibberish_v2')
            missing_values_gibberish_v2 = [eval(value.strip()) for value in missing_values_gibberish_v2.split(',')]
            num_gibberish_v2 = identify_gibberish_v2(df, open_answer_column_v2, missing_values_gibberish_v2).sum()
            st.write(f"Number of gibberish answers v2: {num_gibberish_v2}")

        check_duplicates = st.checkbox('Check Duplicates')
        if check_duplicates:
            duplicate_columns = st.multiselect('Select columns to check for duplicates', df.columns)
            selected_columns.update(duplicate_columns)
            duplicates_weight = st.slider('Duplicates Weight', min_value=0.0, max_value=3.0, value=1.0)
            missing_values_duplicates = st.text_input('Enter missing values separated by commas', '-77,-99,np.nan', key='missing_values_duplicates')
            missing_values_duplicates = [eval(value.strip()) for value in missing_values_duplicates.split(',')]
            if duplicate_columns:
                num_duplicates = identify_duplicates(df, duplicate_columns, missing_values_duplicates).sum()
                st.write(f"Number of duplicates: {num_duplicates}")

        if st.button('Run Check'):
            total_respondents = len(df)
            score = pd.Series(0, index=df.index)
            
            # Initialize columns for all checks
            df['Speeder'] = 0
            df['Inconsistency'] = 0
            df['Straightliner'] = 0
            df['Gibberish'] = 0
            df['Straightliner_v2'] = 0
            df['Gibberish_v2'] = 0
            df['Duplicate'] = 0

            if check_speeders:
                df['Speeder'] = identify_speeders(df, time_column, time_threshold)
                score += df['Speeder'] * speeders_weight

            if check_inconsistencies:
                df['Inconsistency'] = identify_inconsistencies(df, age_column, birth_year_column, missing_values_inconsistencies)
                score += df['Inconsistency'] * inconsistencies_weight

            if check_straightliners:
                df['Straightliner'] = identify_straightliners(df, question_columns, missing_values_straightliners)
                score += df['Straightliner'] * straightliners_weight

            if check_gibberish:
                df['Gibberish'] = identify_gibberish(df, open_answer_column, missing_values_gibberish)
                score += df['Gibberish'] * gibberish_weight

            if check_straightliners_v2:
                df['Straightliner_v2'] = identify_straightliners_v2(df, question_columns_v2, missing_values_straightliners_v2)
                score += df['Straightliner_v2'] * straightliners_v2_weight

            if check_gibberish_v2:
                df['Gibberish_v2'] = identify_gibberish_v2(df, open_answer_column_v2, missing_values_gibberish_v2)
                score += df['Gibberish_v2'] * gibberish_v2_weight

            if check_duplicates:
                df['Duplicate'] = identify_duplicates(df, duplicate_columns, missing_values_duplicates)
                score += df['Duplicate'] * duplicates_weight

            df['Score'] = score

            num_respondents_with_mistakes = (score > 0).sum()
            st.write(f"Total Respondents: {total_respondents}")
            st.write(f"Respondents with at least one mistake: {num_respondents_with_mistakes}")

            st.session_state['df'] = df
            st.session_state['selected_columns'] = list(selected_columns)
            st.session_state['id_column'] = id_column
            st.session_state['original_columns'] = original_columns
            st.session_state['analysis_done'] = True

    if 'analysis_done' in st.session_state and st.session_state['analysis_done']:
        df = st.session_state['df']
        selected_columns = st.session_state['selected_columns']
        id_column = st.session_state['id_column']
        original_columns = st.session_state['original_columns']

        col1, col2 = st.columns(2)

        with col1:
            st.subheader('Score Distribution')
            fig, ax = plt.subplots()
            ax.hist(df['Score'], bins=20, edgecolor='k')
            ax.set_xlabel('Score')
            ax.set_ylabel('Frequency')
            st.pyplot(fig)

        with col2:
            st.subheader('Score Box Plot')
            fig, ax = plt.subplots()
            ax.boxplot(df['Score'], vert=False)
            ax.set_xlabel('Score')
            st.pyplot(fig)

        threshold = st.slider('Score Threshold for Flagging Cheaters', min_value=0.0, max_value=float(df['Score'].max()), value=1.0)

        num_affected = (df['Score'] >= threshold).sum()
        st.write(f"Number of respondents affected by the threshold: {num_affected}")
        st.write(f"Number of respondents remaining in the dataset: {len(df) - num_affected}")

        if st.button('Run'):
            bad_ids = df[df['Score'] >= threshold][id_column].tolist()
            st.write("Bad IDs:", bad_ids)

            if bad_ids:
                quality_check_columns = ['Speeder', 'Inconsistency', 'Straightliner', 'Gibberish', 'Straightliner_v2', 'Gibberish_v2', 'Duplicate', 'Score']
                columns_order = original_columns + [col for col in quality_check_columns if col not in original_columns]
                bad_ids_df = df[df[id_column].isin(bad_ids)][columns_order]

                # Save to a BytesIO buffer
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    bad_ids_df.to_excel(writer, index=False)
                output.seek(0)

                st.download_button('Download Bad IDs', data=output, file_name='bad_ids.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
