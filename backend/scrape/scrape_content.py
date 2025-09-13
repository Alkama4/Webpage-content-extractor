from utils import WebPageScraper

url = 'https://www.westmetall.com/en/markdaten.php?action=table&field=LME_Al_cash'

def main(url, element):
    scraper = WebPageScraper(url, element)
    content = scraper.get_content()
    if content:
        print('Some content was fetched')
        print(content)
    else:
        print("Access to the content is disallowed")
        print(content)


if __name__ == "__main__":
    element = 'body'
    main(url, element)

