from datetime import datetime
from pprint import pprint

import bs4
import requests
from bs4 import BeautifulSoup


def collect_all_matches():
    results_page_url = "https://siege.gg/matches?tab=results"

    result = BeautifulSoup(requests.get(results_page_url).content, features="html.parser")

    max_number_of_pages = int(result.find_all("a", class_="page-link")[-2].text)

    print(max_number_of_pages)

    all_results = {}

    for i in range(1, max_number_of_pages + 1):
        result = collect_page_matches(i)
        all_results.update(result)

    return all_results


def collect_page_matches(page_number):
    url = "https://siege.gg/matches?tab=results&season=&date=&page=&tab=results&page={0:d}".format(page_number)

    result = BeautifulSoup(requests.get(url).content, features="html.parser")

    matches = result.find_all("a", class_="match--has-results")

    print(len(matches))

    answers = {}

    for match in matches:
        match: bs4.element.Tag

        url: str = match.attrs['href']

        match_id = int(url.split('/')[-1])

        player1, player2 = [player.text.strip() for player in match.find_all("span", attrs={"class": "match__name"})]

        answers[match_id] = {
            "url": "{0:s}{1:s}".format(base_url, url),
            "player1": player1,
            "player2": player2,
        }

    # pprint(answers)

    return answers


def collect_all_match_results(ids):
    results = {}

    for match_id in ids:
        results[match_id] = collect_match_result(match_id)

    return results


def collect_match_result(match_identifier):
    match_id = match_identifier

    if isinstance(match_identifier, int):
        match_url = "https://siege.gg/matches/{0:d}".format(match_identifier)
    else:
        match_id = int(match_identifier.split("/")[-1])

        match_url = match_identifier

    result = BeautifulSoup(requests.get(match_url).content, features="html.parser")

    player_1_score, player_2_score = (int(r.text) for r in result.find_all("div", class_="match__score"))

    print(player_1_score, player_2_score)

    # timestamp = datetime.strptime(result.find("time").attrs["datetime"], "%Y-%m-")
    timestamp = datetime.fromisoformat(result.find("time").attrs["datetime"])
    # print(timestamp)

    log = result.find("div", attrs={"id": "game-log-1"})
    s = log.find_all_next("li", class_="log__line")

    actions = []

    for action in s:
        svg = action.find("svg")
        r = {}

        if svg is not None:
            v = 0 if "side-icon--defend" in svg.attrs["class"] else 1
            # print(v)

            r["action"] = v
        else:
            r["action"] = -1

        r["message"] = action.text.strip()

        actions.append(r)

    season = result.find("span", class_="meta__season").text.strip()
    region = result.find("span", class_="match__region").text
    season_number = result.find("span", class_="match__season-number").text

    return {match_id: {
        "timestamp": timestamp,
        "player_1_score": player_1_score,
        "player_2_score": player_2_score,
        "actions": actions,
        "season": season,
        "season_number": season_number,
        "region": region,
    }}


if __name__ == '__main__':
    base_url = "https://siege.gg"

    # collect_all_matches()
    pprint(collect_page_matches(1))
    pprint(collect_match_result(2835))
