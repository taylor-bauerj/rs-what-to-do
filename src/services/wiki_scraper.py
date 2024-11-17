import aiohttp
from bs4 import BeautifulSoup

class WikiScraper:
    def __init__(self):
        self.wiki_base_url = "https://runescape.wiki"
        self.headers = {
            'User-Agent': 'RS-What-To-Do-Bot/1.0 (Contact: your@email.com)'
        }

    async def get_money_making_methods(self):
        url = f"{self.wiki_base_url}/w/Money_making_guide"
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                soup = BeautifulSoup(await response.text(), 'html.parser')
                return self._parse_money_making_table(soup)

    def _parse_money_making_table(self, soup):
        methods = []
        methods_table = soup.find('table', {'class': 'wikitable'})
        if methods_table and methods_table.find_all('tr')[1:]:
            for row in methods_table.find_all('tr')[1:]:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    methods.append({
                        'name': cols[0].get_text(strip=True),
                        'profit': cols[1].get_text(strip=True),
                        'requirements': cols[2].get_text(strip=True)
                    })
        return methods
