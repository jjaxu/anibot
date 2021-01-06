import requests, json, logging

ANILIST_URL = 'https://graphql.anilist.co'

def getAnime(name: str):
    querySearch = '''
    query ($searchInput: String) {
        Page {
            media (search: $searchInput, sort: SEARCH_MATCH) {
                id
                description (asHtml: false)
                status
                type
                averageScore
                episodes
                volumes
                format
                siteUrl
                isAdult
                coverImage {
                    medium
                }
                title {
                    romaji
                    english
                    native
                }
            }
        }
    }
    '''

    # Query variable
    variables = {
        'searchInput': name
    }

    # Make the HTTP Api request
    response = requests.post(ANILIST_URL, json={'query': querySearch, 'variables': variables})
    if not response.ok:
        logging.error(f"Failed to search anime {name}. Error: {response.text}")
        return []

    result = json.loads(response.text)["data"]["Page"]["media"]
    logging.info(f'Anime results returned for query "{name}": {len(result)}')
    return result
