import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import numpy as np
from openai import OpenAI
import os

OpenAI.api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def scrape_rewe_lidl():
    supermarkets = [
        {"name": "Rewe", "url": "https://www.aktionspreis.de/prospekt/rewe-angebote"},
        {"name": "LIDL", "url": "https://www.aktionspreis.de/prospekt/LIDL-angebote"}
    ]
    data = []
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    for supermarket in supermarkets:
        response = requests.get(supermarket["url"], headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        angebote = soup.find_all('div', style="position:relative;")
        for angebot in angebote:
            title = angebot.find('a').get('title') if angebot.find('a') else 'N/A'
            price_tag = angebot.find('span', style="color:#383838; font-size:14px; float:right; padding-right: 0px;text-align:right")
            price = price_tag.get_text(strip=True) if price_tag else 'N/A'
            discount_tag = angebot.find('span', class_='percent_new')
            discount_text = discount_tag.get_text(strip=True) if discount_tag else 'N/A'
            discount = int(discount_text.replace('-', '').strip()) if discount_text != 'N/A' else 'N/A'
            data.append({
                "Supermarket": supermarket["name"],
                "Title": title,
                "Price": price,
                "Discount": discount
            })
    df = pd.DataFrame(data)
    df['Price'] = df['Price'].apply(clean_price)
    df['Discount'] = df['Discount'].apply(clean_discount)
    df = df.sort_values(by="Discount", ascending=False)
    df = df[["Supermarket", "Title", "Price", "Discount"]]
    return df[df['Supermarket'] == 'Rewe'], df[df['Supermarket'] == 'LIDL']

def clean_price(price):
    if isinstance(price, str):
        price = price.replace(' €', '').replace(',', '.')
        if 'keine Preisinfo' in price or 'ab' in price:
            return None
        return float(price)
    return price

def clean_discount(discount):
    if isinstance(discount, str):
        if discount == 'N/A':
            return None
        discount = discount.replace('-', '').strip()
        return float(discount)
    return discount

def scrape_kaufland():
    url = "https://filiale.kaufland.de/angebote/uebersicht.html?kloffer-category=0001_TopArticle"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    script_tags = soup.find_all('script')
    if len(script_tags) > 16:
        script_tag = script_tags[16]
        json_text = script_tag.string
        try:
            start_index = json_text.find('{', json_text.find(';'))
            end_index = json_text.rfind('}') + 1
            json_substring = json_text[start_index:end_index]
            digital_data = json.loads(json_substring)
            offers = digital_data['props']['offerData']['loyalty']['offers']
            df = pd.DataFrame(offers)
        except (json.JSONDecodeError, ValueError) as e:
            print("Failed to decode JSON:", e)
            return pd.DataFrame()
    else:
        print("Script tag containing JSON data not found.")
        return pd.DataFrame()
    food_related_df = df
    food_related_df.loc[:, 'Title'] = food_related_df['title'] + " " + food_related_df['subtitle']
    food_related_df = food_related_df[['Title', 'price', 'discount']]
    food_related_df.columns = ['Title', 'Price', 'Discount']
    food_related_df.loc[:, 'Supermarket'] = "Kaufland"
    food_related_df['Price'] = food_related_df['Price'].apply(lambda x: float(str(x).replace(',', '.')))
    food_related_df['Discount'] = food_related_df['Discount'].apply(lambda x: float(str(x).replace('%', '').replace('-', '').strip()))
    food_related_df = food_related_df.sort_values(by="Discount", ascending=False)
    return food_related_df[['Supermarket', 'Title', 'Price', 'Discount']]

def scrape_edeka():
    url = "https://www.edeka.de/api/offers?limit=999&marketId=6064497"
    headers = {
        'accept': '*/*',
        'accept-language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'cookie': 'TCPID=124601226536145772266; EDEKA_PRIVACY=0@057@1%2C3%2C2%2C8%2C4%2C5%2C6%2C7@91@1719138415012@; EDEKA_PRIVACY_CENTER=1%2C3%2C2%2C8%2C4%2C5%2C6%2C7; atuserid=%7B%22name%22%3A%22atuserid%22%2C%22val%22%3A%22e6e27dba-0f48-4124-8e3f-1ef3837f9e4e%22%2C%22options%22%3A%7B%22end%22%3A%222025-07-25T10%3A26%3A55.016Z%22%2C%22path%22%3A%22%2F%22%7D%7D; _fbp=fb.1.1719138415229.896154841638630358; _gcl_au=1.1.663899145.1719138415; _pin_unauth=dWlkPU1HUmlZemM1WXpjdFlqRmxNUzAwWldGa0xUbGlNREl0T1RrNU56azRPVGd6TnpKbQ',
        'priority': 'u=1, i',
        'referer': 'https://www.edeka.de/eh/s%C3%BCdwest/edeka-baisch-leonberger-stra%C3%9Fe-98/angebote.jsp',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Mobile Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    data = response.json()
    df = pd.json_normalize(data['offers'])
    superknueller_df = df[df['criteria'].apply(lambda x: any(criterion['name'] == 'Superknüller' for criterion in x) if pd.notnull(x) else False)]
    superknueller_df = superknueller_df[['title', 'price.value']]
    superknueller_df.columns = ['Title', 'Price']
    superknueller_df['Supermarket'] = 'Edeka'
    superknueller_df['Discount'] = np.nan
    superknueller_df['Price'] = superknueller_df['Price'].apply(lambda x: float(str(x).replace(',', '.')))
    superknueller_df = superknueller_df.sort_values(by="Price", ascending=True)
    return superknueller_df[['Supermarket', 'Title', 'Price', 'Discount']]

def scrape_prices():
    rewe_df, lidl_df = scrape_rewe_lidl()
    kaufland_df = scrape_kaufland()
    edeka_df = scrape_edeka()
    return rewe_df, lidl_df, kaufland_df, edeka_df

def analyze_with_ai(json_data, prompt):
    ai_prompt = f"""Basierend auf diesen Sondernangeboten aus Supermärkten {json_data}, gib mir die Top 25 Angebote für jemanden mit diesem Wunschprofil: 
    {prompt}, Bitte zeige keine Non-Food-Artikel. 
    Antworte im JSON-Format, das die gleiche Struktur wie die Eingabe hat.in JSON format that has the same structure as the input. the key of the dictionairy is "angebote" """
    response = client.chat.completions.create(
        model="gpt-4o",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are a helpful assistant designed to output JSON."},
            {"role": "user", "content": ai_prompt}
        ],
        temperature=0,
    )
    analyzed_data = json.loads(response.choices[0].message.content)
    print(analyzed_data)
    return pd.DataFrame(analyzed_data['angebote'])

def price_scraper_page():
    st.title("🔍 Price Scraper")

    st.write("Enter Stichwörter for better AI analysis:")
    stichworter = st.text_input("Stichwörter", "Veggie, Schokolade, Olivenöl")

    if st.button("Scrape"):
        with st.spinner("Scraping prices..."):
            rewe_df, lidl_df, kaufland_df, edeka_df = scrape_prices()

        if not rewe_df.empty:
            st.write("### Rewe Offers")
            st.dataframe(rewe_df)
        else:
            st.write("No Rewe data found.")

        if not lidl_df.empty:
            st.write("### LIDL Offers")
            st.dataframe(lidl_df)
        else:
            st.write("No LIDL data found.")

        if not kaufland_df.empty:
            st.write("### Kaufland Offers")
            st.dataframe(kaufland_df)
        else:
            st.write("No Kaufland data found.")

        if not edeka_df.empty:
            st.write("### Edeka Offers")
            st.dataframe(edeka_df)
        else:
            st.write("No Edeka data found.")

        combined_df = pd.concat([rewe_df, lidl_df, kaufland_df, edeka_df])
        combined_df = combined_df.sort_values(by="Discount", ascending=False, na_position='last')
        st.write("### Combined Offers")
        st.dataframe(combined_df)

        # Perform AI analysis
        with st.spinner("Analyzing data with AI..."):
            json_data = combined_df.to_json(orient='records')
            print(json_data)
            analyzed_df = analyze_with_ai(json_data, stichworter)

        st.write("### Analyzed Offers")
        st.dataframe(analyzed_df)

if __name__ == "__main__":
    price_scraper_page()
