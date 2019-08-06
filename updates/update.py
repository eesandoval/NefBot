from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.request import urlretrieve
from datetime import date, timedelta, datetime
import os
import sys


main_url = "https://dragalialost.gamepedia.com"
bs_features = "html.parser"


def pretty_print_name(name):
    return name.strip('/').replace('_', ' ').replace('%27', "'")


def get_first_table(sub_url):
    url = main_url + '/' + sub_url
    content = urlopen(url).read()
    soup = BeautifulSoup(content, features=bs_features)
    table = soup.find_all("table")[0]
    return table


def get_filtered_names(sub_url, from_date):
    table = get_first_table(sub_url)
    result = {}
    for tr in table.find_all("tr", class_="character-grid-entry grid-entry"):
        tds = tr.find_all("td")
        s_date = tds[-1].string.strip()
        true_date = datetime.strptime(s_date, "%b %d, %Y").date()
        if true_date > from_date:
            result[tds[0].find_all('a')[0]["href"]] = tr
    return result


def get_portraits(names, directory):
    print("--- Getting portraits for " + directory + " ---")
    os.makedirs(directory, exist_ok=True)
    for name, tr in names.items():
        pretty_name = pretty_print_name(name)
        print("Processing " + pretty_name)
        image = tr.find_all("a")[0].find_all("img")[0]["srcset"].split()[2]
        urlretrieve(image, directory + pretty_name + ".png")


def get_pictures(names, directory, i=0):
    print("--- Getting pictures for " + directory + " ---")
    os.makedirs(directory, exist_ok=True)
    for name, _ in names.items():
        pretty_name = pretty_print_name(name)
        print("Processing " + pretty_name)
        new_url = main_url + name
        new_content = urlopen(new_url).read()
        new_soup = BeautifulSoup(new_content, features="html.parser")
        new_url = main_url + new_soup.find_all("a", class_="image")[i]["href"]
        new_content = urlopen(new_url).read()
        new_soup = BeautifulSoup(new_content, features="html.parser")
        full_image_div = new_soup.find_all("div", class_="fullImageLink")[0]
        image = full_image_div.find_all("a")[0]["href"]
        urlretrieve(image, directory + pretty_name + ".png")


def update_items(item, sub_url, lookback_period_days):
    from_date = date.today() - timedelta(days=lookback_period_days)
    names = get_filtered_names(sub_url, from_date)
    get_portraits(names, item + "/portraits/")
    if item == "wyrmprints":  # Wyrmrpints have 2 pictures
        get_pictures(names, item + "/base/")
        get_pictures(names, item + "/full/", 1)
        return
    elif item == "weapons":  # Weapons have no pictures
        return
    get_pictures(names, item + "/full/")


if __name__ == "__main__":
    retrieval_list = {"adventurers": "Adventurer_List",
                      "wyrmprints": "Wyrmprint_List",
                      "weapons": "Weapon_List",
                      "dragons": "Dragon_List"}
    lookback_period_days = 7
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        lookback_period_days = int(sys.argv[1])
    for k, v in retrieval_list.items():
        update_items(k, v, lookback_period_days)
