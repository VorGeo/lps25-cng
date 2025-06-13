import datetime
import json
from pprint import pprint
import re
import pandas as pd
from IPython.display import HTML

dt_format = "%A, %B %d, %Y %H:%M"
BASE_URL = 'https://lps25.esa.int/'

class Events:
  def __init__(self, event_info_file):
    with open(event_info_file, 'r') as f:
      self.event_info = json.load(f)

  def get_event_info(self):
    return self.event_info

  def head(self, n=5):
    return self.event_info[:n]

  def count(self):
    return len(self.event_info)

  def set_tags(self, search_terms):
    for event in self.event_info:
      if 'tags' in event:
        tag_set = set(event['tags'])
      else:
        tag_set = set()
      for search_term in search_terms:
        if (
          (re.search(f'{search_term['term']}', event['title'], re.IGNORECASE) is not None)
          or ('abstract' in event and
              re.search(f'{search_term['term']}', event['abstract'], re.IGNORECASE) is not None)
          or ('authors' in event and 
              re.search(f'{search_term['term']}', ', '.join(event['authors']), re.IGNORECASE) is not None)
          or ('affiliations' in event and 
              re.search(f'{search_term['term']}', ', '.join(event['affiliations']), re.IGNORECASE) is not None)
        ):
          tag_set.add(search_term['tag'])
      event['tags'] = list(tag_set)  # Convert to list to support serialization

      # Highlight tagged words in abstract
      if 'abstract' in event and 'tags' in event and event['tags']:
        abstract = event['abstract']
        for search_term in search_terms:
          pattern = search_term['term']
          tag = search_term['tag']
          abstract = re.sub(
            f'({pattern})', 
            r'<span class="text-success">\1</span>',
            abstract,
            flags=re.IGNORECASE
          )
        event['abstract'] = abstract
    return self

  def filter_to_tagged_events(self, search_terms):
    self.set_tags(search_terms)

    tagged_events = [event for event in self.event_info if len(event['tags']) > 0]
    self.event_info = tagged_events
    return self

  def filter(self, filter_func):
    return [event for event in self.event_info if filter_func(event)]

  def add_event_dict(self, event_dict):
    self.event_info.append(event_dict)
  
  def as_dataframe(self):
    items = self.event_info
    for item in items:
      item['start_dt'] = datetime.datetime.fromisoformat(item['start'])
      item['end_dt'] = datetime.datetime.fromisoformat(item['end'])
    df = pd.DataFrame(items)
    # try:
    #   df.sort_values(by='start_dt', inplace=True)
    # except KeyError: # this occurs when there are no records
    #   pass
    return df


def get_lps25_events():
  """Return a list of LPS25 events as a dataframe."""
  event_info_json = '2_event_info.json'
  events_lps25 = Events(event_info_json)

  # Add manual events that are not on the LPS25 website
  events_lps25.add_event_dict({
    "title": "Cloud-native Geospatial Community Social.<br/>Register to attend <a href='https://lu.ma/56jksm3l?tk=LJtRja'>here</a>",
    "start": "2025-06-25T17:00:00",
    "end": "2025-06-25T19:00:00",
    "duration": "120 Minutes",
    "location": "Schweizerhaus, Prater 116",
    "abstract": "Socialize with other members of the Cloud-Native Geospatial community. ",
    "type": "social",
  })
  events_lps25.add_event_dict({
    "title": "Earth Engine User Meetup<br/>Register to attend <a href='https://www.tickettailor.com/events/thrivegeo/1694427'>here</a>",
    "start": "2025-06-23T18:00:00",
    "end": "2025-06-23T19:30:00",
    "duration": "90 Minutes",
    "location": "Arcotel Kaiserwasser, 1220",
    "abstract": "Join us for an evening of networking opportunities with fellow Earth Engine enthusiasts who are attending the Living Planet Symposium.<br/><br/>Whether you're a beginner or an advanced user, this event is perfect for anyone looking to connect with like-minded individuals and learn from experts in the field.",
    "type": "social",
  })

  return events_lps25


def display_info_html():
  return HTML(f"""
      <div class="alert alert-dismissible alert-success">
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        <p>
        The following is a list of events at the
        <a href='https://lps25.esa.int/'>2025 ESA Living Planet Symposium</a>
        that involve cloud-native geospatial technologies.
        </p>
      </div>
    """)

