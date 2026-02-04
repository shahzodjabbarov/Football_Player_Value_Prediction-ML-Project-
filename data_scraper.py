import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
import re

class TransfermarktScraper:
    def __init__(self):
        self.base_url = "https://www.transfermarkt.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        self.players_data = []
    
    def get_page(self, url):
        """Fetch a page with error handling"""
        try:
            response = self.session.get(url, timeout=15)
            time.sleep(random.uniform(2, 4))  # Random delay to be polite
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def scrape_player_list_page(self, page_num):
        """Scrape one page of top players - gets ~25 players per page"""
        url = f"{self.base_url}/spieler-statistik/wertvollstespieler/marktwertetop?page={page_num}"
        print(f"Fetching page {page_num}: {url}")
        
        soup = self.get_page(url)
        if not soup:
            return []
        
        player_urls = []
        
        # Find all links with '/profil/spieler/' in href
        all_links = soup.find_all('a', href=lambda x: x and '/profil/spieler/' in x)
        
        for link in all_links:
            href = link.get('href', '')
            # Build full URL
            if href.startswith('/'):
                full_url = self.base_url + href
            else:
                full_url = href
            
            # Avoid duplicates and market value links
            if 'marktwertverlauf' not in full_url and full_url not in player_urls:
                player_urls.append(full_url)
        
        print(f"  Found {len(player_urls)} unique player URLs on page {page_num}")
        return player_urls
    
    def parse_market_value(self, value_str):
        """Convert '€75.00m' to 75000000"""
        if not value_str or value_str == '-':
            return None
        
        try:
            # Remove €, spaces, and any other currency symbols
            value_str = value_str.replace('€', '').replace('$', '').replace(' ', '').strip()
            
            # Handle millions
            if 'm' in value_str.lower():
                number = float(value_str.lower().replace('m', ''))
                return int(number * 1_000_000)
            # Handle thousands
            elif 'k' in value_str.lower():
                number = float(value_str.lower().replace('k', ''))
                return int(number * 1_000)
            else:
                return int(float(value_str))
        except:
            return None
    
    def clean_text(self, text):
        """Clean text data"""
        if not text:
            return None
        return text.strip().replace('\n', ' ').replace('\t', ' ')
    
    def scrape_player_details(self, player_url):
        """Scrape individual player page for detailed stats"""
        print(f"  Scraping: {player_url.split('/')[-3]}")
        
        soup = self.get_page(player_url)
        if not soup:
            return None
        
        try:
            player_data = {'url': player_url}
            
            # Player name - try multiple selectors
            name_tag = soup.find('h1', {'class': 'data-header__headline-wrapper'})
            if not name_tag:
                name_tag = soup.find('h1')
            player_data['name'] = self.clean_text(name_tag.get_text()) if name_tag else None
            
            # Find all info rows (they contain spans with labels and values)
            info_table = soup.find('div', {'class': 'info-table'})
            
            if info_table:
                spans = info_table.find_all('span')
                
                # Create a dict of label: value pairs
                info_dict = {}
                for i in range(0, len(spans)-1, 2):
                    label = self.clean_text(spans[i].get_text())
                    value = self.clean_text(spans[i+1].get_text())
                    if label and value:
                        info_dict[label] = value
                
                # Extract specific fields
                for key, value in info_dict.items():
                    if 'age' in key.lower():
                        # Extract just the number from "25 (Feb 21, 1999)"
                        age_match = re.search(r'(\d+)', value)
                        player_data['age'] = int(age_match.group(1)) if age_match else None
                    
                    elif 'position' in key.lower():
                        player_data['position'] = value
                    
                    elif 'citizenship' in key.lower() or 'nationality' in key.lower():
                        player_data['nationality'] = value
                    
                    elif 'current club' in key.lower():
                        player_data['current_club'] = value
                    
                    elif 'contract' in key.lower():
                        player_data['contract_expiry'] = value
                    
                    elif 'height' in key.lower():
                        # Extract just the meters: "1,94 m" -> 1.94
                        height_match = re.search(r'(\d+)[,.](\d+)', value)
                        if height_match:
                            player_data['height_m'] = float(f"{height_match.group(1)}.{height_match.group(2)}")
            
            # Market value - look for the big number
            market_value_tag = soup.find('a', {'class': 'data-header__market-value-wrapper'})
            if market_value_tag:
                value_text = market_value_tag.get_text()
                player_data['market_value'] = self.parse_market_value(value_text)
            
            # Performance stats - find the stats table
            # Look for table with performance data (goals, assists, etc.)
            perf_table = soup.find('table', {'class': 'items'})
            if perf_table:
                # Usually the first data row is current/most recent season
                first_row = perf_table.find('tr', {'class': ['odd', 'even']})
                if first_row:
                    cells = first_row.find_all('td')
                    if len(cells) >= 10:
                        # Typical structure: competition, club, matches, goals, assists, etc.
                        try:
                            player_data['competition'] = self.clean_text(cells[1].get_text())
                            player_data['appearances'] = self.clean_text(cells[3].get_text())
                            
                            # Goals and assists might have extra formatting
                            goals_cell = cells[6].get_text() if len(cells) > 6 else '0'
                            assists_cell = cells[7].get_text() if len(cells) > 7 else '0'
                            minutes_cell = cells[9].get_text() if len(cells) > 9 else '0'
                            
                            player_data['goals'] = self.clean_text(goals_cell)
                            player_data['assists'] = self.clean_text(assists_cell)
                            player_data['minutes_played'] = self.clean_text(minutes_cell)
                        except:
                            pass
            
            return player_data
            
        except Exception as e:
            print(f"    Error parsing player: {e}")
            return None
    
    def scrape_top_players(self, target_count=1000):
        """
        Scrape top players until we hit target count
        Each page has ~25 players, so for 1000 players we need ~40 pages
        """
        print(f"Target: {target_count} players")
        print("=" * 60)
        
        all_player_urls = []
        page = 1
        
        # Step 1: Collect player URLs until we have enough
        while len(all_player_urls) < target_count:
            print(f"\nPage {page}: Collecting player URLs...")
            player_urls = self.scrape_player_list_page(page)
            
            if not player_urls:
                print("No more players found. Stopping.")
                break
            
            all_player_urls.extend(player_urls)
            print(f"Total URLs collected: {len(all_player_urls)}")
            
            page += 1
            
            # Safety limit
            if page > 50:  # ~1250 players max
                print("Reached page limit (50 pages)")
                break
        
        # Trim to target count
        all_player_urls = all_player_urls[:target_count]
        print(f"\n{'='*60}")
        print(f"Collected {len(all_player_urls)} player URLs")
        print(f"Now scraping detailed data...")
        print(f"{'='*60}\n")
        
        # Step 2: Scrape details for each player
        for i, url in enumerate(all_player_urls, 1):
            print(f"[{i}/{len(all_player_urls)}] ", end='')
            
            player_data = self.scrape_player_details(url)
            
            if player_data:
                self.players_data.append(player_data)
            
            # Save progress every 50 players (IMPORTANT!)
            if i % 50 == 0:
                self.save_data(f'players_backup_{i}.csv')
                print(f"\n  >>> Saved backup at {i} players <<<\n")
            
            # Don't hammer the server
            time.sleep(random.uniform(2, 4))
        
        print(f"\n{'='*60}")
        print(f"Scraping complete! Total players: {len(self.players_data)}")
        return self.players_data
    
    def save_data(self, filename='transfermarkt_players.csv'):
        """Save scraped data to CSV"""
        if not self.players_data:
            print("No data to save!")
            return None
        
        df = pd.DataFrame(self.players_data)
        df.to_csv(filename, index=False, encoding='utf-8-sig')  # utf-8-sig for Excel compatibility
        print(f"Saved {len(self.players_data)} players to {filename}")
        return df


