import requests
import json

def create_notion_database(page_id, notion_token):
    """
    Creates a new database in Notion with the specified schema
    
    Args:
        page_id (str): The ID of the parent page where database will be created
        notion_token (str): Your Notion integration token
    """
    url = "https://api.notion.com/v1/databases"
    
    headers = {
        "Authorization": f"Bearer {notion_token}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28"
    }
    
    data = {
        "parent": {
            "type": "page_id",
            "page_id": page_id
        },
        "title": [
            {
                "type": "text",
                "text": {
                    "content": "Task Management"
                }
            }
        ],
        "properties": {
            "Name": {
                "title": {}
            },
            "Description": {
                "rich_text": {}
            },
            "Assignee": {
                "people": {}
            },
            "Due Date": {
                "date": {}
            },
            "Priority": {
                "select": {
                    "options": [
                        {"name": "Low", "color": "blue"},
                        {"name": "Medium", "color": "yellow"},
                        {"name": "High", "color": "red"}
                    ]
                }
            },
            "Tags": {
                "multi_select": {
                    "options": []
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "Not Started", "color": "gray"},
                        {"name": "In Progress", "color": "yellow"},
                        {"name": "Completed", "color": "green"}
                    ]
                }
            }
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print("Database created successfully!")
        return response.json()
    else:
        print(f"Error creating database: {response.status_code}")
        print(response.text)
        return None

# Usage example:

NOTION_TOKEN = "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"
PAGE_ID = "19490634f00280d7a621d5b5a247dc7d"
result = create_notion_database(PAGE_ID, NOTION_TOKEN)
