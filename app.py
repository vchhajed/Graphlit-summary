import streamlit as st
import requests
import jwt
import datetime
import json


def create_token():
    # Define the issuer and audience
    issuer = "graphlit"
    audience = "https://portal.graphlit.io"

    # Specify the role (Owner, Contributor, Reader)
    role = "Owner"

    # Specify the expiration (one hour from now)
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    # Define the payload
    payload = {
        "https://graphlit.io/jwt/claims": {
            "x-graphlit-environment-id": environment_id,
            "x-graphlit-organization-id": organization_id,
            "x-graphlit-role": role,
        },
        "exp": expiration,
        "iss": issuer,
        "aud": audience,
    }

    # Sign the JWT
    token = jwt.encode(payload, secret_key, algorithm="HS256") 
    return token

def graphlit_request(mutation, variables, func):
    url = 'https://data-scus.graphlit.io/api/v1/graphql'
    graphql_request = {'query': mutation, 'variables': variables}
    headers = {'Authorization': 'Bearer {}'.format(st.session_state['token'])}

    response = requests.post(url, json=graphql_request, headers=headers)

    if response.status_code == 200:
        st.success(f"{func} was successful!")
        # Display some part of the response, e.g., the created feed's ID

        response_data = response.json()
        st.json(response.json())
    else:
        st.error(f"GraphQL request failed with status code: {response.status_code}")
        st.text(f"Response: {response.text}")

def send_request(name, uri):
    url = 'https://data-scus.graphlit.io/api/v1/graphql'
    mutation = """
    mutation CreateFeed($feed: FeedInput!) {
        createFeed(feed: $feed) {
            id
            name
            state
            type
        }
    }
    """
    variables = {
        "feed": {
            "type": "WEB",
            "web": {
                "uri": uri
            },
            "name": name
        }
    }
    graphlit_request(mutation, variables, "feed creation")

def list_feeds():
    # Define the GraphQL mutation
    query = """
    query QueryFeeds($filter: FeedFilter!) {
        feeds(filter: $filter) {
            results {
            id
            name
            creationDate
            state
            owner {
                id
            }
            type
            reddit {
                subredditName
            }
            lastPostDate
            lastReadDate
            readCount
            schedulePolicy {
                recurrenceType
                repeatInterval
            }
            }
        }
    }
    """

    # Define the variables for the mutation
    variables = {
    "filter": {
        "offset": 0,
        "limit": 100
    }
    }
    graphlit_request(query, variables, "show list")


def delete_all_feeds():
    # Define the GraphQL mutation
    query = """
    mutation DeleteAllFeeds {
        deleteAllFeeds {
            id
            state
        }
        }
    """

    # Define the variables for the mutation
    variables = {
    }
    graphlit_request(query, variables, "delete all feed")

