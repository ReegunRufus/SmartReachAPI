import json
import requests

SMARTREACH_API_KEY = 'uk__OAKNwpYC2Me6nLg2vaqM27deEWqc5xzf'
TEAM_ID = 'team_2VnI7aTHSO2SCXk16ithmEsshL1'
CAMPAIGN_ID = 'cmp_aa_2uFb7JcFwjxVEby6qwpc83zXz8t'

def lambda_handler(event, context):
    """AWS Lambda function to add a prospect and assign it to a campaign in SmartReach.io if profile is completed."""

    try:
        # Extract records from payload
        record = event.get("record", {})
        old_record = event.get("old_record", {})

        # Check if basic_profile_completed changed from False to True
        if old_record.get("basic_profile_completed") is False and record.get("basic_profile_completed") is True:
            email = record.get("email")
            full_name = record.get("full_name", "Unknown User").split(" ")

            first_name = full_name[0] if len(full_name) > 0 else "Unknown"
            last_name = " ".join(full_name[1:]) if len(full_name) > 1 else "User"

            if email:
                # Add prospect
                prospect_id = add_prospect(email, first_name, last_name)
                if not prospect_id:
                    return response(500, {'error': 'Failed to add prospect'})

                # Assign to campaign
                if not assign_prospect_to_campaign(prospect_id):
                    return response(500, {'error': 'Failed to assign prospect to campaign'})

                return response(200, {'message': 'Prospect added and assigned to campaign successfully'})

        return response(200, {'message': 'No action taken'})

    except Exception as e:
        print(f"Error: {str(e)}")
        return response(500, {"error": "Internal server error"})

def add_prospect(email, first_name, last_name):
    """Adds a prospect to SmartReach.io and returns the prospect ID."""
    url = f'https://api.smartreach.io/api/v3/prospects?team_id={TEAM_ID}'
    headers = {
        'X-API-KEY': SMARTREACH_API_KEY,
        'Content-Type': 'application/json'
    }
    data = [{
        'email': email,
        'first_name': first_name,
        'last_name': last_name
    }]

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        try:
            prospect = response.json()
            print("Prospect Response:", prospect)  # Debugging: Check the actual response format
            return prospect[0].get('id') if isinstance(prospect, list) else None
        except json.JSONDecodeError:
            print("Error decoding JSON:", response.text)
            return None
    else:
        print(f'Error adding prospect: {response.status_code}, {response.text}')
        return None

def assign_prospect_to_campaign(prospect_id):
    """Assigns a prospect to an email campaign in SmartReach.io."""
    url = f'https://api.smartreach.io/api/v3/campaigns/{CAMPAIGN_ID}/prospects?team_id={TEAM_ID}'
    headers = {
        'X-API-KEY': SMARTREACH_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {'prospect_ids': [prospect_id]}

    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        return True
    else:
        print(f'Error assigning prospect to campaign: {response.status_code}, {response.text}')
        return False

def response(status_code, body):
    """Helper function to format AWS Lambda API Gateway responses."""
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {'Content-Type': 'application/json'}
    }
