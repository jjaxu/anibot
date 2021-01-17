INLINE_QUERY_KEY = "inline_query"
CALLBACK_QUERY_KEY = "callback_query"
EDITED_MESSAGE_KEY = "edited_message"
MESSAGE_KEY = "message"
MESSAGE_ID_KEY = "message_id"
DATA_KEY = "data"
ID_KEY = "id"
CHAT_ID_KEY = "chat_id"
QUERY_KEY = "query"
TEXT_KEY = "text"
CHAT_KEY = "chat"
FROM_KEY = "from"
TYPE_KEY = "type"
TITLE_KEY = "title"
FIRST_NAME_KEY = "first_name"
LAST_NAME_KEY = "last_name"
USERNAME_KEY = "username"
PARSE_MODE_KEY = "parse_mode"
PHOTO_KEY = "photo"

GROUP_STR = "group"
SUPERGROUP_STR = "supergroup"
PRIVATE_STR = "private"

class BotQuery:

    @classmethod
    def parse_event(cls, event_json):
        data = event_json
        empty = dict()
        result = cls()
        
        if INLINE_QUERY_KEY in data:
            result.is_inline_query = True
            result.inline_query_id = data[INLINE_QUERY_KEY][ID_KEY]
            result.inline_query_text = data[INLINE_QUERY_KEY][QUERY_KEY]
    
        if CALLBACK_QUERY_KEY in data:
            result.has_callback_query = True
            result.callback_query = cls.parse_event(data[CALLBACK_QUERY_KEY])

        msg_key = None
        if MESSAGE_KEY in data:
            msg_key = MESSAGE_KEY
        elif EDITED_MESSAGE_KEY in data:
            msg_key = EDITED_MESSAGE_KEY
            result.is_edited = True
            
        result.message = data.get(msg_key, empty).get(TEXT_KEY)
        result.message_id = data.get(msg_key, empty).get(MESSAGE_ID_KEY)
        result.callback_data = data.get(DATA_KEY)
        result.callback_from_id = data.get(FROM_KEY, empty).get(ID_KEY)
        result.chat_id = data.get(msg_key, empty).get(CHAT_KEY, empty).get(ID_KEY)
        result.chat_title = data.get(msg_key, empty).get(CHAT_KEY, empty).get(TITLE_KEY)
        result.from_id = data.get(msg_key, empty).get(FROM_KEY, empty).get(ID_KEY)
        result.user_first_name = data.get(msg_key, empty).get(FROM_KEY, empty).get(FIRST_NAME_KEY)
        result.user_last_name = data.get(msg_key, empty).get(FROM_KEY, empty).get(LAST_NAME_KEY)
        result.user_username = data.get(msg_key, empty).get(FROM_KEY, empty).get(USERNAME_KEY)

        result.is_private = data.get(msg_key, empty).get(CHAT_KEY, empty).get(TYPE_KEY) == PRIVATE_STR

        group_type = data.get(msg_key, empty).get(CHAT_KEY, empty).get(TYPE_KEY)
        
        result.is_group = group_type == GROUP_STR or group_type == SUPERGROUP_STR
        result.is_supergroup = group_type == SUPERGROUP_STR
        result.is_private = data.get(msg_key, empty).get(CHAT_KEY, empty).get(TYPE_KEY) == PRIVATE_STR

        if not (
            result.message or
            result.is_inline_query or 
            result.has_callback_query
        ): raise ValueError("Invalid or unsupported query event while parsing")

        return result

    def __init__(self):
        self.is_private = False
        self.is_group = False
        self.is_supergroup = False
        self.is_edited = False

        # Inline query
        self.is_inline_query = False
        self.inline_query_id = None
        self.inline_query_text = None

        # Callback query
        self.has_callback_query = False
        self.callback_query = None
        self.callback_data = None
        self.callback_from_id = None

        # Message content
        self.message = None
        self.message_id = None
        self.chat_id = None
        self.from_id = None
        self.user_first_name = None
        self.user_last_name = None
        self.user_username = None
        self.chat_title = None

    def __repr__(self):
        return str(vars(self))
