import requests
from lxml import html
import csv
from bs4 import BeautifulSoup


def fetch_content(url):
    response = requests.get(url)
    try:
        response.status_code == 200
        return response.content
    except:
        print(f'The status code for this website is: {response.status_code}')
        return None


def get_medal_holders_data(url):
    content = fetch_content(url)
    if content:
        tree = html.fromstring(content)
        campus_path_query = '//a[text()="Medal Holders"]/@href'
        results = tree.xpath(campus_path_query)
        data = []

        for result in results:
            if result.startswith('/'):
                result = requests.compat.urljoin(url, result)
                campus_medal_request = requests.get(result)
                r = campus_medal_request.content
                soup = BeautifulSoup(r, "html.parser")

                headers = [th.text.strip() for th in soup.find_all("th")]
                headers.insert(0,"Degree")
                
                degree_program = soup.find_all("div",class_ = "col-md-4 mb")
                for degree in degree_program:
                       degree_name = degree.find("strong").text.strip()
                       for row in degree.find_all("tr"):
                               cells = [td.text.strip() for td in row.find_all("td")]
                               if cells:
                                   cells.insert(0,degree_name)
                                   data.append(cells)

            data_to_csv(data)


def data_to_csv(data):
    with open('medal_holders.csv', 'w', newline='', encoding='utf-8') as medal_data:
        writer = csv.writer(medal_data)
        writer.writerow(['Degree','Sr.#','Roll No','Name','Medal'])
        for row in data:
            writer.writerow(row)


if __name__ == '__main__':
    base_url = 'https://www.nu.edu.pk/'
    get_medal_holders_data(base_url)