def create_specs():
    # Define the GraphQL endpoint URL
    url = 'https://data-scus.graphlit.io/api/v1/graphql'

    # Define the GraphQL mutation
    mutation = """
    mutation CreateSpecification($specification: SpecificationInput!) {
    createSpecification(specification: $specification) {
        id
        name
        state
        type
        serviceType
    }
    }
    """

    # Define the variables for the mutation
    variables = {
    "specification": {
        "type": "COMPLETION",
        "serviceType": "AZURE_OPEN_AI",
        "azureOpenAI": {
        "model": "GPT35_TURBO_16K",
        "temperature": 0.8,
        "probability": 0.2
        },
        "name": "GPT-3.5 Turbo Summarization"
    }
    }

    # Create a dictionary representing the GraphQL request
    graphql_request = {
        'query': mutation,
        'variables': variables
    }

    # Convert the request to JSON format
    graphql_request_json = json.dumps(graphql_request)

    # Include the JWT token in the request headers
    headers = {'Authorization': 'Bearer {}'.format(st.session_state['token'])}

    # Send the GraphQL request with the JWT token in the headers
    response = requests.post(url, json=graphql_request, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response content
        print(response.json()['data']['createSpecification']['id'])
        st.session_state['summarize_id'] = response.json()['data']['createSpecification']['id']
        print(response.json())
    else:
        print('GraphQL request failed with status code:', response.status_code)
        print('Response:', response.text)

def generate_summary(id, search):
    print(id)
    # Define the GraphQL endpoint URL
    url = 'https://data-scus.graphlit.io/api/v1/graphql'

    # Define the GraphQL mutation
    mutation = """
    mutation SummarizeContents($summarizations: [SummarizationStrategyInput!]!, $filter: ContentFilter) {
    summarizeContents(summarizations: $summarizations, filter: $filter) {
        specification {
        id
        }
        content {
        id
        }
        type
        items {
        text
        tokens
        summarizationTime
        }
        error
    }
    }
    """

    # Define the variables for the mutation
    variables = {
    "summarizations": [
        {
        "type": "SUMMARY",
        "specification": {
            "id": id
        },
        "items": 5
        },
        {
        "type": "QUESTIONS",
        "specification": {
            "id": id
        },
        "items": 5
        },
        {
        "type": "CUSTOM",
        "specification": {
            "id": id
        },
        "prompt": "Extract any named entities into JSON-LD format."
        }
    ],
    "filter": {
        "search": "OpenAI developer conference",
        "queryType": "SIMPLE",
        "searchType": "HYBRID"
    }
    }

    # Create a dictionary representing the GraphQL request
    graphql_request = {
        'query': mutation,
        'variables': variables
    }

    # Convert the request to JSON format
    graphql_request_json = json.dumps(graphql_request)

    # Include the JWT token in the request headers
    headers = {'Authorization': 'Bearer {}'.format(st.session_state['token'])}

    # Send the GraphQL request with the JWT token in the headers
    response = requests.post(url, json=graphql_request, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the response content
        print(response.json())
    else:
        print('GraphQL request failed with status code:', response.status_code)
        print('Response:', response.text)
    return response.json()


# Initialize session state variables if not already done
if 'token' not in st.session_state:
    st.session_state['token'] = None
if 'summary_result' not in st.session_state:
    st.session_state['summary_result'] = None
if 'summarize_id' not in st.session_state:
    st.session_state['summarize_id'] = None

def create_token(secret_key, environment_id, organization_id):
    # Define the issuer and audience
    issuer = "graphlit"
    audience = "https://portal.graphlit.io"

    # Specify the role (Owner, Contributor, Reader)
    role = "Owner"

    # Specify the expiration (one hour from now)
    expiration = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

    # Define the payload
    payload = {
        "https://graphlit.io/jwt/claims": {
            "x-graphlit-environment-id": environment_id,
            "x-graphlit-organization-id": organization_id,
            "x-graphlit-role": role,
        },
        "exp": expiration.timestamp(),  # Ensure this is a Unix timestamp
        "iss": issuer,
        "aud": audience,
    }

    # Sign the JWT
    token = jwt.encode(payload, secret_key, algorithm="HS256")
    return token

# Streamlit UI for credentials and data feeding
st.title("Data Feed and Summarization App")
if st.session_state['token'] is None:
    st.info("Generate token to get started!")
# Data feeding section
with st.form("data_feed_form"):
    name = st.text_input("Name")
    uri = st.text_input("URI to Feed Data")
    submit_data = st.form_submit_button("Submit Data")
if st.session_state['token']:
    list, delete = st.columns(2)
    with list:
        list_feed = st.button("List Feed")
        if list_feed:
            list_feeds()
    with delete:
        delete_feed = st.button("Delete All Feed")
        if delete_feed:
            delete_all_feeds()

if submit_data:
    if st.session_state['token'] and uri:
        send_request(name, uri)
        st.success("Data submitted successfully!")
    else:
        st.error("Please generate a token and provide a URI.")

search = st.text_input("Search")
submit_summary = st.button("Generate Summary based on search")
if submit_summary:
    if st.session_state['token'] and search:
        if st.session_state['summarize_id']:
            st.session_state['summary_result'] = generate_summary(st.session_state['summarize_id'], search)
            st.success("Summary generated successfully!")
        else:
            create_specs()
            st.session_state['summary_result'] = generate_summary(st.session_state['summarize_id'], search)
            st.success("Summary generated successfully!")
    else:
        st.error("Please ensure you have a token and have provided a content filter.")

# Display summarization results
if st.session_state['summary_result']:
    st.header("Summary Result")
    st.json(st.session_state['summary_result'])
    
with st.sidebar:
    with st.form("credentials_form"):
        st.info("Look into App Settings in Graphlit to get info!")
        secret_key = st.text_input("Secret Key", type="password")
        environment_id = st.text_input("Environment ID")
        organization_id = st.text_input("Organization ID")
        submit_credentials = st.form_submit_button("Generate Token")
    
if submit_credentials:
    if secret_key and environment_id and organization_id:
        st.session_state['token'] = create_token(secret_key, environment_id, organization_id)
        st.success("Token generated successfully!")
    else:
        st.error("Please fill in all the credentials.")