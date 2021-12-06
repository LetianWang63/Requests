import math
import requests
import bs4
import json
import re
from bs4 import BeautifulSoup



MAIN_URL = 'https://www.toysrus.ca/'
CATEGORY_URL = MAIN_URL + 'en/toysrus/Category'
SOURCE_URL = MAIN_URL + 'en/search-updategrid'



class Item:
    def __init__(self):
        self.pid = 'N/A'
        self.title = 'N/A'
        self.price = 'N/A'
        self.url = 'N/A'
        self.upc = 'N/A'
        self.img = 'N/A'

    # consume an item and url, produce an Item
    def get_data(self, item_url):
        r = requests.get(item_url)
        soup = BeautifulSoup(r.text, 'lxml')
        self.url = item_url

        # find tag with pid
        class_pid = 'l-pdp js-product-detail'
        tag_pid = soup.find('div', class_pid)
        self.pid = tag_pid['data-pid']

        # find tag with title
        class_title = 'b-product_details-name'
        tag_title = soup.find('h1', class_title)
        self.title = tag_title.string

        # find tag with price
        class_old = 'b-price-value js-list-price-value'
        class_new = 'b-price-value js-sales-price-value'
        tag_old = soup.find('span', class_old)
        tag_new = soup.find('span', class_new)
        if tag_old == None:
            # if tag_old is None, then item is not on discount
            self.price = tag_new.string[1:-1]
        else:
            self.price = 'Was: ' + tag_old.string[1:-1] + ' Now: ' + tag_new.string[1:-1]

        # find tag with upc
        tag_upc = soup.find(lambda tag: tag.name=='li' and 'UPC' in tag.text)
        if tag_upc.find('strong') == None:
            self.upc = 'None'
        else:
            self.upc = tag_upc.find('strong').string

        # find tag with img
        class_img = 'b-product_carousel-image_item js-product-image'
        tag_img = soup.find_all('img', class_img, src=True)
        self.img = []
        for img in tag_img:
            self.img.append(img['src'])



# produce a list of url for all categories
def list_category_url():
    r = requests.get(CATEGORY_URL)
    soup = BeautifulSoup(r.text, 'lxml')
    class_name = 'shopallLink b-featured-carousel_shop-link'
    tags = soup.find_all('a', class_name)
    categories = []
    for a in tags:
        categories.append(a['href'])
    return(categories)

# consume a category url, produce a list of url for all items
def list_item_url(cat_url):
    items = []

    # get url for the first 24 items
    r = requests.get(cat_url)
    soup = BeautifulSoup(r.text, 'lxml')
    class_name = 'b-tile_image_container-link js-pdp-link'
    tags = soup.find_all('a', class_name)
    for a in tags:
        items.append(MAIN_URL + a['href'])
    
    # find cgid of category
    soup = BeautifulSoup(r.text, 'lxml')
    tag = soup.find('body')
    cat_id = tag['data-querystring'][5:]

    # find how many items in total
    class_name = 'b-plp_header-results_count js-header-bar'
    tag = soup.find('div', class_name).find_all('strong')[1]
    num_item = int(tag.string)

    # iterate on source url to get all other items
    item_per_page = 24
    num_page = math.floor(int(tag.string) / 24)
    for i in range(1, num_page + 1):
        print(cat_url[len(CATEGORY_URL)+1:] + ' ' + str(i) + '/' + str(num_page))
        page_params = {'cgid': cat_id, 'start': i*num_page, 'sz': num_page}
        r = requests.get(SOURCE_URL, params=page_params)
        soup = BeautifulSoup(r.text, 'lxml')
        class_name = 'b-tile_image_container-link js-pdp-link'
        tags = soup.find_all('a', class_name)
        for a in tags:
            items.append(MAIN_URL + a['href'])

    return(items)



if __name__ == '__main__':
    categories = list_category_url()
    for c in categories:
        items = list_item_url(c)
        item_data = []
        for i in items:
            new_item = Item()
            new_item.get_data(i)
            item_data.append(new_item.__dict__)
        with open('./all_items_json/' + c[len(CATEGORY_URL):] + \
            '.json', 'w', encoding='utf-8') as f:
            json.dump(item_data, f, indent=2)