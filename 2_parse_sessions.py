import json
import logging
from datetime import datetime, timedelta
from pprint import pprint
import time

from playwright.sync_api import sync_playwright

logging.basicConfig(filename='session_scraping.log', level=logging.ERROR)

BASE_URL = 'https://lps25.esa.int/'
EVENT_INFO_FILE = '2_event_info.json'
    
def scrape_session_info(id, page):

  date_header_el = page.locator("div.date-header")
  if date_header_el.count() == 0:
    print('WARNING: No date-header elements found')
    print(f'{page.inner_html()=}')
    logging.error(f'id={id} No date-header elements found when scraping session info.')
    raise Exception('No date-header elements found when scraping session info.')
  date_str = date_header_el.inner_text()

  time_el = page.locator("div.session-time-column")
  if time_el.count() == 0:
    print('WARNING: No session time found')
    logging.error(f'id={id} No session time found when scraping session info.')
    raise Exception('No session time found when scraping session info.')
  time_str = time_el.inner_text()

  session_container_el = page.locator("div.session-container")
  if session_container_el.count() == 0:
    print('WARNING: No session container found')
    logging.error(f'id={id} No session container found when scraping session info.')
    raise Exception('No session container found when scraping session info.')
  title_str = session_container_el.locator('h4').first.inner_text()

  try:
    type_str = title_str.split(' ', 2)[1]
    if type_str in ['TUTORIAL', 'HANDS-ON', 'DEMO']:
      type = type_str.lower()
    else:
      if 'POSTER' in title_str:
        type = 'poster'
      else:
        type = 'session'
  except IndexError:
    type = 'session'
  except Exception as e:
    print(f'DEBUG error={e}')
    logging.error(f'{e=}')
    logging.error(f"Failed to determine session type for {id}")
    raise Exception('Failed to determine session type when scraping session info.')

  info_box_el = page.locator("div.info-box")
  if info_box_el.count() == 0:
    print('WARNING: No info box found')
    logging.error(f'id={id} No info box found when scraping session info.')
    raise Exception('No info box found when scraping session info.')

  details_els = page.locator("div.details-grid")
  if details_els.count() != 2:
    print('WARNING: Expected 2 details elements')
    logging.error(f'id={id} Expected 2 details elements when scraping session info.')
    raise Exception('Expected 2 details elements when scraping session info.')

  chairs_str = info_box_el.locator("div").nth(0).inner_text().split('\n')[1].strip()
  room_str = info_box_el.locator("div").nth(2).inner_text().split('\n')[1].strip()
  duration_str = info_box_el.locator("div").nth(2).inner_text().split('\n')[3].strip()
  details_str = info_box_el.locator("div.details-grid").nth(1).locator("div").locator("div").nth(0).inner_html()

  date_obj = datetime.strptime(date_str.split('-')[1].strip(), '%d.%m.%Y')
  date_iso = date_obj.strftime('%Y-%m-%d')
  start_datetime = datetime.strptime(f'{date_iso}T{time_str}', '%Y-%m-%dT%H:%M')
  duration_mins = int(duration_str.split()[0])
  end_datetime = start_datetime + timedelta(minutes=duration_mins)

  start_dt_iso = start_datetime.isoformat()
  end_dt_iso = end_datetime.isoformat()

  info_dict = {
    'title': title_str,
    'start': start_dt_iso,
    'end': end_dt_iso,
    'duration': duration_str,
    'chairs': chairs_str,
    'location': room_str,
    'abstract': details_str,
    'type': type,
    'session_id': id
  }

  return info_dict


def process_session(session_event):
  id = session_event['id']
  session_url = f'programme/programme-session?id={id}'
  # print(f'{session_url=}')
  with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    
    page.goto(BASE_URL + session_url, wait_until="networkidle")
    
    session_info_dict = scrape_session_info(id, page)

    presentation_info_dicts = []
    for presentation_el in page.locator('div.presentation-item').all():
      presentation_title_str = presentation_el.locator('h2').inner_text()

      author_els = presentation_el.locator('span.author-name')
      authors = [author_el.inner_text().rsplit(maxsplit=1)[0].strip()
                 for author_el in author_els.all()]
      authors = [author.rstrip(' ,0123456789') for author in authors]

      affiliation_els = presentation_el.locator('span.affiliation-name')
      affiliations = [affiliation_el.inner_text().split('.', 1)[1].strip() for affiliation_el in affiliation_els.all()]

      abstract_el = presentation_el.locator('div.accordion-body')
      assert abstract_el.count() == 1, 'DEBUG: Expected 1 abstract element'
      abstract = abstract_el.inner_text().strip()

      presentation_id = presentation_el.locator('div.collapse').first.get_attribute('id').split('-', 1)[1]

      if session_info_dict['type'] == 'poster':
        type = 'poster'
      else:
        type = 'presentation'

      # Save the presentation info
      presentation_info_dicts.append({
        'title': presentation_title_str,
        'authors': authors,
        'affiliations': affiliations,
        'abstract': abstract,
        'type': type,
        'session_id': id,
        'start': session_info_dict['start'],
        'end': session_info_dict['end'],
        'location': session_info_dict['location'],
        'presentation_id': presentation_id
      })

    return [session_info_dict] + presentation_info_dicts

    
with open('1_crawled_links.json', 'r') as f:
    session_page_links = json.load(f)
try:
  with open(EVENT_INFO_FILE, 'r') as f:
    event_info = json.load(f)
except FileNotFoundError:
  event_info = []

# Get list of session ids that have already been processed
event_ids = [event['session_id'] for event in event_info]

# Get list of sessions that haven't been processed
unprocessed_session_ids = [id for id in session_page_links.keys() 
                       if id not in event_ids]

# Filter session_page_links to only include unprocessed sessions
session_page_links = {id: info for id, info in session_page_links.items() 
                     if id in unprocessed_session_ids}

print(f'{len(session_page_links)} sessions remain unprocessed.')

# # Filter to only process poster sessions
# session_page_links = {id: info for id, info in session_page_links.items() 
#                      if info['event_type'] == 'poster session'}

# # Limit sessions for testing/debugging
# session_page_links = dict(list(session_page_links.items())[:3])

print(f'{len(session_page_links)} will be processed by this run.')

# Process sessions
for id, session_event in session_page_links.items():
  print(f'{id=}')
  print(f'{session_event=}')
  
  try:
    result = process_session(session_event)
  except Exception as e:
    print(f'DEBUG error={e}')
    logging.error(f'{e=}')
    logging.error(f"Failed to process session {session_event['id']}")
    time.sleep(1)
    continue

  event_info.extend(result)

  # Save links to file
  with open(EVENT_INFO_FILE, 'w') as f:
    json.dump(event_info, f, indent=2)

print(f'{len(event_info)} sessions have now been successfully processed')