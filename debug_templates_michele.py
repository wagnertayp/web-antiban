#!/usr/bin/env python3
"""
Debug templates da BM Michele
"""
import os
import requests
import json

def debug_templates():
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    bm_id = "1523966465251146"  # Michele
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get templates
        response = requests.get(f"https://graph.facebook.com/v22.0/{bm_id}/message_templates", headers=headers)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            templates = data.get('data', [])
            print(f"Total templates: {len(templates)}")
            
            for template in templates:
                name = template.get('name')
                status = template.get('status')
                language = template.get('language')
                category = template.get('category')
                
                print(f"\nTemplate: {name}")
                print(f"  Status: {status}")
                print(f"  Language: {language}")
                print(f"  Category: {category}")
                
                if status == "APPROVED":
                    print(f"  ✓ APROVADO")
                else:
                    print(f"  ✗ Status: {status}")
                
                # Print full structure
                print(f"  Full: {json.dumps(template, indent=2)}")
        else:
            print(f"Error: {response.text}")
            
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    debug_templates()