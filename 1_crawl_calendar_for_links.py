from datetime import datetime
from playwright.sync_api import sync_playwright
import json

def process_modal_content(page):
    content_el = page.locator('div.modal-content')
    title_el = content_el.locator('h5.modal-title')
    title_str = title_el.inner_text()
    print(f'Processing session modal: {title_str}')

    # Get the details link.
    link_obj = page.locator("div.modal-footer").locator("a")
    href = link_obj.get_attribute("href")    
    id = href.split("id=")[1]

    # close the modal
    page.locator("a.close").click()

    # id = href.split("id=")[1]
    session_info = {
        'id': id,
        'title': title_str,
    }
    return session_info

def crawl(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()        
        page.goto(url, wait_until="networkidle")
    
        tabs = [
            '22 June',
            '23 June',
            '24 June',
            '25 June',
            '26 June',
            '27 June',
        ]

        events = {}
        for tab_text in tabs:
            print(f'{tab_text=}')
            button = page.locator('button', has_text=tab_text)
            button.click()

            # Wait for the calendar information to load
            page.wait_for_selector("div.time-header")

            event_elements = page.locator("div.event").all()
            print(f'{len(event_elements)=}')
            
            for event_element in event_elements:
                event_element.click() # Open the event details

                poster_session_info = page.locator('div.poster-session-container')
                session_info = page.locator('div.session-modal')

                if poster_session_info.count() > 0:
                    print('Processing poster sessions page')
                    poster_sessions = poster_session_info.locator("div.poster-session").all()
                    print(f'{len(poster_sessions)=}')
                    for poster_session in poster_sessions:
                        poster_session.click()
                        session_info = process_modal_content(page)
                        session_info['event_type'] = 'poster session'
                        events[session_info['id']] = session_info

                    # Close the modal displaying the poster sessions
                    close_button = page.locator("a.back-to-agenda")
                    if close_button.count() > 0:
                        close_button.first.click()
                    else:
                        print('DEBUG no close button')

                elif session_info.count() > 0:
                    # print('Processing session page')
                    session_info = process_modal_content(page)
                    session_info['event_type'] = 'session'
                    events[session_info['id']] = session_info
                else:
                    print('WARNING Session not recognized!')

        browser.close()
        return events

test = crawl("https://lps25.esa.int/programme/")

# Save links to file
with open('1_crawled_links.json', 'w') as f:
    json.dump(test, f, indent=2)
