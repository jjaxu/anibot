import requests, json, logging

ANILIST_URL = 'https://graphql.anilist.co'

def getAnime(name: str):
    query = '''
    query ($searchInput: String) {
        Page (page: 1, perPage: 20) {
            media (search: $searchInput, sort: POPULARITY_DESC) {
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
    result = send_graphql_request(query, variables)
    if not result:
        logging.error(f"Failed to search anime {name}")
        return []

    result = result["Page"]["media"]
    logging.info(f'Anime results returned for query "{name}": {len(result)}')
    return result

def getUserInfo(token: str) -> (int, str):
    query = '''
    query {
        Viewer {
            name
            id
        }
    }
    '''

    result = send_graphql_request(query, token=token)
    if not result:
        logging.error(f"Failed to get current user info")
        return None

    result = result['Viewer']
    logging.info(f"Got user info from AniList: {result}")

    
    return (result['id'], result['name'])
    

# Get's the list of status "WATCHING"
def getAnimeList(user_id: int) -> list:
    query = '''
    query ($userId: Int) {
        Page {
            mediaList (userId: $userId, status: CURRENT, type: ANIME){
                progress
                media {
                    id
                    episodes
                    title {
                        userPreferred
                    }
                }
            }
        }
    }
    '''

    variables = {
        "userId": int(user_id)
    }

    result = send_graphql_request(query, variables)
    if not result:
        logging.error(f"Failed to get user's anime list")
        return None

    result = result['Page']['mediaList']
    logging.info(f"Got user info from AniList: {result}")

    return result

def increaseProgress(access_token: str, media_id: int) -> dict:
    return None
    


def setProgress():
    query = '''
    mutation($mediaId: Int, $progress: Int) {
        SaveMediaListEntry(mediaId: $mediaId, progress: $progress) {
            status
            progress
            media {
                episodes
                title {
                    userPreferred
                }
            }
        }
    }
    '''


def send_graphql_request(query: dict, variables: dict=dict(), token: str=None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    response = requests.post(ANILIST_URL, headers=headers ,json={'query': query, 'variables': variables})

    if not response.ok:
        logging.error(f"AniList API returned an error: {response.text}")
        return None

    return response.json()['data']
