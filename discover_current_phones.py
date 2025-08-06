#!/usr/bin/env python3
"""
Script para descobrir automaticamente os phone numbers da BM atual
"""
import os
import requests
import json

def discover_phones():
    token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    if not token:
        print("Token não encontrado")
        return
    
    print(f"Token: {token[:20]}...")
    
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    try:
        # Get user info
        me_response = requests.get("https://graph.facebook.com/v22.0/me", headers=headers)
        print(f"Me response: {me_response.status_code}")
        if me_response.status_code == 200:
            me_data = me_response.json()
            print(f"User ID: {me_data.get('id')}")
            user_id = me_data.get('id')
            
            # Try to get business accounts
            try:
                accounts_response = requests.get(f"https://graph.facebook.com/v22.0/{user_id}?fields=accounts", headers=headers)
                print(f"Accounts response: {accounts_response.status_code}")
                if accounts_response.status_code == 200:
                    accounts_data = accounts_response.json()
                    print(f"Accounts data: {json.dumps(accounts_data, indent=2)}")
            except Exception as e:
                print(f"Error getting accounts: {e}")
            
            # Try known business account IDs
            known_bms = [
                "1523966465251146",  # Michele
                "639849885789886",   # Jose Carlos
                "580318035149016",   # Cleide
                "1779444112928258"   # Maria
            ]
            
            for bm_id in known_bms:
                try:
                    phones_response = requests.get(f"https://graph.facebook.com/v22.0/{bm_id}/phone_numbers", headers=headers)
                    print(f"\nBM {bm_id}: {phones_response.status_code}")
                    if phones_response.status_code == 200:
                        phones_data = phones_response.json()
                        phone_numbers = phones_data.get('data', [])
                        print(f"  Found {len(phone_numbers)} phones:")
                        for phone in phone_numbers:
                            print(f"    - {phone.get('id')} ({phone.get('display_phone_number')})")
                        if phone_numbers:
                            return bm_id, [phone.get('id') for phone in phone_numbers]
                    else:
                        print(f"  Error: {phones_response.text}")
                except Exception as e:
                    print(f"  Exception: {e}")
            
        else:
            print(f"Me error: {me_response.text}")
    
    except Exception as e:
        print(f"General error: {e}")

if __name__ == "__main__":
    result = discover_phones()
    if result:
        bm_id, phones = result
        print(f"\nSUCESSO: BM {bm_id} com {len(phones)} phones:")
        for phone in phones:
            print(f"  - {phone}")