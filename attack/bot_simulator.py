#!/usr/bin/env python3
import requests
import time
import threading
import random
import argparse
import json
from concurrent.futures import ThreadPoolExecutor

try:
    from fake_useragent import UserAgent
    HAS_FAKE_UA = True
except ImportError:
    HAS_FAKE_UA = False
    print("Warning: fake_useragent package not installed. Using fallback user agents.")
    print("Install with: pip install fake-useragent")

# Fallback user agents if the package isn't installed
FALLBACK_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59"
]

# Global counters
success_counter = 0
failure_counter = 0
lock = threading.Lock()

class BotSimulator:
    def __init__(self, target_url):
        self.target_url = target_url
        self.ua_generator = UserAgent() if HAS_FAKE_UA else None
        self.session = requests.Session()
        
        # API-specific paths for the product reviews system
        self.api_paths = [
            "",  # Main endpoint
            "?product_id=prod1234",
            "?product_id=test",
            "?product_id=xyz123"
        ]
    
    def get_random_user_agent(self):
        """Get a random user agent string"""
        if HAS_FAKE_UA:
            return self.ua_generator.random
        else:
            return random.choice(FALLBACK_USER_AGENTS)
    
    def generate_bot_session(self, bot_type):
        """Create a session with characteristics of the specified bot type"""
        s = requests.Session()
        
        if bot_type == "simple":
            # Simple bot with fixed user agent
            s.headers.update({
                "User-Agent": "Python-urllib/3.8",
                "Accept": "*/*"
            })
        
        elif bot_type == "browser":
            # Bot trying to look like a browser
            s.headers.update({
                "User-Agent": self.get_random_user_agent(),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive"
            })
        
        elif bot_type == "scraper":
            # Typical scraper bot
            s.headers.update({
                "User-Agent": f"WebScraper/1.0 (Custom Scraper; Python/{random.choice(['3.6', '3.7', '3.8', '3.9'])})",
                "Accept": "application/json, text/plain, */*",
                "Accept-Encoding": "gzip, deflate",
            })
            
        elif bot_type == "rotating":
            # Bot that rotates user agents
            pass  # We'll rotate user agents on each request
            
        return s
    
    def generate_review_data(self, index=None):
        """Generate random review data for POST requests"""
        if index is None:
            index = random.randint(1000, 9999)
            
        return {
            "product_id": f"prod{index:04d}",
            "review": f"This is review {index} from bot simulation",
            "username": f"bot_user_{index:04d}"
        }
    
    def simple_bot_behavior(self, num_requests, delay_range=(0.05, 0.2)):
        """Execute simple bot behavior - rapid requests with fixed patterns"""
        global success_counter, failure_counter
        session = self.generate_bot_session("simple")
        
        print(f"Starting simple bot simulation with {num_requests} requests")
        for i in range(num_requests):
            # Randomly choose between GET and POST
            method = random.choice(["GET", "POST"])
            
            if method == "GET":
                path = random.choice(self.api_paths)
                url = f"{self.target_url}{path}"
                
                try:
                    response = session.get(url, timeout=5)
                    print(f"Simple Bot GET {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Simple Bot GET {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
            
            else:  # POST
                url = self.target_url
                data = self.generate_review_data(i)
                
                try:
                    response = session.post(url, json=data, timeout=5)
                    print(f"Simple Bot POST {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Simple Bot POST {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
                    
            time.sleep(random.uniform(*delay_range))
    
    def browser_bot_behavior(self, num_requests, delay_range=(0.5, 2)):
        """Execute browser-like bot behavior with more realistic timing"""
        global success_counter, failure_counter
        session = self.generate_bot_session("browser")
        
        print(f"Starting browser-like bot simulation with {num_requests} requests")
        visited_paths = []
        
        for i in range(num_requests):
            # Sometimes revisit previous paths like a real user might
            if visited_paths and random.random() < 0.3:
                path = random.choice(visited_paths)
            else:
                path = random.choice(self.api_paths)
                visited_paths.append(path)
            
            method = random.choice(["GET", "POST"])
            
            if method == "GET":
                url = f"{self.target_url}{path}"
                
                try:
                    response = session.get(url, timeout=10)
                    print(f"Browser Bot GET {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Browser Bot GET {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
            
            else:  # POST
                url = self.target_url
                data = self.generate_review_data(i)
                
                try:
                    response = session.post(url, json=data, timeout=10)
                    print(f"Browser Bot POST {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Browser Bot POST {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
                
            time.sleep(random.uniform(*delay_range))
    
    def rotating_user_agent_bot(self, num_requests, delay_range=(0.2, 1)):
        """Execute bot behavior that rotates user agents"""
        global success_counter, failure_counter
        print(f"Starting rotating user agent bot simulation with {num_requests} requests")
        
        for i in range(num_requests):
            # Create fresh headers with a new user agent for each request
            headers = {
                "User-Agent": self.get_random_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Content-Type": "application/json"
            }
            
            method = random.choice(["GET", "POST"])
            
            if method == "GET":
                path = random.choice(self.api_paths)
                url = f"{self.target_url}{path}"
                
                try:
                    response = requests.get(url, headers=headers, timeout=5)
                    print(f"Rotating UA Bot GET {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    print(f"  User-Agent: {headers['User-Agent'][:50]}...")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Rotating UA Bot GET {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
            
            else:  # POST
                url = self.target_url
                data = self.generate_review_data(i)
                
                try:
                    response = requests.post(url, json=data, headers=headers, timeout=5)
                    print(f"Rotating UA Bot POST {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    print(f"  User-Agent: {headers['User-Agent'][:50]}...")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Rotating UA Bot POST {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
                
            time.sleep(random.uniform(*delay_range))
    
    def scraper_bot_behavior(self, num_requests, delay_range=(0.1, 0.5)):
        """Execute scraper bot behavior that follows a systematic pattern"""
        global success_counter, failure_counter
        session = self.generate_bot_session("scraper")
        
        print(f"Starting scraper bot simulation with {num_requests} requests")
        
        # Use mostly GET requests, scraping is typically read-heavy
        for i in range(num_requests):
            # 80% chance of GET, 20% chance of POST for scrapers that also submit data
            method = "GET" if random.random() < 0.8 else "POST"
            
            if method == "GET":
                # Systematic approach - go through product IDs sequentially
                path = f"?product_id=prod{i%100:04d}"
                url = f"{self.target_url}{path}"
                
                try:
                    response = session.get(url, timeout=5)
                    print(f"Scraper Bot GET {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Scraper Bot GET {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
            
            else:  # POST
                url = self.target_url
                data = self.generate_review_data(i)
                
                try:
                    response = session.post(url, json=data, timeout=5)
                    print(f"Scraper Bot POST {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Scraper Bot POST {i+1}/{num_requests}: {url} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
                
            time.sleep(random.uniform(*delay_range))
    
    def flood_bot_behavior(self, num_requests, delay_range=(0.01, 0.05)):
        """Execute a flood attack with minimal delays between requests"""
        global success_counter, failure_counter
        session = self.generate_bot_session("simple")
        
        print(f"Starting flood bot simulation with {num_requests} requests")
        
        # Mostly POST requests for flood attack
        for i in range(num_requests):
            url = self.target_url
            data = self.generate_review_data(i)
            
            try:
                response = session.post(url, json=data, timeout=3)
                print(f"Flood Bot POST {i+1}/{num_requests}: {url} - Status: {response.status_code}")
                with lock:
                    success_counter += 1
            except Exception as e:
                print(f"Flood Bot POST {i+1}/{num_requests}: {url} - Error: {str(e)}")
                with lock:
                    failure_counter += 1
            
            time.sleep(random.uniform(*delay_range))
    
    def simulate_botnet(self, bot_types, requests_per_bot=20):
        """Simulate multiple bots attacking simultaneously"""
        global success_counter, failure_counter
        success_counter = 0
        failure_counter = 0
        
        print(f"Starting botnet simulation with {len(bot_types)} bot types")
        start_time = time.time()
        
        bot_functions = {
            "simple": self.simple_bot_behavior,
            "browser": self.browser_bot_behavior,
            "rotating": self.rotating_user_agent_bot,
            "scraper": self.scraper_bot_behavior,
            "flood": self.flood_bot_behavior
        }
        
        threads = []
        
        for bot_type in bot_types:
            if bot_type in bot_functions:
                t = threading.Thread(
                    target=bot_functions[bot_type], 
                    args=(requests_per_bot,)
                )
                threads.append(t)
                print(f"Starting {bot_type} bot thread")
                t.start()
            else:
                print(f"Unknown bot type: {bot_type}")
        
        for t in threads:
            t.join()
        
        elapsed_time = time.time() - start_time
        total_requests = success_counter + failure_counter
        
        print("\nBotnet simulation complete")
        print(f"Total time: {elapsed_time:.2f} seconds")
        print(f"Total requests: {total_requests}")
        print(f"Successful requests: {success_counter}")
        print(f"Failed requests: {failure_counter}")
        print(f"Success rate: {success_counter/total_requests*100:.2f}% if total_requests > 0 else 0")
        print(f"Requests per second: {total_requests/elapsed_time:.2f}")

def simulate_human_traffic(url, num_users=5, requests_per_user=10):
    """Simulate legitimate human traffic patterns"""
    global success_counter, failure_counter
    success_counter = 0
    failure_counter = 0
    
    print(f"Starting human traffic simulation with {num_users} users making {requests_per_user} requests each")
    start_time = time.time()
    
    def human_session(user_id):
        # Create session with realistic headers
        session = requests.Session()
        ua = UserAgent() if HAS_FAKE_UA else None
        user_agent = ua.random if HAS_FAKE_UA else random.choice(FALLBACK_USER_AGENTS)
        
        session.headers.update({
            "User-Agent": user_agent,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.5",
            "Content-Type": "application/json"
        })
        
        # Generate some product IDs this user might be interested in
        product_ids = [f"prod{random.randint(1000, 9999):04d}" for _ in range(3)]
        
        # First action: view products (GET requests)
        for i in range(min(5, requests_per_user)):
            product_id = random.choice(product_ids)
            full_url = f"{url}?product_id={product_id}"
            
            try:
                response = session.get(full_url, timeout=10)
                print(f"Human {user_id} - GET {i+1}/{requests_per_user}: product_id={product_id} - Status: {response.status_code}")
                with lock:
                    success_counter += 1
            except Exception as e:
                print(f"Human {user_id} - GET {i+1}/{requests_per_user}: product_id={product_id} - Error: {str(e)}")
                with lock:
                    failure_counter += 1
                
            # Human-like pause
            time.sleep(random.uniform(2, 8))
        
        # Second action: submit a review (POST request) if we have remaining requests
        if requests_per_user > 5:
            for i in range(5, requests_per_user):
                product_id = random.choice(product_ids)
                
                # Generate review data
                review_data = {
                    "product_id": product_id,
                    "review": f"I really like this product! It's exactly what I needed. User {user_id} review.",
                    "username": f"User{user_id:03d}"
                }
                
                try:
                    response = session.post(url, json=review_data, timeout=10)
                    print(f"Human {user_id} - POST {i+1}/{requests_per_user}: product_id={product_id} - Status: {response.status_code}")
                    with lock:
                        success_counter += 1
                except Exception as e:
                    print(f"Human {user_id} - POST {i+1}/{requests_per_user}: product_id={product_id} - Error: {str(e)}")
                    with lock:
                        failure_counter += 1
                
                # Human-like pause
                time.sleep(random.uniform(5, 15))
        
        print(f"Human {user_id} session complete")
    
    # Launch human sessions in parallel
    with ThreadPoolExecutor(max_workers=num_users) as executor:
        for user_id in range(1, num_users+1):
            executor.submit(human_session, user_id)
    
    elapsed_time = time.time() - start_time
    total_requests = success_counter + failure_counter
    
    print("\nHuman traffic simulation complete")
    print(f"Total time: {elapsed_time:.2f} seconds")
    print(f"Total requests: {total_requests}")
    print(f"Successful requests: {success_counter}")
    print(f"Failed requests: {failure_counter}")
    if total_requests > 0:
        print(f"Success rate: {success_counter/total_requests*100:.2f}%")
    print(f"Requests per second: {total_requests/elapsed_time:.2f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bot Network Simulation Tool for API Gateway")
    parser.add_argument("--url", help="Target URL (will use default endpoints if not provided)")
    parser.add_argument("--mode", required=True, choices=["botnet", "human", "mixed", "flood"], help="Simulation mode")
    parser.add_argument("--protected", action="store_true", help="Use protected API instead of unprotected")
    parser.add_argument("--bot-types", nargs="+", default=["simple", "browser", "rotating", "scraper"], 
                        help="Types of bots to simulate")
    parser.add_argument("--bot-requests", type=int, default=20, help="Requests per bot")
    parser.add_argument("--humans", type=int, default=3, help="Number of human users to simulate")
    parser.add_argument("--human-requests", type=int, default=10, help="Requests per human user")
    parser.add_argument("--duration", type=int, default=60, help="Maximum duration in seconds")
    
    args = parser.parse_args()
    
    # Default API endpoints
    unprotected_api = "https://ej8w9qp45k.execute-api.us-east-1.amazonaws.com/demo/reviews"
    protected_api = "https://vpra7ju8ka.execute-api.us-east-1.amazonaws.com/demo/reviews"
    
    # Set target URL based on args
    if args.url:
        target_url = args.url
    else:
        target_url = protected_api if args.protected else unprotected_api
    
    print(f"Starting API simulation against {target_url}")
    print(f"Mode: {args.mode}")
    print(f"API Type: {'Protected' if args.protected else 'Unprotected'}")
    print("Press Ctrl+C to abort\n")
    
    # Start a timer to limit total runtime
    max_duration = args.duration
    start_time = time.time()
    
    try:
        # Set up a timer to enforce maximum duration
        timer = threading.Timer(max_duration, lambda: print(f"\nMaximum duration of {max_duration}s reached. Exiting...") or exit(0))
        timer.daemon = True
        timer.start()
        
        if args.mode == "flood" or (args.mode == "botnet" and "flood" in args.bot_types):
            if "flood" not in args.bot_types:
                args.bot_types.append("flood")
            bot_sim = BotSimulator(target_url)
            bot_sim.simulate_botnet(args.bot_types, args.bot_requests)
        elif args.mode == "botnet":
            bot_sim = BotSimulator(target_url)
            bot_sim.simulate_botnet(args.bot_types, args.bot_requests)
        elif args.mode == "human":
            simulate_human_traffic(target_url, args.humans, args.human_requests)
        elif args.mode == "mixed":
            # Start human traffic in a separate thread
            human_thread = threading.Thread(
                target=simulate_human_traffic,
                args=(target_url, args.humans, args.human_requests)
            )
            human_thread.daemon = True
            human_thread.start()
            
            # Start botnet simulation
            bot_sim = BotSimulator(target_url)
            bot_sim.simulate_botnet(args.bot_types, args.bot_requests)
            
            # Wait for human thread to complete
            human_thread.join()
            
        # Cancel the timer if we complete before the max duration
        timer.cancel()
            
    except KeyboardInterrupt:
        print("\nSimulation aborted by user")