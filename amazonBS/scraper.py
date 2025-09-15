import requests
from bs4 import BeautifulSoup
import sqlite3 

#Header for Page Content
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.5'
}

#Connect to SQLite database
db = sqlite3.connect('products.db')
cursor = db.cursor()

cursor.execute(''' CREATE TABLE IF NOT EXISTS products (
               id INTEGER PRIMARY KEY AUTOINCREMENT,
               title TEXT NOT NULL,
               price TEXT NOT NULL,
               product_url TEXT UNIQUE,
               scrape_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
db.commit()

def get_product_details(product_url: str) -> dict:
    #Create an empty product details dictionary
    product_details = {}

    #Get the product page content and create a soup
    page = requests.get(product_url, headers=headers)
    soup = BeautifulSoup(page.content, features ='lxml')

    try:
        #Scraping product details 
        #Title and Price from HTML Elements
        title = soup.find('span', attrs={'id': 'productTitle'}).get_text().strip()
        extracted_price = soup.find('span', attrs={'class': 'a-price'}).get_text().strip()
        price = '$' + extracted_price.split('$')[1]

        #Adding information to product details dictionary
        product_details['title'] = title
        product_details['price'] = price
        product_details['product_url'] = product_url
        #Save product to SQL database
        if product_details:
            save_product_to_db(product_details)

        return product_details
    
    except Exception as e:
        print('Could not fetch product details')
        print(f'Failed with exception: {e}')

def save_product_to_db(product):
    try:
        #Adding or updating product 
        cursor.execute('''
        INSERT OR REPLACE INTO products (title, price, product_url)
        VALUES (?, ?, ?) 
        ''', (product['title'], product['price'], product['product_url']))
        db.commit()

        print(f'Saved {product['title']} to database.')
    except Exception as e:
        print(f'Failed to save to data base: {e}')

def query_database():
    cursor.execute('SELECT * FROM products')
    rows = cursor.fetchall()
    for row in rows:
        print(row)

def main():
    product_url = input('Enter product url: ')
    product_details = get_product_details(product_url)
    #print(product_details)

if __name__ == "__main__":
    main()

