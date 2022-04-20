'''
Table definitions that correspond to an event database
Dictionaries will be used to create each table in the database
'''

#
# speakers table definition
#
# lookup table for every speaker that speaks at a session in an event
# each row will be unique to one specific speaker
#
speakers_dict = {
    "speaker_id": "integer PRIMARY KEY",
    "speaker_name": "text UNIQUE"
}

#
# sessions table definition
#
# contains records of sessions and subsessions
# contains foreign key
#   - parent_session_id : if the record is a subsession, this id references a session in the table. Can be NULL
#
sessions_dict = {
    "session_id": "integer PRIMARY KEY",
    "parent_session_id": "integer",
    "location": "text",
    "date": "text NOT NULL",
    "time_start": "text NOT NULL",
    "time_end": "text NOT NULL",
    "session_type": "text NOT NULL",
    "title": "text NOT NULL",
    "description": "text"
}

#
# sessions_speakers table definition
#
# each row refers to a row in the sessions table and a row in the speakers table
# composite key will be a combination of the session_id and speaker_id to enforce first normal form
#
sessions_speakers_dict = {
    "session_id": "integer",
    "speaker_id": "integer",
}