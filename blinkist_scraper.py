# -*- coding: utf-8 -*-
"""Module used to extract highlights from the Blinkist website.

The functions in this module rely on the Selenium and BeautifoulSoup packages to navigate
the Blinkist website, logging in using the credentials provided and extracting the highlights.
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
import os


def extract_blinkist_highlights(blinkist_email, blinkist_password, should_keep_loading, save_csv, show_chrome):
    """ Returns a list of json objects corresponding to highlights extracted from the Blinkist website.

    The function takes 5 parameters:
    - blinkist_email: The email used to log in to the Blinkist account.
    - blinkist_password: The password used to log in to the Blinkist account.
    - should_keep_loading: A function, which takes the results fetched from the Blinkist website and returns a boolean 
    to indicate if more highlights need to be loaded on the webpage.
    - save_csv: A boolean that indicates if a CSV file containing all the Blinkist highlights
    should be created and saved.
    - show_chrome: A boolean that indicates is the Chrome window should be visible while extracting
    information from the Blinkist website.
    """

    # Prepare the webdriver to scrape Blinkist highlights
    options = Options()
    options.add_argument(
        'user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36')

    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--incognito")
    if not show_chrome:  # hide the window if the user didn't choose to see it
        options.add_argument("--headless")
    options.add_argument("window-size=1024,768")
    driver = webdriver.Chrome(options=options)
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'})
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    # Load the Blinkist login page
    print('Opening the Blinkist webpage...')
    url = 'https://www.blinkist.com/en/nc/login?last_page_before_login=%2Fen%2Fnc%2Fhighlights'
    driver.get(url)
    time.sleep(5)

    # Allow cookies if prompted
    try:
        found_cookies = driver.find_elements_by_class_name(
            'cookie-disclaimer__cta')
        if len(found_cookies) > 0:
            found_cookies[0].click()
            time.sleep(5)
    except NoSuchElementException:
        pass

    # Enter Blinkist login and password, click login button
    print('Logging in into Blinkist...')
    try:
        email_field = driver.find_element_by_name('login[email]')
        password_field = driver.find_element_by_name('login[password]')
        submit_button = driver.find_element_by_name('commit')
    except NoSuchElementException:
        print('Error: Could not find all required fields on the Blinkist login page.')
        return None

    email_field.send_keys(blinkist_email)
    time.sleep(2)
    password_field.send_keys(blinkist_password)
    time.sleep(2)
    submit_button.click()
    time.sleep(5)

    # Throw an error if the login failed (the page did not change)
    if driver.current_url == url:
        print('Error: Blinkist login failed. Please check your credentials.')
        return None

    # Order highlights by date (most recent ones first)
    driver.find_elements_by_css_selector("a[data-order-by='date']")[0].click()
    time.sleep(5)

    def extract_highlights(driver):
        # Function to extract all highlights that can be seen on the Blinkist page

        # First, create a "soup" from the page content to parse it
        soup = BeautifulSoup(driver.page_source, 'lxml')

        # Define the CSS selectors for the fields that interest us (book title, chapter and highlight)
        tag_name = 'div'
        class_name_book_title = 'text-markersV2__items__item__subheadline'
        class_name_highlight = 'text-markersV2__items__item__highlight__text'
        class_name_chapter = 'text-markersV2__items__item__highlight__chapter'
        all_css_selectors = ', '.join(
            map(lambda s: tag_name + '.' + s, [class_name_book_title, class_name_highlight, class_name_chapter]
                )
        )

        # Fetch the fields that interest us
        fetched_results = []
        book_title = ''
        highlight = ''
        chapter = ''
        try:
            selected_tags = soup.select(all_css_selectors)
            if len(selected_tags) == 0:
                print(
                    'Error: Could not find all required fields on the Blinkist highlights page.')
                return None
        except NoSuchElementException:
            print(
                'Error: Could not find all required fields on the Blinkist highlights page.')
            return None

        for tag in selected_tags:
            if(class_name_book_title in tag.attrs['class']):
                book_title = tag.text
            elif(class_name_highlight in tag.attrs['class']):
                highlight = tag.text
            else:
                chapter = tag.text
                fetched_results.append({
                    'book_title': book_title,
                    'chapter': chapter,
                    'highlight': highlight
                })
        return fetched_results

    # Extract the highlights from the Blinkist page
    print('Extracting Blinkist highlights...')
    fetched_results = extract_highlights(driver)
    if fetched_results is None:
        return None

    # Loop to keep loading more highlights as long as the oldest visible highlight
    # in Blinkist is not already saved in Readwise
    keep_loading = should_keep_loading(fetched_results)
    while keep_loading:
        try:
            found_buttons = driver.find_elements_by_css_selector(
                'a.text-markersV2__load-more[style="display: block;"')
            if len(found_buttons) > 0:
                # Click on the load button to load more highlights, if any
                found_buttons[0].click()
                time.sleep(5)
                # Extract visible highlights again
                fetched_results = extract_highlights(driver)
                # Check if the oldest visible highlight is already saved
                keep_loading = should_keep_loading(fetched_results)
            else:
                keep_loading = False
        except NoSuchElementException:
            keep_loading = False

    # Close the webdriver now that we have fetched all required highlights
    driver.quit()

    # Save the highlights into a CSV if the user chose this option
    if save_csv:
        print('Saving Blinkist highlights to a CSV file...')
        with open('blinkist_highlights.csv', 'w') as f:
            f.writelines('Highlight,Title\n')
            for i in range(len(fetched_results)-1, 0, -1):
                book = fetched_results[i]['book_title']
                highlight = fetched_results[i]['highlight']
                f.writelines('"' + highlight + '","' + book +
                             '"' + ('\n' if i > 0 else ''))

    return fetched_results
