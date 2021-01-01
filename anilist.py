import requests, json, logging

ANILIST_URL = 'https://graphql.anilist.co'

def getAnime(name: str):
    querySearch = '''
    query ($searchInput: String) {
        Page {
            media (search: $searchInput, type: ANIME, sort: SEARCH_MATCH) {
                id
                description
                averageScore
                episodes
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
    logging.info(f'Anime results returned: {len(result)}')
    return result
