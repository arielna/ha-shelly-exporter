#!/usr/bin/env python3
"""
Export Shelly switch entities from Home Assistant to a CSV file.
Simple version that only exports device ID and name.
"""

import csv
import os
import argparse
import sys
from datetime import datetime

# Check for required modules
missing_modules = []
try:
    import requests
except ImportError:
    missing_modules.append("requests")

try:
    from dotenv import load_dotenv
except ImportError:
    missing_modules.append("python-dotenv")

# If modules are missing, provide instructions
if missing_modules:
    print("ERROR: Missing required Python modules:", ", ".join(missing_modules))
    print("\nTo install the missing modules, run the following command:")
    print(f"pip install {' '.join(missing_modules)}")
    print("\nIf you have multiple Python versions installed, you might need to use:")
    print(f"pip3 install {' '.join(missing_modules)}")
    sys.exit(1)

def get_shelly_devices(ha_url, token):
    """Get Shelly device entities from Home Assistant API"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    
    # Ensure URL doesn't end with a slash
    if ha_url.endswith('/'):
        ha_url = ha_url[:-1]
    
    # Check if API is accessible
    config_url = f"{ha_url}/api/config"
    print(f"Testing API connection at: {config_url}")
    
    try:
        # Check if API is accessible
        config_response = requests.get(config_url, headers=headers, timeout=30)
        if config_response.status_code != 200:
            print(f"Error: Unable to access Home Assistant API. Status code: {config_response.status_code}")
            print("This suggests a problem with authentication or the API is not accessible.")
            return []
        else:
            print("Successfully connected to Home Assistant API")
        
        # Get all entities from states endpoint
        states_url = f"{ha_url}/api/states"
        print(f"Getting entities from: {states_url}")
        states_response = requests.get(states_url, headers=headers, timeout=30)
        
        if states_response.status_code != 200:
            print(f"Error: Unable to get states. Status code: {states_response.status_code}")
            return []
            
        all_entities = states_response.json()
        print(f"Retrieved {len(all_entities)} total entities from Home Assistant")
        
        # Filter for Shelly device entities
        shelly_devices = []
        seen_ids = set()  # To prevent duplicates
        
        # Process switch entities
        for entity in all_entities:
            entity_id = entity.get("entity_id", "")
            attributes = entity.get("attributes", {})
            friendly_name = attributes.get("friendly_name", entity_id)
            
            # Only process switch or cover entities
            # User requested: All covers, but only Shelly switches
            is_switch = entity_id.startswith("switch.") and "shelly" in entity_id.lower()
            is_cover = entity_id.startswith("cover.")
            is_availability = "availability" in entity_id.lower() or "connectivity" in entity_id.lower()
            
            if (is_switch or is_cover) and not is_availability:
                # Check if this is a duplicate
                if entity_id not in seen_ids:
                    seen_ids.add(entity_id)
                    print(f"Found Shelly device: {entity_id} ({friendly_name})")
                    
                    shelly_devices.append({
                        "id": entity_id,
                        "name": friendly_name
                    })
        
        print(f"\nFound {len(shelly_devices)} unique Shelly device entities")
        return shelly_devices
    
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")
        return []
    except ValueError as e:
        print(f"JSON parsing error: {e}")
        return []
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return []

def export_to_csv(entities, output_file=None):
    """Export the entities list to a CSV file"""
    if not entities:
        print("No Shelly device entities to export. CSV file will not be created.")
        return None
        
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"shelly_devices_{timestamp}.csv"
    
    # Print current working directory for debugging
    print(f"Current working directory: {os.getcwd()}")
    print(f"Attempting to create file: {output_file}")
    
    try:
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['id', 'name']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for entity in entities:
                writer.writerow(entity)
        
        print(f"Successfully exported {len(entities)} Shelly device entities to {output_file}")
        # Check if file exists after writing
        if os.path.exists(output_file):
            print(f"Verified: File exists at {os.path.abspath(output_file)}")
        else:
            print(f"Warning: File was written but cannot be found at {os.path.abspath(output_file)}")
    except PermissionError:
        print(f"ERROR: Permission denied when writing to {output_file}")
        print("Try specifying a different output location or run with administrator privileges")
        return None
    except Exception as e:
        print(f"Error writing to CSV file: {e}")
        return None
        
    return output_file

def main():
    parser = argparse.ArgumentParser(description='Export Shelly device entities from Home Assistant to CSV')
    parser.add_argument('--url', required=False, help='Home Assistant URL (e.g., http://homeassistant.local:8123) (can also be set via HA_URL env var)')
    parser.add_argument('--token', required=False, help='Long-lived access token for Home Assistant (can also be set via HA_TOKEN env var)')
    parser.add_argument('--output', help='Output CSV file path (default: shelly_devices_<timestamp>.csv)')
    
    # Load environment variables
    load_dotenv()
    
    args = parser.parse_args()
    
    # Get configuration from args or environment
    token = args.token or os.getenv('HA_TOKEN')
    ha_url = args.url or os.getenv('HA_URL')
    
    if not ha_url:
        print("Error: Home Assistant URL not provided. Please provide it via --url argument or HA_URL in .env file")
        sys.exit(1)
        
    if not token:
        print("Error: Token not provided. Please provide it via --token argument or HA_TOKEN in .env file")
        sys.exit(1)
    
    print("=" * 50)
    print("Home Assistant Shelly Device Entity Export Tool")
    print("=" * 50)
    print(f"Home Assistant URL: {ha_url}")
    print(f"Token provided: {'Yes (length: ' + str(len(token)) + ' characters)' if token else 'No'}")
    print(f"Output file: {args.output if args.output else 'Auto-generated filename'}")
    
    try:
        print("\nFetching Shelly device entities from Home Assistant...")
        entities = get_shelly_devices(ha_url, token)
        
        if not entities:
            print("\nNo Shelly device entities found. Please check:")
            print("1. Your Home Assistant instance is running")
            print("2. Your token has the necessary permissions")
            print("3. You have Shelly devices configured in Home Assistant")
            print("4. The URL is correct and accessible")
            return
        
        output_file = export_to_csv(entities, args.output)
        
        if output_file:
            print("\nExport Summary:")
            print(f"- Successfully exported {len(entities)} Shelly device entities")
            print(f"- CSV file location: {os.path.abspath(output_file)}")
            print("\nCSV file contents preview:")
            print("-" * 60)
            try:
                with open(output_file, 'r') as f:
                    lines = f.readlines()[:min(6, len(entities) + 1)]  # Header + up to 5 entities
                    for line in lines:
                        print(line.strip())
                if len(entities) > 5:
                    print(f"... and {len(entities) - 5} more switch entities")
                print("-" * 60)
            except Exception as e:
                print(f"Could not read file for preview: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
        print("\nPlease check your connection and try again.")

if __name__ == "__main__":
    main()