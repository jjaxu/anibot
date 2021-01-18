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


# access_token is technically optional, but including it allows the 
# user to update private lists
def getMediaInfo(user_id: int, media_id: int, access_token: str=None):
    query = '''
    query ($userId: Int, $mediaId: Int) {
        MediaList (userId: $userId, mediaId: $mediaId){
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
    '''
    
    variables = {
        "userId": int(user_id),
        "mediaId": int(media_id)
    }

    result = send_graphql_request(query, variables, access_token)
    if not result:
        logging.error(f"Failed to get media info of userId: {user_id}, mediaId: {media_id}")
        return None

    return result["MediaList"]


def increaseProgress(access_token: str, user_id: int, media_id: int) -> dict:
    currentInfo = getMediaInfo(user_id, media_id, access_token)
    if not currentInfo:
        return None

    current_progress = currentInfo['progress']
    total_progress = currentInfo['media']['episodes']

    if current_progress == total_progress:
        return {
            "alreadyCompleted": True
        }

    updateResult = setProgress(access_token, media_id, current_progress + 1)
    if not updateResult:
        logging.error("Failed increment progress")
        return None

    return updateResult

def setProgress(access_token: str, media_id: int, progress: int):
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

    variables = {
        "mediaId": int(media_id),
        "progress": int(progress)
    }

    result = send_graphql_request(query, variables, access_token)
    if not result:
        logging.error(f"Failed to set progress to {progress} for media {media_id}")
        return None

    result = result["SaveMediaListEntry"]
    logging.info(f"Set progress for anime: {result}")
    return result

def send_graphql_request(query: dict, variables: dict=dict(), token: str=None) -> dict:
    headers = {"Authorization": f"Bearer {token}"} if token else None
    response = requests.post(ANILIST_URL, headers=headers ,json={'query': query, 'variables': variables})

    if not response.ok:
        logging.error(f"AniList API returned an error: {response.text}")
        return None

    return response.json()['data']
