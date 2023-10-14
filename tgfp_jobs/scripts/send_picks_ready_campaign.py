""" Used to send out the picks page is ready campaign email """
import httpx
from prefect import flow
from config import get_config

config = get_config()


@flow
def send_campaign_email(week_no: int):
    """ Send a 'picks page is ready email"""
    auth_hash = config.LISTMONK_AUTH_HASH
    campaign_id = _create_campaign(week_no)

    url = config.LISTMONK_API_URL + f"campaigns/{campaign_id}/status"
    data = {"status": "running"}
    headers = {
        "Authorization": f"Basic {auth_hash}",
        "Content-Type": "application/json; charset=utf-8",
    }
    httpx.put(url=url, json=data, headers=headers)


def _create_campaign(week_no) -> int:
    """
    Creates the listmonk campaign
    @return: int ID of the campaign
    """
    auth_hash = config.LISTMONK_AUTH_HASH
    list_id: int = int(config.LISTMONK_LIST_ID)
    url = config.LISTMONK_API_URL + 'campaigns'
    data = {
        "lists": [
            list_id
        ],
        "subject": f"Picks Page is READY for week {week_no}",
        "template_id": 5,
        "type": "regular",
        "body": f"The Picks page is ready for week {week_no}",
        "name": f"Picks Page is READY for week {week_no}",
        "content_type": "richtext"
    }
    headers = {
        "Authorization": f"Basic {auth_hash}",
        "Content-Type": "application/json; charset=utf-8",
    }
    result = httpx.post(url=url, json=data, headers=headers)
    json_result = result.json()
    return json_result['data']['id']


if __name__ == '__main__':
    send_campaign_email(6)
