from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
import time

BASE_URL = "https://www.presidency.ucsb.edu/documents/presidential-documents-archive-guidebook/annual-messages-congress-the-state-the-union"

def fetch_speech_links():
    response = requests.get(BASE_URL)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    speech_links = soup.select("td a[href]")
    speeches = []
    for link in speech_links:
        year = link.get_text().replace("*", "").strip()
        if len(year) == 4 and year.isdigit():
            full_url = urljoin(BASE_URL, link["href"])
            speeches.append({
                "year": year,
                "url": full_url
            })
    return speeches

def download_speech(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    
    speech_content = soup.find("div", class_="field-docs-content")
    speech_text = speech_content.get_text(strip=True) if speech_content else None
    
    president_element = soup.find("h3", class_="diet-title")
    president_name = president_element.find("a").get_text(strip=True) if president_element else "Unknown"
    
    return speech_text, president_name

def scrape_speeches(output_file="state_of_union_speeches.json"):
    speeches = fetch_speech_links()
    print(f"Found {len(speeches)} speeches.")
    
    all_speeches = []
    for ix, speech in enumerate(speeches):
        try:
            print(f"Downloading: ({ix + 1}/{len(speeches)}) Year: {speech['year']}")
            text, president = download_speech(speech["url"])
            if text:
                all_speeches.append({
                    "year": speech["year"],
                    "url": speech["url"],
                    "president": president,
                    "text": text
                })
            else:
                print(f"Warning: No text found for {speech['year']}")
            time.sleep(1)
        except Exception as e:
            print(f"Failed to download {speech['year']}: {e}")
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(all_speeches, file, indent=2)
    print(f"Saved {len(all_speeches)} speeches to {output_file}.")

if __name__ == "__main__":
    scrape_speeches()
