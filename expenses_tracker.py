import os
import streamlit as st
import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from openai import OpenAI
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Initialize OpenAI API client
OpenAI.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

IMGUR_CLIENT_ID = os.getenv("IMGUR_CLIENT_ID")  # Replace with your Imgur client ID

def upload_image_to_imgur(image_path):
    headers = {"Authorization": f"Client-ID {IMGUR_CLIENT_ID}"}
    with open(image_path, "rb") as image_file:
        data = {"image": image_file.read()}
    response = requests.post("https://api.imgur.com/3/image", headers=headers, files=data)
    if response.status_code == 200:
        return response.json()["data"]["link"]
    else:
        st.error("Failed to upload image to Imgur")
        return None

def process_receipt(image_url, heutiges_datum):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"""Du siehst hier einen Kassenzettel. Bitte gebe mir einen output im json format 
                    wo du das jeweilige Produkt, der Price, die Menge (wenn vorhanden), die Produktkategorie (z.B. "Obst & Gemüse"), das Kaufdatum, und der Supermarkt zu finden sind. 

                    Das Json soll so aussehen: 
                    {{
                      "store": store,
                      "date": "date",
                      "items": {{
                        "product_name": "name",
                        "quantity": "menge als zahl",
                        "price": "preis als zahl",
                        "category": "produktkategorie"
                      }}
                    }}    

                    Das Datum soll immer in diesem Format dargestellt werden: "%d.%m.%Y". Wenn du kein Datum identifizieren kannst, dann schreibe bitte das heutige Datum {heutiges_datum} hinein.
                    
                    Bei dem store schreibe bitte nur den Namen hin - nichts längeres. 

                    Diese produktkategorien gibt es: 
                        "Obst und Gemüse",
                        "Brot und Backwaren",
                        "Milchprodukte",
                        "Fleisch und Wurstwaren",
                        "Fisch und Meeresfrüchte",
                        "Tiefkühlprodukte",
                        "Konserven und Fertiggerichte",
                        "Teigwaren und Reis",
                        "Getränke",
                        "Süßwaren und Snacks",
                        "Kaffee und Tee",
                        "Babynahrung und Babyprodukte",
                        "Haushaltswaren und Reinigungsmittel",
                        "Körperpflege und Kosmetik",
                        "Tiernahrung und -zubehör",
                        "Backzutaten und Gewürze",
                        "Bio- und Reformprodukte",
                        "Non-Food-Artikel"
                    """},
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url},
                    },
                ],
            }
        ],
        max_tokens=4096,
        temperature=0,
        response_format={"type": "json_object"},
    )

    # Extract the response content
    json_string = json.loads(response.choices[0].message.content)
    print(json_string)
    data = json_string
    return data

def plot_expenses_chart(df):
    # Convert the date column to datetime
    df['date'] = pd.to_datetime(df['date'], format="%d.%m.%Y")

    # Aggregate expenses by month
    df['month'] = df['date'].dt.to_period('M')
    monthly_expenses = df.groupby('month')['price'].sum().reset_index()
    
    # Plot the line chart
    fig, ax = plt.subplots()
    ax.plot(monthly_expenses['month'].astype(str), monthly_expenses['price'], marker='o')
    ax.set_xlabel('Month')
    ax.set_ylabel('Total Expenses')
    ax.set_title('Monthly Expenses')
    plt.xticks(rotation=45)
    
    st.pyplot(fig)

def plot_category_expenses(df):
    category_expenses = df.groupby('category')['price'].sum().reset_index()
    category_expenses = category_expenses.sort_values(by='price', ascending=True)  # Sort by total expenses descending
    
    # Plot a horizontal bar chart
    fig, ax = plt.subplots()
    ax.barh(category_expenses['category'], category_expenses['price'])
    ax.set_xlabel('Total Expenses')
    ax.set_ylabel('Category')
    ax.set_title('Expense Distribution by Category')
    
    st.pyplot(fig)

def expenses_tracker_page():
    st.image("img/et_banner.jpg", use_column_width=True)
    st.title("💸 Expenses Tracker")

    # Load existing data if available
    csv_file_path = "receipt_data.csv"
    if os.path.exists(csv_file_path):
        df = pd.read_csv(csv_file_path)
    else:
        df = None

    uploaded_file = st.file_uploader("Choose a receipt image...", type=["jpg", "png"], key="unique_uploader")

    if uploaded_file is not None:
        # Display the uploaded image
        st.image(uploaded_file, caption='Uploaded Receipt', use_column_width=True)

        # Save the uploaded file temporarily
        temp_file_path = "temp_receipt." + uploaded_file.name.split(".")[-1]
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Upload the image to Imgur to get the URL
        image_url = upload_image_to_imgur(temp_file_path)

        if image_url:
            heutiges_datum = datetime.today().strftime('%d.%m.%Y')
            # Process the image URL
            data = process_receipt(image_url, heutiges_datum)
            print(data)
            # Convert the data to a DataFrame
            df_new = pd.DataFrame(data['items'])
            df_new['store'] = data['store']
            df_new['date'] = data['date']
            
            # Display the new DataFrame
            st.subheader('Newly Uploaded Receipt Data')
            st.dataframe(df_new)  # Display the DataFrame with a scrollbar
            
            # Append the new data to the existing DataFrame
            if df is not None:
                df = pd.concat([df, df_new], ignore_index=True)
            else:
                df = df_new

            # Save the combined DataFrame to CSV
            df.to_csv(csv_file_path, index=False)

            # Provide download link for the CSV
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download data as CSV",
                data=csv,
                file_name='receipt_data.csv',
                mime='text/csv',
            )

    # Plot charts at the bottom of the page
    if df is not None:
        st.header('Expense Analysis')
        st.subheader('Monthly Expenses')
        plot_expenses_chart(df)

        st.subheader('Expense Distribution by Category')
        plot_category_expenses(df)
