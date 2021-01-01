import requests, json

ANILIST_URL = 'https://graphql.anilist.co'

def getAnime(name: str):
    querySearch = '''
    query ($searchInput: String) {
        Page {
            media (search: $searchInput, type: ANIME) {
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
    json_data = json.loads(response.text)

    return json_data["data"]["Page"]["media"]
