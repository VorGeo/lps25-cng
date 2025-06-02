import json
import re

with open('2_event_info.json', 'r') as f:
    event_info = json.load(f)


def search_events(search_term):
  matched_events = []
  for event in event_info:
      if (
          (re.search(rf'\b{search_term['term']}\b', event['title'].lower()) is not None)
          or ('abstract' in event and re.search(rf'\b{search_term['term']}\b', event['abstract'].lower()) is not None)
      ):
          matched_events.append(event)
      
          if len(matched_events) > 0:
            if 'tags' not in event:
              event['tags'] = set()
            event['tags'].add(search_term['tag'])

  return matched_events

search_terms = [
  {'term': 'cloud-native|cloud native', 'tag': 'cloud-native'},
  {'term': 'stac', 'tag': 'stac'},
  {'term': 'pangeo', 'tag': 'pangeo'},
  {'term': 'cog|cogs', 'tag': 'cog'},
  {'term': 'jupytergis', 'tag': 'jupytergis'},
  {'term': 'zarr|geozarr', 'tag': 'zarr'},
  {'term': 'parquet|geoparquet', 'tag': 'parquet'},
  # {'term': 'earth engine', 'tag': 'earth engine'},
]

for search_term in search_terms:
  search_events(search_term)

print("\nEvents with tags:")
tagged_events = [event for event in event_info if 'tags' in event]
for event in tagged_events:
    print(f"""
    Session ID: {event['session_id']}
    Presentation ID: {event['presentation_id'] if 'presentation_id' in event else 'No presentation ID'}
    Title: {event['title']}
    Authors: {', '.join(event['authors']) if 'authors' in event else 'No authors'}
    Affiliations: {', '.join(event['affiliations']) if 'affiliations' in event else 'No affiliations'}
    Tags: {', '.join(event['tags']) if 'tags' in event else 'No tags'}
    """)
    print("-" * 80)

print(f'{len(tagged_events)}')

# Change tag set into list
for event in tagged_events:
   event['tags'] = list(event['tags'])

with open('3_test_tagged_file.json', 'w') as f:
  json.dump(tagged_events, f, indent=2)
