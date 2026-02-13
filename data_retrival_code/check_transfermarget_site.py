import requests
from bs4 import BeautifulSoup
import time

# Test single page fetch
url = "https://www.transfermarkt.com/spieler-statistik/wertvollstespieler/marktwertetop"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

print("Fetching URL:", url)
response = requests.get(url, headers=headers)
print("Status Code:", response.status_code)
print("Content Length:", len(response.content))

# Save HTML to file to inspect
with open('debug_page.html', 'w', encoding='utf-8') as f:
    f.write(response.text)

print("\n✅ Saved page HTML to debug_page.html - open it in browser to see what you got")

# Quick check for common elements
soup = BeautifulSoup(response.content, 'html.parser')
print("\nFound tables:", len(soup.find_all('table')))
print("Found divs:", len(soup.find_all('div')))
print("Found links:", len(soup.find_all('a')))

# Look for player names
print("\nSearching for player-related content...")
player_links = soup.find_all('a', href=True)
for link in player_links[:10]:  # First 10 links
    if 'spieler' in link['href'] or 'profil' in link['href']:
        print(f"Found potential player link: {link.get('title', 'No title')} -> {link['href']}")