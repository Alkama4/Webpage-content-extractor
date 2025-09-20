import requests
from bs4 import BeautifulSoup

class WebPageScraper:
    def __init__(self, url, element):
        ''' 
        Initialize with URL and CSS selector for the element to extract. 
        url: str - The URL of the webpage to scrape.
        element: str - The CSS selector of the HTML element to extract.
            e.g., 'div#content > div.section > table > tbody > tr > td:nth-of-type(2)'
            Note: "#" in CSS selector denotes id, "." denotes class.
        '''
        self.url = url
        self.element = element
        self.robots_txt = None

    def get_content(self):
        ''' 
        Main method to get content of the specified element if access is allowed by robots.txt. 
        returns: content: str or None
        '''
        disallowed_paths = self._check_access()
        access = None

        if disallowed_paths == []:
            access = True
        else:
            for path in disallowed_paths:
                if path in self.url:
                    print(f"Access to {self.url} is disallowed by robots.txt")
                    access = False
                    break
            else:
                access = True
            
        if access:
            self.content = self._fetch_content()
            self.result = self._parse_html()
            return self.result
        else:
            return None

    def _check_access(self, user_agent='*'):
        ''' 
        Check robots.txt file for disallowed paths for the given user agent. 
        user_agent: str - The user agent to check for (default is '*').
        Returns: disallowed_paths: list
        '''
        disallowed_paths = []
        robots_txt = self._fetch_robots_txt()
        if not robots_txt:
            return disallowed_paths

        lines = robots_txt.splitlines()
        for line in lines:
            if line.startswith('User-agent:'):
                current_user_agent = line.split(':')[1].strip()
                if current_user_agent == user_agent or current_user_agent == '*':
                    continue

            elif line.startswith('Disallow:'):
                disallowed_path = line.split(':')
                disallowed_path = disallowed_path[1].strip()
                if disallowed_path != '/' and disallowed_path != '':
                    disallowed_paths.append(disallowed_path)

        return disallowed_paths

    def _fetch_robots_txt(self):
        ''' 
        Fetch robots.txt file from the website. 
        Returns the content of robots.txt or None if not found.
        Returns: robots_txt: str or None
        '''
        if not self.robots_txt:
            robots_url = '/'.join(self.url.split('/')[:3]) + '/robots.txt'
            response = requests.get(robots_url)

            if response.status_code == 200:
                self.robots_txt = response.text
            else:
                self.robots_txt = None

        return self.robots_txt
    
    def _fetch_content(self):
        ''' 
        Fetch HTML content of the webpage. 
        Returns: content: str or None
        '''
        response = requests.get(self.url)
        if response.status_code == 200:
            return response.text
        else:
            print(f'Failed to fetch content from {self.url}, status code: {response.status_code}')
            return None

    def _parse_html(self):
        ''' 
        Parse HTML content and extract the specified element. 
        Returns: parsed_content: BeautifulSoup object or None
        '''
        if not self.content:
            return None

        soup = BeautifulSoup(self.content, 'html.parser')
        parsed_content = soup.select_one(self.element)
        return parsed_content