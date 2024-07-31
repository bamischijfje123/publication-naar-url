import streamlit as st
import re
import requests
import json

st.title("PublicationId naar URL PDZ")

def check_input(publication_id):
    if 'cockpit' in publication_id:
        return 'Plak niet de hele url, alleen de publicationId (bijvoorbeeld: publications-1234-A)'
    elif 'JobRequests' in publication_id:
        return 'Dit is een jobrequestId, geen publicationId :)'
    elif 'publications' not in publication_id:
        return 'Dit is geen publicationId'

#visit url and extract json with data
def get_json(url):
    response = requests.get(url).text

    #isolate the json text
    opening_pattern = '{'
    closing_pattern = '"loadMoreText":null}'

    json_pattern = re.compile(rf'{opening_pattern}(.*){closing_pattern}')
    json_match = re.search(json_pattern, response)

    if json_match:
        json_str = json_match.group(0)
        try:
            json_data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
    else:
        print("Error with extracting JSON data")
    return json_data

#extract job info from json
def extract_job_details(json_data, werkmaatschappij):
    job_details = []

    for job in json_data['results']:
        salary = 'Markconform salaris' if job['salary']['salaryMin'] == 0 else f"€{job['salary']['salaryMin']} - €{job['salary']['salaryMax']}"
        hours_per_week_min = job['employment']['hoursPerWeekMin'] or 0
        hours_per_week_max = job['employment']['hoursPerWeekMax'] or 0
        details = {
                'werkmaatschappij': werkmaatschappij,
                'publicationId': job['remoteId'],
                'publicationUrl': job['metaData']['publicationUrl'],
                'functietitel': job['title'],
                'hoursPerWeek': f"{hours_per_week_min} - {hours_per_week_max} uur",
                'city': job['workLocation']['city'],
                'summary': job['descriptions']['summary'],
                'educationLevels': ', '.join([level['name'] for level in job['facets']['educationLevels']]),
                'salary': salary
            }
        job_details.append(details)

    return job_details

def get_url(publication_id):
    limit = 1000
    url_PDZ = f'https://jobsite-pdz.recruitnow.nl/api/scripts/jobboard-search-results.js?sort=Published&sortDirection=Descending&limit={limit}&dist=25&filters=agencies-1283-A'

    json_data_PDZ = get_json(url_PDZ)

    job_details_PDZ = extract_job_details(json_data_PDZ, 'PDZ')

    for job in job_details_PDZ:
        if job['publicationId'] == publication_id:
            text_to_print = job['publicationUrl']
            break
        else:
            text_to_print = 'Geen online publicatie gevonden'
    return text_to_print

# Create a form
with st.form(key='publication_form'):
    publication_id = st.text_input('PublicationId: ')
    
    # Create a submit button
    submit_button = st.form_submit_button(label='Vind URL')

# Store the input when the form is submitted
if submit_button:
    response = check_input(publication_id)
    if response:
        st.write(response)
    else:
        url = get_url(publication_id)
        st.write(url)