# =====================================================
# MAIN EXECUTION
# =====================================================

if __name__ == "__main__":
    scraper = TransfermarktScraper()
    
    # Choose your target (start small to test!)
    # TEST: 50 players (~2-3 minutes)
    # SMALL: 200 players (~10-15 minutes)
    # MEDIUM: 500 players (~30-40 minutes)
    # LARGE: 1000 players (~60-80 minutes)
    
    TARGET = 500  # Change this number
    
    print(f"Starting scrape for {TARGET} players...")
    print("This will take approximately {TARGET * 4 / 60:.0f} minutes")
    print("Press Ctrl+C to stop at any time (progress is auto-saved)\n")
    
    try:
        players = scraper.scrape_top_players(target_count=TARGET)
        
        # Save final data
        df = scraper.save_data('transfermarkt_players_final.csv')
        
        # Show summary
        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total players scraped: {len(df)}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nFirst 5 players:")
        print(df[['name', 'age', 'position', 'market_value', 'goals', 'assists']].head())
        print(f"\nData saved to: transfermarkt_players_final.csv")
        
    except KeyboardInterrupt:
        print("\n\nStopped by user!")
        print("Saving progress...")
        scraper.save_data('transfermarkt_players_interrupted.csv')
        print("You can resume later or use the backup files")