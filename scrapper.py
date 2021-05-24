import scrapy
import json
from scrapy.http import TextResponse
from w3lib.html import remove_tags

class Scrapper(scrapy.Spider):
    name = "LoL-Universe"
    allowed_domains = ["universe.leagueoflegends.com", "universe-meeps.leagueoflegends.com"]

    def start_requests(self):
        urls = ["https://universe-meeps.leagueoflegends.com/v1/en_au/search/index.json"]
        for urls in urls:
            yield scrapy.Request(url=urls, callback=self.parse_character_links)

    def parse_character_links(self, response: TextResponse):
        json_response = json.loads(response.body)
        champions = json_response["champions"]
        for champion in champions:
            champion_name = champion["slug"]
            champion_details_link = "https://universe-meeps.leagueoflegends.com/v1/en_au/champions/"+champion_name+"/index.json"
            # champion_details_link = "https://universe-meeps.leagueoflegends.com/v1/en_au/story/" + champion_name + "-color-story/index.json"
            yield scrapy.Request(url=champion_details_link, callback=self.parse_champion_details)

    def parse_champion_details(self, response: TextResponse):
        data = {}
        champion_details = json.loads(response.body)
        data["story_full"] = remove_tags(champion_details["champion"]["biography"]["full"])

        data["story_short"] = remove_tags(champion_details["champion"]["biography"]["short"])

        data["name"] = champion_details["champion"]["name"]

        race = ""
        if "races" in champion_details["champion"]:
            race = champion_details["champion"]["races"][0]["name"]
        data["race"] = race

        data["role"] = champion_details["champion"]["roles"][0]["name"]

        secondary_role = ""
        if len(champion_details["champion"]["roles"]) == 2:
            secondary_role = champion_details["champion"]["roles"][1]["name"]
        data["secondary_role"] = secondary_role

        data["region"] = champion_details["champion"]["associated-faction-slug"]
        yield data