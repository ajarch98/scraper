import urllib.request
import requests
from bs4 import BeautifulSoup

def return_categories():
    """Return a list of dictionaries in the format [{category: cat1, url: url1}]"""
    url = r"https://www.leaderdrive.fr/magasin/leader-price-drive-parismagenta/"
    with urllib.request.urlopen(url) as url:
        html = url.read()
    soup = BeautifulSoup(html, 'html.parser')
    section = soup.find("section", attrs = {'class':'product-nav product-nav--inline show-for-large'})
    links = section.find_all("a")
    categories = []
    for link in links:
        category = link['title']
        url = r"https://www.leaderdrive.fr" + link['href']
        temp = {'category':category, 'url':url}
        categories.append(temp)
    return categories

categories = return_categories()

import mysql.connector

db = mysql.connector.connect(host = "localhost",
                            user = "root",
                            passwd = "password",
                            database = "price_leader")
							
#This code created the two mySQL Tables
# cursor.execute("CREATE TABLE Categories (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(255), number_of_products INT, last_product_scrapped INT, url_id INT)")
# cursor.execute("CREATE TABLE Products (id INT AUTO_INCREMENT PRIMARY KEY, title VARCHAR(255), url VARCHAR(255), price DECIMAL(10,2), unit_of_measurement VARCHAR(255), per_unit_label VARCHAR(255), category_id INT NOT NULL,  FOREIGN KEY fk_cat(category_id) REFERENCES Categories(id))")

#This code inserts data into the categories table
# val = []
# for category in categories:
#     url = category['url']
#     with urllib.request.urlopen(url) as url:
#         html = url.read()
#     soup = BeautifulSoup(html, 'html.parser') 
#     no_of_products_span = soup.find("span", attrs = {"class":"product-filter-list__count"})
#     value_tuple = (category['category'], no_of_products_span.text, 0, 1)
#     val.append(value_tuple)
    
# cursor = db.cursor()
# sql = "INSERT INTO categories (name, number_of_products, last_product_scrapped, url_id) VALUES (%s, %s, %s, %s)"

# cursor.executemany(sql, val)
# db.commit()
# print(cursor.rowcount, "was inserted")




#cell containing code to populate products table

import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException   


from shadow_useragent import ShadowUserAgent
shadow_user_agent = ShadowUserAgent()

categories_info = []

for _, category in enumerate(categories, start = 1):
    options = Options()
    options.add_argument("user-agent = {}".format(shadow_user_agent.random_nomobile))

    browser = webdriver.Chrome(executable_path = r'C:\Users\PAVILION\Documents\Work\price_leader\chromedriver.exe', options = options)

    browser.get(category['url']) #open category url
    html = browser.find_element_by_tag_name('html') #get HTML element from category page
    html.send_keys(Keys.END) #scroll to end of page to load all products
    product_elements = html.find_elements_by_class_name('card-product-a__panel') #find product_elements on the category web page

    products = [] #initialize list

    for elem in product_elements:
        title = elem.find_element_by_css_selector('.card-product-a__name.clic_open_product_fiche').text #get product title
        #urllib.request.urlretrieve(img_url, 'C:\\Users\\PAVILION\\Documents\\Work\\price_leader\\images\\' + categories[1]['category'] + '\\' + title + '.jpg')
        try: #if an error is thrown in the Try block, execute except block. Could not use if function because program breaks if selenium does not find element
            promo_price_elem = elem.find_element_by_css_selector('.product-price__number.product-price__promo') #get price elements
            price_int = promo_price_elem.find_element_by_class_name('product-price__integer').text #get price integer
            price_decimal = promo_price_elem.find_element_by_class_name('product-price__decimal').text #get price decimal
        except NoSuchElementException:
            price_int = elem.find_element_by_class_name('product-price__integer').text #get price integer
            price_decimal = elem.find_element_by_class_name('product-price__decimal').text #get price decimal
        price = price_int + ',' + price_decimal #join price integer and price decimal
        per_unit_label_elem = elem.find_element_by_class_name('product-price__summary') #get element for per_unit_label
        if ' ' in per_unit_label_elem.text: #if space exists in per_unit_label string
            per_unit_label = per_unit_label_elem.text.split(' ')[1] #split per_unit_label text
        else:
            per_unit_label = per_unit_label_elem.text 
        if "LITRE" in per_unit_label :
            unit_of_measure = 'Liter'
        if "KILO" in per_unit_label:
            unit_of_measure = 'Kilogramme'
        if 'Unit' in per_unit_label:
            unit_of_measure = 'Unite'
        product_id = elem.find_element_by_css_selector('.card-product-a__quantity.product-quantity').get_attribute('product-quantity') #Get attribute product-quantity for product_id element
        r = requests.post(r'https://www.leaderdrive.fr/product_ajax/', data = {'id_product':product_id, 'id_entity':864}) #retrieve product url
        product_url_name = r.json()['name_product'] #retrieve product_url_name from response to request on line above
        product_url = r'https://www.leaderdrive.fr/magasin/leader-price-drive-parismagenta/rayon/' + category['category'] + '/produit/' + product_id + '-' + product_url_name #create product_url
        #TODO: retrieve images
        if not os.path.isdir("C:\\Users\\PAVILION\\Documents\\Work\\price_leader\\images\\" + category['category']): #create category folder for images if it does not exist
            os.mkdir('C:\\Users\\PAVILION\\Documents\\Work\\price_leader\\images\\' + category['category'])
        category_id = _ #retrieve category_id from enumerate() function
        product_info = (title, product_url, price,unit_of_measure, per_unit_label, _) #put values into tuple for future SQL statement
        products.append(product_info) #append product_info to list of products
#         image_browser_page = browser.get(product_url)
#         time.sleep(5)
#         image_page_html = browser.find_element_by_tag_name('html')
#         image_elems = image_page_html.find_elements_by_class_name('product-media-gallery__media')
#         for img_no, image_elem in enumerate(image_elems):
#             if '640' in image_elem.get_attribute('src'):
#                 image_url = image_elem.get_attribute('src')
#                 print(image_url)
#                 urllib.request.urlretrieve(image_url, 'C:\\Users\\PAVILION\\Documents\\Work\\price_leader\\images\\' + category['category'] + '\\' + product_url_name + str(img_no) + '.jpg')
#         browser.execute_script("window.history.go(-1)")
    categories_info.append(products) #append list of products to categories_info
    product_scrapped = len(products) #get number of products_scrapped for each category
    browser.quit() #close chromedriver instance
    #TODO: Add info in product_info tuples to products table
    #TODO: add product_scrapped to category table
        # TODO: cursor = db.cursor()    
        # sql = 'INSERT INTO products (title, url, price, unit_of_measurement, per_unit_label, category_id) VALUES (%s, %s, %s, %s, %s, %s)'
    
print(categories_info)