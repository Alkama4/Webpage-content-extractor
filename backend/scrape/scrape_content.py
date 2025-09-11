from utils import WebPageScraper


url = 'https://www.lme.com/en/Metals/Non-ferrous/LME-Aluminium-Alloy#Summary'

def main(url, element):
    scraper = WebPageScraper(url, element)
    disallowed_paths = scraper.check_access()
    access = None

    if disallowed_paths == []:
        access = True
    else:
        for path in disallowed_paths:
            if path in url:
                access = False
            else:
                access = True

    if access:
        print(f"Access granted to {url}")

        content = scraper.fetch_content()
        print(content)

    else:
        print(f"Access denied to {url}")


if __name__ == "__main__":
    element = 'body'
    main(url, element)

