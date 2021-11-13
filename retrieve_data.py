import requests
import bs4
from bs4 import BeautifulSoup

class Item:
    def __init__(self):
        self.pid = 'N/A'
        self.title = 'N/A'
        self.price = 'N/A'
        self.url = 'N/A'
        self.upc = 'N/A'
        self.img = 'N/A'
    
    def __repr__(self):
        return '======================================================================\n' + \
            'pid: %s\ntitle: %s\nprice: %s\nurl: %s\nupc: %s\nimg: %s\n' \
            % (self.pid, self.title, self.price, self.url, self.upc, self.img)



MAIN_URL = 'https://www.toysrus.ca/'
CATEGORY_URL = MAIN_URL + 'en/toysrus/Category'
 


# function to get url for each category
def get_categories():
    r = requests.get(CATEGORY_URL)
    soup = BeautifulSoup(r.text, 'lxml')
    class_name = 'shopallLink b-featured-carousel_shop-link'
    tags = soup.find_all('a', class_name)
    categories = []
    for a in tags:
        categories.append(a['href'])
    return(categories)



# consume a category url, produce url for each item
def get_items(cat_url):
    r = requests.get(cat_url)
    soup = BeautifulSoup(r.text, 'lxml')
    class_name = 'b-tile_image_container-link js-pdp-link'
    tags = soup.find_all('a', class_name)
    items = []
    for a in tags:
        items.append(MAIN_URL + a['href'])
    return(items)



# consume an item url, produce an Item
def item_data(item_url):
    r = requests.get(item_url)
    soup = BeautifulSoup(r.text, 'lxml')
    i = Item()
    i.url = item_url

    # find tag with pid
    class_pid = 'l-pdp js-product-detail'
    tag_pid = soup.find('div', class_pid)
    i.pid = tag_pid['data-pid']

    # find tag with title
    class_title = 'b-product_details-name'
    tag_title = soup.find('h1', class_title)
    i.title = tag_title.string

    # find tag with price
    class_old = 'b-price-value js-list-price-value'
    class_new = 'b-price-value js-sales-price-value'
    tag_old = soup.find('span', class_old)
    tag_new = soup.find('span', class_new)
    if tag_old == None:
        # if tag_old is None, then item is not on discount
        i.price = tag_new.string[1:-1]
    else:
        i.price = 'Was: ' + tag_old.string[1:-1] + ' Now: ' + tag_new.string[1:-1]

    '''
    # find tag with upc
    tag_upc = soup.select('li > strong')
    '''

    # find tag with img
    class_img = 'b-product_carousel-image_item js-product-image'
    tag_img = soup.find_all('img', class_img, src=True)
    img_sources = ''
    for img in tag_img:
        img_sources = img_sources + img['src'] + '\n'
    i.img = img_sources

    return i



if __name__ == '__main__':
    categories = get_categories()
    for c in categories:
        items = get_items(c)
        with open('.\\all_items\\' + c[len(CATEGORY_URL):] + \
            '.txt', 'w', encoding='utf-8') as f:
            for i in items:
                f.write(str(item_data(i)))
