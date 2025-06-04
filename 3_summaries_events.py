import json
import re

with open('2_event_info.json', 'r') as f:
    event_info = json.load(f)


def search_events(search_term):
  matched_events = []
  for event in event_info:
      if (
          (re.search(f'{search_term['term']}', event['title'], re.IGNORECASE) is not None)
          or ('abstract' in event and re.search(f'{search_term['term']}', event['abstract'], re.IGNORECASE) is not None)
          or ('authors' in event and re.search(f'{search_term['term']}', ', '.join(event['authors']), re.IGNORECASE) is not None)
          or ('affiliations' in event and re.search(f'{search_term['term']}', ', '.join(event['affiliations']), re.IGNORECASE) is not None)
      ):
          matched_events.append(event)
      
          if len(matched_events) > 0:
            if 'tags' not in event:
              event['tags'] = set()
            event['tags'].add(search_term['tag'])

  return matched_events

search_terms = [
  {'term': r'\bcloud-native|cloud native\b', 'tag': 'cloud-native'},
  {'term': r'\bstac\b', 'tag': 'stac'},
  {'term': r'\bCOG(s)?\b', 'tag': 'cog'},
  {'term': r'\b(geo)?zarr\b', 'tag': 'zarr'},
  {'term': r'\bvirtualizarr\b', 'tag': 'virtualizarr'},
  {'term': r'\b(geo)?parquet\b', 'tag': 'parquet'},
  {'term': r'\bkerchunk\b', 'tag': 'kerchunk'},
  {'term': r'\b(geo)?flatgeobuf\b', 'tag': 'flatgeobuf'},
  {'term': r'\bpmtiles\b', 'tag': 'pmtiles'},
  {'term': r'\bfiboa\b', 'tag': 'fiboa'},
  {'term': r'\bpangeo\b', 'tag': 'pangeo'},
  {'term': r'\bcopc\b', 'tag': 'copc'},
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

print(f'{len(tagged_events)} out of {len(event_info)} events have matched tags')

# Change tag set into list
for event in tagged_events:
   event['tags'] = list(event['tags'])

with open('3_test_tagged_file.json', 'w') as f:
  json.dump(tagged_events, f, indent=2)
