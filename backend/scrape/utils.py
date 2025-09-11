import requests

class WebPageScraper:
    def __init__(self, url, element):
        self.url = url
        self.element = element
        self.robots_txt = None

    def check_access(self, user_agent='*', path='/'):
        disallowed_paths = []
        robots_txt = self._fetch_robots_txt()
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
        if not self.robots_txt:
            robots_url = '/'.join(self.url.split('/')[:3]) + '/robots.txt'
            response = requests.get(robots_url)

            if response.status_code == 200:
                self.robots_txt = response.text
            else:
                self.robots_txt = ""

        return self.robots_txt
    
    def fetch_content(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            print(response.text)
        else:
            print(response)