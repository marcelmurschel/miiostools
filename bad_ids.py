import streamlit as st
import pandas as pd
import io

def bad_ids_page():
    st.image("img/badids.jpg")
    st.title("☢️ Bad Ids")

    st.write("""
    Bad Ids identifies which survey responses were retained and which were discarded, providing panel providers with a clear report on the IDs of good and bad data used in the final analysis.
    """)

    original_file = st.file_uploader("Upload the original dataset (xlsx)", type="xlsx")
    cleaned_file = st.file_uploader("Upload the cleaned dataset (xlsx)", type="xlsx")

    if original_file is not None and cleaned_file is not None:
        original_df = pd.read_excel(original_file)
        cleaned_df = pd.read_excel(cleaned_file)

        st.write("First 5 rows of the original dataset:")
        st.write(original_df.head())

        st.write("First 5 rows of the cleaned dataset:")
        st.write(cleaned_df.head())

        respondent_id_var = st.selectbox("Select the respondent ID variable", options=original_df.columns)

        if st.button("Process"):
            with st.spinner("Processing IDs..."):
                good_ids = set(cleaned_df[respondent_id_var])
                all_ids = set(original_df[respondent_id_var])
                bad_ids = all_ids - good_ids

                good_ids_df = pd.DataFrame(good_ids, columns=[respondent_id_var])
                bad_ids_df = pd.DataFrame(bad_ids, columns=[respondent_id_var])

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    good_ids_df.to_excel(writer, index=False, sheet_name='Good IDs')
                    bad_ids_df.to_excel(writer, index=False, sheet_name='Bad IDs')
                
                excel_data = output.getvalue()

                st.download_button(
                    label="Download IDs Report",
                    data=excel_data,
                    file_name='ids_report.xlsx',
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                )