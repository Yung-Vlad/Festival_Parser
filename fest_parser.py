from bs4 import BeautifulSoup
import requests
from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from data_writer import write_to_json, write_to_csv, convert_to_pdf


# global vars
headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                  " (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
}
images_list = []
full_info = []


# get data from our site
def get_data(url):
    response = requests.get(url=url, headers=headers)
    src = response.text

    with open("data/index.html", 'w', encoding="utf-8") as file:
        file.write(src)

    with open("data/index.html", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")
    cards = soup.find_all("div", class_="card flex-height lvl-1 brt-5px bg-white relative has-details")

    counter = 1
    global full_info, images_list

    # collect all the cards in certain category of the festivals
    for i in cards:
        # get fest name
        card_info = i.find("div", class_="card-info")
        fest_name = card_info.find("h3").text

        # check if the data doesn't contain this fest
        if repeatability_check(fest_name):
            print(f"Festival #{counter} ({fest_name}), already exists in data\nSkip...")
            print('#' * 22)
            continue

        # get fest details-info
        details_list = i.find_all("p", class_="details-list")
        fest_place = details_list[0].text
        fest_date = details_list[1].text

        # get and save fest cover as img
        cover_link = i.find("img", class_="card-img").get("src")
        response = requests.get(cover_link).content
        with open(f"media/{counter}.png", "wb") as file:
            images_list.append(f"media/{counter}.png")
            file.write(response)

        # get fest link
        fest_link = "https://www.skiddle.com" + i.find("a", class_="card-details-link").get("href")

        # get source html-code
        src = using_selenium(url=fest_link)

        # get additional information
        soup = BeautifulSoup(src, "lxml")
        add_info = soup.find_all("span", class_="MuiChip-label MuiChip-labelMedium css-9iedg7")

        # get festival rating and tags
        fest_rating = None
        tags = []
        for j in add_info:
            text = j.text
            if text.replace('.', '').isdigit():
                fest_rating = text
            else:
                tags.append(text)

        if not tags:
            tags.append(None)

        # get fest_musicians
        musicians_container = soup.find("p", class_="MuiTypography-root MuiTypography-body1 css-1dzi2b8")
        fest_musicians = get_musicians(musicians_container)

        # append dict to list
        full_info.append({
            "Name": fest_name,
            "Place": fest_place,
            "Date": fest_date,
            "Link": fest_link,
            "Rating": fest_rating,
            "Tags": tags,
            "Musicians": fest_musicians
        })

        print(f"Festival: #{counter} done...")
        print('#' * 22)
        counter += 1


# return a dict of the musicians
def get_musicians(container):
    musicians_list = []
    fest_musicians = {}

    try:
        musicians_link = container.find_all("a")
        for j in musicians_link:
            fest_musicians[j.text] = j.get("href")
    except Exception as ex:
        print(ex)

    try:
        musicians_span = container.find_all("span")
        for j in musicians_span:
            if '/' not in j.text:
                musicians_list.append(j.text)
    except Exception as ex:
        print(ex)

    musicians_list = {key: None for key in musicians_list}
    fest_musicians.update(musicians_list)

    return fest_musicians


# return False if this festival doesn't exist in data else True
def repeatability_check(name):
    for i in full_info:
        if i["Name"] == name:
            return True

    return False


# return the src code
def using_selenium(url):
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.get(url=url)

    sleep(1)
    src = driver.page_source
    driver.quit()

    return src


# main function
def main():
    get_data(url="https://www.skiddle.com/festivals/")
    write_to_json(full_info)
    write_to_csv(full_info)
    convert_to_pdf(images_list)


if __name__ == '__main__':
    main()
