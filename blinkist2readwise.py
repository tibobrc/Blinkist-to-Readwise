import blinkist_scraper as bs
import readwise_util as ru
import sys
import time
import argparse
from functools import partial

parser = argparse.ArgumentParser()
# Required positional argument, for capturing the email address used to log in to the
# Blinkist account
parser.add_argument(
    "blinkist_email",
    help="specify the email address used to log in to your Blinkist account"
)
# Required positional argument, for capturing the password used to log in to the
# Blinkist account
parser.add_argument(
    "blinkist_password",
    help="specify the password used to log in to your Blinkist account"
)
# Optional argument, used to download all Blinkist highlights into a CSV file
parser.add_argument(
    "-d",
    "--download",
    help="download all Blinkist highlights into a CSV file",
    action="store_true"
)
# Optional argument, used to show the Chrome window while extracting Blinkist highlights
# with Selenium
parser.add_argument(
    "-s",
    "--show-chrome",
    help="show the Chrome window while extracting Blinkist highlights",
    action="store_true"
)
# Optional argument, used to specify the token used to interact with the user's
# Readwise highlights
parser.add_argument(
    "-t",
    "--token-readwise",
    help="specify the token used to access your Readwise highlights"
)
args = parser.parse_args()

BLINKIST_EMAIL = args.blinkist_email
BLINKIST_PASSWORD = args.blinkist_password
READWISE_TOKEN = args.token_readwise
#Download the CSV if the option is passed or if no Readwise token is passed
DOWNLOAD_CSV = args.download or (READWISE_TOKEN is None)
SHOW_CHROME = args.show_chrome

# First, we load the current user's Readwise highlights, if the token was provided.
# We will use this information to check if highlights found on the Blinkist
# page are already saved on Readwise, and thus to know if we need to load
# more ancient highlights or not
readwise_highlights = None
if READWISE_TOKEN is not None:
    print('Fetching current Readwise highlights...')
    readwise_highlights = ru.get_all_readwise_highlights(READWISE_TOKEN)
    if readwise_highlights is None:
        sys.exit('Script interrupted due to error.')


def should_keep_loading(readwise_highlights, download_csv, blinkist_highlights):
    # Function to know if more highlights from the Blinkist website need to be
    # loaded.
    # If the user chooses to download the CSV, then this function will always return True
    # and all highlights will be extracted.
    # If the user hasn't chosen to download the CSV, then this function checks if the most
    # ancient highlight that can currently be seen on the Blinkist page is already saved
    # in Readwise
    if download_csv:
        return True
    already_saved = False
    oldest_blinkist_highlight = blinkist_highlights[len(
        blinkist_highlights) - 1]['highlight']
    for highlight in readwise_highlights:
        if highlight['text'].strip() == oldest_blinkist_highlight.strip():
            already_saved = True
            break
    return not already_saved


def get_highlight_object(fetched_object):
    # Function to prepare the highlight objects that will be uploaded to Readwise
    return {
        'text': fetched_object['highlight'],
        'title': fetched_object['book_title'],
        'image_url': 'https://upload.wikimedia.org/wikipedia/en/c/ca/Blinkist_logo.png',
        'source_type': 'book',
        'author': 'Blinkist'
    }


# Fetch the Blinkist highlights
fetched_highlights = bs.extract_blinkist_highlights(
    BLINKIST_EMAIL,
    BLINKIST_PASSWORD,
    partial(should_keep_loading, readwise_highlights, DOWNLOAD_CSV),
    DOWNLOAD_CSV,
    SHOW_CHROME
)
if fetched_highlights is None:
    sys.exit('Script interrupted due to error.')

if READWISE_TOKEN is not None:
    # Prepare a new list of highlight objects from our previously fetched and sorted results
    highlight_objects = []
    fetched_highlights.reverse()  # reverse list to get oldest highlights first
    for highlight in fetched_highlights:
        highlight_objects.append(get_highlight_object(highlight))

    # Upload the highlights to Readwise
    api_response = ru.export_highlights_to_readwise(
        READWISE_TOKEN, highlight_objects)

    if api_response.status_code != 200:
        sys.exit('Script interrupted due to error.')
    else:
        print("Success: Blinkist highlights uploaded to Readwise!")
else:
    print("Success: Blinkist highlights extracted to a CSV file!")