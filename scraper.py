import requests
import bs4
from unidecode import unidecode
from googlesearch import search
from time import sleep

URL = 'https://www.lasy.gov.pl/pl/edukacja/lesnoteka-1/drzewa?b_start:int='


class Tree:
    def __init__(self, name, desc, details_link):
        self.name = name
        self.site_name = unidecode(name.lower().replace(' ', '_'))
        self.desc = desc
        self.details_link = details_link

    def to_md(self):
        return f'### [{self.name}](drzewa/{self.site_name}.markdown)\n![{self.name}](images/{self.site_name}.jpg)\n\n{self.desc}\n'

    def to_md_details(self):
        req = requests.get(self.details_link)
        sleep(2)
        soup = bs4.BeautifulSoup(req.content, 'html.parser')
        paragraphs = soup.find('div', id='parent-fieldname-text').find_all('p')
        ret = f'# {self.name}\n\n---\n{self.desc}\n\n---\n'
        for p in paragraphs:
            ret += p.text
            ret += '\n\n'

        ret += f'## {self.name} - wyniki:\n'
        for site in search(self.name, stop=3):
            ret += f'[{site}]({site})\n\n'

        return ret


def scrape(url):
    tree_list = []
    req = requests.get(url)
    soup = bs4.BeautifulSoup(req.content, 'html.parser')
    trees = soup.find_all('article', class_='tileItem')
    for tree in trees:
        name = tree.find('div', class_='tileHeadline').find('a').text
        desc = tree.find('span', class_='description').text
        link = tree.find('div', class_='tileHeadline').find('a')['href']
        tree_list.append(Tree(name, desc, link))
        img_url = 'https://lasy.gov.pl' + tree.find('div', class_='tileImage').find('img')['src']
        img = requests.get(img_url).content
        sleep(2)
        with open(f'website/images/{tree_list[-1].site_name}.jpg', 'wb') as f:
            f.write(img)
        print(f'Scraped {name}')
    return tree_list


def main():
    trees = []
    trees.extend(scrape(URL + '0'))
    trees.extend(scrape(URL + '12'))
    trees.extend(scrape(URL + '24'))

    for tree in trees:
        with open(f'website/drzewa/{tree.site_name}.markdown', 'w') as f:
            f.write(tree.to_md_details())
        print(f'Created subpage for {tree.name}')

    with open('website/index.markdown', 'w') as f:
        f.write('# Drzewa w Polsce\n')

        f.write('## Opis\n')
        f.write('**Drzewa** są roślinami wieloletnimi, mającymi zdrewniały jeden pęd główny (pień) lub kilka pędów '
                'głównych i gałęzi, tworzących koronę. To największe lądowe rośliny, rekordziści osiągają ponad 100 '
                'metrów wysokości. Drzewo nie jest jednostką systematyczną, to tylko grupa podobnych organizmów '
                'roślinnych. Drzewa istnieją na ziemi od 370 milionów lat. Nauka o drzewach to **dendrologia**.\n')

        f.write('## Podział drzew\n')
        f.write('Tradycyjnie stosuje się podział na:\n')
        f.write('- **Drzewa iglaste (szpilkowe)** to drzewa należące do roślin nagonasiennych. Mają liście w postaci '
                'igieł lub łusek. Z niewielkimi wyjątkami (modrzew, metasekwoja, cypryśnik błotny, modrzewnik, '
                'Glyptostrobus pensilis) to rośliny wiecznie zielone, czyli takie, które nie zrzucają igieł na zimę. '
                'Drzewa iglaste dominują w chłodnym klimacie. Czasem do grupy drzew iglastych zalicza się także '
                'miłorząb dwuklapowy i przęśl.\n')
        f.write('- **Drzewa liściaste** to drzewa z grupy roślin okrytonasiennych. Mają stosunkowo szerokie blaszki '
                'liści. Występują głównie w ciepłym i umiarkowanym klimacie. W klimacie umiarkowanym najczęściej '
                'zrzucają liście na zimę.\n')

        f.write('## Gatunki drzew w Polsce\n')
        for tree in trees:
            f.write(tree.to_md())



if __name__ == '__main__':
    main()