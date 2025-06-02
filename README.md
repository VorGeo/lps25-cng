# Cloud-Native Geospatial Events at the 2025 ESA Living Planet Symposium

This repository hosts a curated list of events, presentations, and tutorials at the [2025 ESA Living Planet Symposium (LPS25)](https://lps25.esa.int/) that are relevant to the Cloud-Native Geospatial (CNG) community. Our goal is to provide a quick and easy reference for attendees interested in learning more about technologies like STAC, COG, Zarr, GeoParquet, and other related topics within the Earth Observation (EO) domain.

The live website can be found at: https://VorGeo.github.io/lps25-cng/

## How This List is Generated

The event list is dynamically generated using Python and Pandas within a Quarto (`.qmd`) document (`index.qmd`). The Quarto document processes a list of event dictionaries, sorts them by date and time, and then renders them as HTML cards on the website.

## Contributing

We welcome contributions to keep this list accurate and comprehensive!

There are a couple of ways you can contribute:

1.  **Add new events directly:**
    *   You can edit the `index.qmd` file directly in your browser using [this link](https://github.com/VorGeo/lps25-cng/edit/main/index.qmd).
    *   Add a new Python dictionary to the `items.append({...})` list, following the existing structure for event details.
    *   Commit your changes and create a pull request.

2.  **Report missed events or suggest changes:**
    *   If you know of an event that should be on the list, or have a suggestion, please [create a new issue](https://github.com/VorGeo/lps25-cng/issues/new) on GitHub.
    *   Provide as much detail as possible about the event (title, session ID, date, time, location, URL, relevant CNG tags).

## Key Technologies Used

*   **Quarto:** For creating the dynamic web page from Python code and markdown.
*   **Python:** For scripting the event data processing.
*   **Pandas:** For data manipulation and sorting of the event list.

We hope this resource helps you navigate the exciting CNG-related content at LPS25!