def display_footer_html():
  return HTML(f"""
      <div class="alert alert-dismissible alert-success">
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      <p>
        Of course, some events may have been missed while compiling this list.
        If you know of other LPS events involving CNG, please create a 
        <a href='https://github.com/VorGeo/lps25-cng/issues/new'>new issue</a>
        describing the event
        and/or add the event yourself
        (i.e. 
        <a href='https://github.com/VorGeo/lps25-cng/edit/main/index.qmd'>edit this page</a>, add a new event 'item', and then submit a PR).
        </p>
      </div>
    """)

def create_event_html(row, show_abstract=False, show_id=False):
  desc = f'{row.title}' if isinstance(row.title, str) else ''
  if isinstance(row.session_id, str):
    event_url = f'{BASE_URL}programme/programme-session/?id={row.session_id}'
    event_title_html = f'<a href="{event_url}" class="card-link">{desc}</a>'
  else:
    event_url = ''
    event_title_html = desc
  if isinstance(row.authors, list):
    authors_str = 'Author(s): ' + ', '.join(row.authors) + '<br/>'
  else:
    authors_str = ''
  if isinstance(row.affiliations, list):
    affiliations_str = 'Affiliation(s): ' + ', '.join(row.affiliations) + '<br/>'
  else:
    affiliations_str = ''
  if isinstance(row.tags, list):
    tag_str = ' '.join(['#' + tag for tag in row.tags])
  else:
    tag_str = ''
  location = f'({row.location})' if pd.notna(row.location) else ''

  calendar_daterange = f"{row.start_dt.strftime('%Y%m%dT%H%M%S%z')}/{row.end_dt.strftime('%Y%m%dT%H%M%S%z')}"
  calendar_url = (
    f"https://calendar.google.com/calendar/render?action=TEMPLATE"
    f"&text=[{row.type.title()}] {row.title}"
    f"&dates={calendar_daterange}"
    f"&ctz=Europe/Vienna"
    f"&details={authors_str}{affiliations_str}LPS Website link: <a href='{event_url}'>{row.title}</a>"
    f"&location={row.location.replace(' ', '+')}"
  )

  match row.type.title():
    case 'Session':
      type_span_class = 'badge bg-info'
    case 'Presentation':
      type_span_class = 'badge bg-info disabled'
    case 'Poster':
      type_span_class = 'badge bg-info disabled'
    case 'Hands-On':
      type_span_class = 'badge bg-warning'
    case 'Tutorial':
      type_span_class = 'badge bg-warning disabled'
    case 'Demo':
      type_span_class = 'badge bg-warning'
    case 'Social':
      type_span_class = 'badge bg-danger'
    case _:
      type_span_class = 'badge bg-light'

  # print(f"{row = }")

  return HTML(f"""
    <div class="card border-primary mb-3">
      <div class="card-header">
        {row.start_dt.strftime("%A %d %B")}
        {row.start_dt.strftime("%H:%M")} - {row.end_dt.strftime("%H:%M")}
        {location}
      </div>
      <div class="card-body">
        <h4 class="card-title"><span class="{type_span_class}">{row.type.title()}:</span> {event_title_html}</h4>
        <p class="card-text">
          {'<span class="text-success">{tag_str}</span><br/>' if tag_str else ''}
          {'<div class="alert alert-dismissible alert-light"><b>Chairs:</b> ' + ', '.join(row.chairs) + '</div>' if isinstance(row.chairs, list) else ''}
          {'<div class="alert alert-dismissible alert-light"><b>Authors:</b> ' + ', '.join(row.authors) + '</div>' if isinstance(row.authors, list) else ''}
          {'<div class="alert alert-dismissible alert-light"><b>Affiliations:</b> ' + ', '.join(row.affiliations) + '</div>' if isinstance(row.affiliations, list) else ''}
          {'<div class="alert alert-dismissible alert-light">' + row.abstract + '</div>' if isinstance(row.abstract, str) else ''}
          <a href="{calendar_url}" class="text-info" target="_blank">Add to Google Calendar</a>
          </p>
        </p>
      </div>
    </div>
  """)





##### testing
# event_info = Events('2_event_info.json')
# event_info.set_tags([
#   {'term': r'\bcloud-native|cloud native\b', 'tag': 'cloud-native'},
#   {'term': r'\bstac\b', 'tag': 'stac'},
#   {'term': r'\bCOG(s)?\b', 'tag': 'cog'},
#   {'term': r'\b(geo)?zarr\b', 'tag': 'zarr'},
#   {'term': r'\bvirtualizarr\b', 'tag': 'virtualizarr'},
#   {'term': r'\bhyperspectral\b', 'tag': 'hyperspectral'},
# ])
# pprint(event_info.head(1))
