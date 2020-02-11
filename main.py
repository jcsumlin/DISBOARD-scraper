import requests
from bs4 import BeautifulSoup
import re
import json
import csv

servers_home_page = requests.get("https://disboard.org/servers")
if servers_home_page.status_code != 200:
    raise ValueError("Unable to get Disboard servers list")
soup = BeautifulSoup(servers_home_page.text, 'html.parser')
print("What category of servers do you wish to scan for?")

count = 1
categories = []
ultag = soup.find('ul', {'class': 'categories'})
for span in ultag.find_all('span', {'class': 'name'}):
    print(f"{count}) {span.text}")
    categories.append(span.text)
    count += 1

category = int(input("> "))
if category > len(categories) or category < 1:
    raise ValueError("invalid Choice.")
category_name = categories[category-1]
print(f"Fetching 10 pages of {category_name} servers")
choice = category_name.replace('·', '').replace(' ', '-', 1).lower().replace(' ', '')
# choice = "anime-manga"
list_of_servers = []
for page in range(1,10):
    if page != 1:
        url = "https://disboard.org/servers/category/" + choice + "/" + str(page)
    else:
        url = "https://disboard.org/servers/category/" + choice
    servers = requests.get(url)
    soup = BeautifulSoup(servers.text, 'html.parser')

    if servers.status_code != 200:
        raise ValueError("Unable to get Disboard servers list")

    servers = soup.find_all('div', {'class': 'listing-card'})
    list_of_servers = list_of_servers + servers
end_result = []
for server in list_of_servers:
    basic_info = server.find('div', class_="server-name")
    div = basic_info.find('a')
    server_id = re.findall("\/server\/(\d+)", div.attrs['href'])
    if len(server_id) > 0:
        try:
            members_online = server.find('span', class_="server-online").get_text()
        except AttributeError:
            members_online = 0
            pass
        widget_code = f"https://discordapp.com/api/guilds/{server_id[0]}/widget.json"
        widget = requests.get(widget_code)
        if widget.status_code == 403:
            widget_code = "Disabled"
        elif widget.status_code == 429:
            # rate limited
            widget_code = f"https://discordapp.com/api/guilds/{server_id[0]}/widget.json"
        else:
            widget_code = widget.content
        server_bumped_at = server.find('div', class_="server-bumped-at").attrs['title']
        server_to_add = {"server_id": server_id[0], "server_name": div.get_text().strip(), "category": category_name, "members_online": members_online, "server_last_bumped": server_bumped_at, "widget_code": widget_code}
        end_result.append(server_to_add)
    else:
        print("Failed to compile server info")
        continue
keys = end_result[0].keys()
with open(f'{category_name} servers.csv', 'w+') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(end_result)
