# -*- coding: utf-8 -*-
"""Module used to import and export Readwise highlights.
"""

import requests
import time


def get_all_readwise_highlights(readwise_token):
    """ Returns a list of json objects corresponding to highlights extracted from the Readwise website.

    The function takes 1 parameter, which is the token used for accessing the user's Readwise highlights
    through the Readwise API.
    """

    all_current_readwise_highlights = []
    get_url = "https://readwise.io/api/v2/highlights/"
    # Use a loop to load more highlights in case not all highlights were returned.
    while get_url is not None:
        api_response = requests.get(
            url=get_url,
            headers={"Authorization": "Token " + readwise_token},
            params={
                'page_size': 1000
            }
        )
        if api_response.status_code != 200:
            print("Error: Extract of highlights from Readwise failed with status code " +
                  str(api_response.status_code) + '. Please check that the provided Readwise token is correct.')
            return None
        data = api_response.json()
        get_url = data['next']
        all_current_readwise_highlights = all_current_readwise_highlights + \
            data['results']
        time.sleep(5)
    return all_current_readwise_highlights


def export_highlights_to_readwise(readwise_token, highlight_objects):
    """ Submits highlights to Readwise via their API and return the API response.

    The function takes 2 parameters:
    - readwise_token: the token used for accessing the user's Readwise highlights through the Readwise API.
    - highlight_objects: a list of json objects containing the highlights details.
    """
    print('Uploading highlights to Readwise...')
    api_response = requests.post(
        url='https://readwise.io/api/v2/highlights/',
        headers={'Authorization': 'Token ' + readwise_token},
        json={
            'highlights': highlight_objects
        }
    )
    if api_response.status_code != 200:
        print("Error: Upload of highlights to Readwise failed with status code " +
              str(api_response.status_code) + '. Please check that the provided Readwise token is correct.')
        return api_response

    return api_response
