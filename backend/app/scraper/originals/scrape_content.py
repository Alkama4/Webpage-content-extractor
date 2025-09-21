from utils import WebPageScraper

url = 'https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Al_cash'
element = 'div#content > div.section > table > tbody > tr > td:nth-of-type(2)'

scraper = WebPageScraper(url, element)
content = scraper.get_content()
if content:
    print('Some content was fetched')
    print(content.text)
else:
    print("Access to the content is disallowed")
    print(content)
