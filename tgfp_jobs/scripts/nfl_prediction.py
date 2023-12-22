import requests
from bs4 import BeautifulSoup


def main():
    url = 'https://www.nflgamesim.com/nfl-predictions.asp?WeekSN=15'
    req = requests.get(url, timeout=10)
    soup = BeautifulSoup(req.content, 'html.parser')
    rows = soup.find_all('tr')
    for row in rows:
        print(row)

if __name__ == '__main__':
    main()