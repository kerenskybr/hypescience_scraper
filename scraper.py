import mechanicalsoup
from loguru import logger
from fire import Fire
import time
from fp.fp import FreeProxy

ROOT = 'https://hypescience.com/page/'

class HomePage:
    """ Get title, url, body, then uses the link to
        to visit the page and get the body text
    """
    def __init__(self, title, url, body):
        self.title = title
        self.url = url
        self.body = body
        self.browser = mechanicalsoup.StatefulBrowser(
            raise_on_404=True,
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
            )
        logger.info(f"Title: {self.title} - URL: {self.url}")
        
        self.get_body_text()
    
    def get_body_text(self):
        time.sleep(.2)
        response = self.browser.open(self.url)
        section = response.soup.find('article', class_='content-area__body')
        all_p = section.find_all('p')
        self.body = [i.text.replace(',', '') for i in all_p]
        self.body = ''.join(self.body)
        #logger.info(f"Visit url {self.body}")


class HSScraper(HomePage):
    def __init__(self) -> None:
        self.body = HomePage.get_body_text
        self.browser = mechanicalsoup.StatefulBrowser(
            raise_on_404=True,
            user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            )

    def _get_links_title(self):
        page = 7
        while True:
            proxy = FreeProxy(timeout=1).get()
            logger.info(f"Using Proxy: {proxy}")

            try:
                response = self.browser.open(ROOT + str(page), proxies={'http':proxy, 'https':proxy}, verify=False)
                logger.info(f"Opening {response}")
            except:
                response = self.browser.open(ROOT + str(page), proxies={'http':proxy, 'https':proxy}, verify=False)
                logger.info(f"Opening {response}")

            if response.status_code == 403:
                logger.info(f"Bad proxy. Returning {response}")
                response = self.browser.open(ROOT + str(page), proxies={'http':proxy, 'https':proxy}, verify=False)
                logger.info(f"Opening {response}")

            article = response.soup.find_all('article', class_='posts__item')

            self.title_and_url = [
                HomePage(
                    title=i.find('a', class_='posts__item__thumb__link').text.replace(',', '').replace('&#8220', '').replace('&#8221', ''),
                    url=i.find('a', class_='posts__item__thumb__link')['href'],
                    body=self.body,
                )
                for i in article 
            ]
            page +=1
            
            logger.info(f"Scrapping page {page}")

            # Saving after each page
            self._save_to_file()

            if article is None:
                break
    
    def _save_to_file(self):
        logger.info(f"Saving to file")
        with open('data.csv', 'a') as file:
            for i in self.title_and_url:
                #for key, value in i.__dict__.items():
                file.write("%s,%s,%s\n" % (i.__dict__['title'], i.__dict__['url'], i.__dict__['body']))
    
    def start(self):
        self._get_links_title()
        #self._save_to_file()


if __name__ == "__main__":
    hs = HSScraper()
    hs.start()

    #Checking if the csv has 3 columns
    # import pandas
    # df = pandas.read_csv('data.csv')
    # print(df)
