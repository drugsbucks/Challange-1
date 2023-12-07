import httpx, pandas as pd
from selectolax.parser import HTMLParser
import time, random

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15"}
results = []

start = time.time()
for i in range(1,13):
    url = f'https://gopher1.extrkt.com/?paged={i}'
    resp = httpx.get(url=url, headers=headers)
    html = HTMLParser(resp.text)
    products = html.css('li.product')
    for product in products:
        tags = []
        item = {
                "productId" : product.css_first('a.button').attributes.get('data-product_id'),
                "productSKU" : product.css_first('a.button').attributes.get('data-product_sku'),
                "product_url" : product.css_first('a').attributes.get('href'),
                "name" : product.css_first('h2').text(),
                "price" : product.css_first('bdi').text()
                }
        productResp = httpx.get(url=item['product_url'], headers=headers)
        productHtml = HTMLParser(productResp.text)
        cat = productHtml.css_first('span.posted_in')
        item['Category'] = cat.css_first('a').text()
        item['Short Description'] = productHtml.css_first('div.woocommerce-product-details__short-description > p').text()
        item['Description'] = productHtml.css_first('#tab-description > p:nth-child(2)').text()
        for tag in productHtml.css_first('nav.woocommerce-breadcrumb').css('a'):
            tags.append(tag.text())
        tags.pop(0)
        item['tags'] = tags
        try:
            item['Features'] = productHtml.css_first('#tab-description > p:nth-child(3)').text().replace('•','').strip()
        except AttributeError:
            try:
                item['Features'] =  productHtml.css_first('#tab-description > ul').text().replace('\n','').strip()
            except AttributeError:
                try:
                    item['Features'] =  productHtml.css_first('#tab-description > p br').text().replace('\n','').strip()
                except AttributeError:
                    item['Features'] = 'None'
        #Related items
        relatedItems = []
        #tab-description > p > br:nth-child(1)
        try:
            for relItem in productHtml.css_first('div > section').css('li'):
                # print(item['name'] + relItem.css_first('a h2').text())
                relProduct = {
                    'Name' : relItem.css_first('a h2').text()
                    # 'Price' : relItem.css_first('span').text(),
                    # 'Link' : relItem.css_first('a.woocommerce-LoopProduct-link.woocommerce-loop-product__link').attributes.get('href')
                    }
                relatedItems.append(relProduct)
            item['Related Products'] = relatedItems
        except AttributeError:
                item['Related Products'] = 'None'
        
        try:
            item['sizes'] = productHtml.css_first('#tab-additional_information > table > tbody > tr.woocommerce-product-attributes-item.woocommerce-product-attributes-item--attribute_size > td > p').text()
        except AttributeError:
            item['sizes'] = 'None'
        try:
            item['Activity'] = productHtml.css_first('#tab-additional_information > table > tbody > tr.woocommerce-product-attributes-item.woocommerce-product-attributes-item--attribute_activity > td > p').text()
        except AttributeError:
            item['Activity'] = 'None'
        try:
            item['Gender'] = productHtml.css_first('#tab-additional_information > table > tbody > tr.woocommerce-product-attributes-item.woocommerce-product-attributes-item--attribute_gender > td > p').text()
        except AttributeError:
            item['Gender'] = 'None'
        try:
            item['Material'] = productHtml.css_first('#tab-additional_information > table > tbody > tr.woocommerce-product-attributes-item.woocommerce-product-attributes-item--attribute_material > td > p').text()
        except AttributeError:
            item['Material'] = 'None'
        try:
            item['Color'] = productHtml.css_first('#tab-additional_information > table > tbody > tr.woocommerce-product-attributes-item.woocommerce-product-attributes-item--attribute_color > td > p').text()
        except AttributeError:
            item['Color'] = 'None'  
        results.append(item)
    print(f'Page number: {i}, Number of items scraped: {len(results)} ')
    time.sleep(random.randint(1,3)+ random.random())
# print(len(results))
#product-141 > div.summary.entry-summary > div.product_meta > span.posted_in
#product-141 > div.summary.entry-summary > div.woocommerce-product-details__short-description > p
resultsDf = pd.DataFrame(results)
# print(resultsDf)
end = time.time()
duration = end - start
print(f"Scraping Duration: {duration}")
resultsDf.to_clipboard()
