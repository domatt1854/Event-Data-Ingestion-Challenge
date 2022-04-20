#!/usr/bin/env python3

# to access command line arguments
import sys

from html2text import html2text

# sqlite wrapper class
from db_table import db_table

# for method typing
from typing import Dict, List

# python modules for table definitions and constants
import table_definitions as table_defs
import agenda_constants as constants

"""
This script filters and queries the tables in the database created from import_agenda.py

"""

def sanitize_string(val:str) -> str:
    """
    removes a string of any whitespace, carriage returns, tabs, and hard spaces. 
    Makes a string safe for use in SQL statements.

    Parameters
    -------------
    val: str
        the string to sanitize

    Returns: the sanitized string
    
    """
    if val is None:
        return None

    val = html2text(val)

    chars_to_sub = ['\n', '\r', '\t', '&nbsp']
    quotes = ["'", '"']

    for char in chars_to_sub:
        val = val.replace(char, ' ')

    # remove any quotes to make our sql statement can be executed
    for quote in quotes:
            val = val.replace(quote, '')

    # remove trailing and leading whitespace
    val = val.strip()


    return val


def parse_command_line(cmdline: List[str]) -> Dict[str, str]:
    """
    Parses the command line by locating the column value and lookup values.

    Paramaters
    -------------
    cmdline: List[str]
        the commandline arguments
    
    Returns
        a dictionary in the format of { column_name: lookup_value }
    """

    # if the user forgot to provide a value or column to look up

    if(len(cmdline) < 3):
        raise TypeError("Please provide your query in the following format: [column] [value]")

    column_index = 1
    column_name = cmdline[column_index]


    # if the user inputs a wrong column name
    if(column_name not in constants.LOOKUP_COLS):
        raise ValueError("{} is not a valid lookup column.".format(column_name))

    lookup_dict = {}
    lookup_val = ""
    

    # lookup values can be separated by whitespace, concatenate the arguments into one string
    for i in range(column_index + 1, len(cmdline)):
        lookup_val += cmdline[i] + " "

    lookup_val = sanitize_string(lookup_val)
    lookup_dict[column_name] = lookup_val
    

    return lookup_dict

def shorten_string(val:str, width:int) -> str:
    """
    Takes a string and shortens it down a specified width and appends an elipsis if 
    the string is wider than the specified width
    
    Parameters
    ------------
    val: str   
        the string to be shortened
    width: int
        the desired width of a string

    Returns
        the shortened string
    """

    # make space for the elipsis 
    ellipsis_length = 5

    if(len(val) > (width - ellipsis_length)):
        return val[:(width - ellipsis_length)].rstrip() + "..."

    return val


def print_query_result(result: List[Dict[str,str]]) -> None:
    """"
    Formats a query and prints them to the screen including headers.
    
    Parameters
    -----------
    result: List[Dict[str, str]]
        a list of dictionaries returned from a query
    
    Returns
        Nothing
    """

    # column widths for header
    title_width = 40
    location_width = 20
    description_width = 45
    type_width = 35

    # underlying border under the header columns
    total_width = title_width + location_width + description_width + type_width
    header_underline = "=" * total_width

    # query header

    print(
        '{:<{}}'.format('Title', title_width),
        '{:<20}'.format('Location'),
        '{:<45}'.format('Description'),
        '{:<35}'.format('Type')
    )

    print(header_underline)

    for row in result:

        # shorten the strings and append an ellipsis 
        title = shorten_string(row['title'], title_width)
        location = shorten_string(row['location'], location_width)
        description = shorten_string(row['description'], description_width)
        session_type = shorten_string(row['session_type'], type_width)

        print(
            '{0: <40}'.format(title),
            '{0: <20}'.format(location),
            '{0: <45}'.format(description),
            '{0: <35}'.format(session_type)
        )

    print()
        

def select_from_sessions_columns(lookup_dict: Dict[str,str]) -> List[Dict[str,str]]:
    """
    Uses the sqlite wrapper class to select and filter rows passed in through lookup_dict.

    Parameters
    -----------
    lookup_dict: Dict[str,str]
        dictionary containing the column name and the value to search for

    Returns
        - a list of dictionaries returned from the search query. 
        - an empty list if no rows match the lookup value
    """

    # connect to the sessions table
    sessions = db_table(constants.SESSIONS_TABLE_NAME, table_defs.sessions_dict)

    # grab all sessions that match the value provided
    parent_result = sessions.select(constants.SESSIONS_COLS, lookup_dict)

    final_result = []

    # index to skip over subsessions if they are already added
    latest_subsession_id = 0
    

    for row in parent_result:
        
        # if this row has already been added, skip it
        if(row['session_id'] > latest_subsession_id):
            final_result.append(row)

      
        # query the sessions' subsessions if it has any
        if(row["session_type"] == "Session"):
            subsessions_query = sessions.select(constants.SESSIONS_COLS, {'parent_session_id': str(row['session_id'])})

            for subsession_row in subsessions_query:
                final_result.append(subsession_row)

                # keep track of the last subsession's index
                if(subsession_row['session_id'] > latest_subsession_id):
                    latest_subsession_id = subsession_row['session_id']


    return final_result

def select_from_speakers_column(lookup_dict: Dict[str,str]) -> List[Dict[str,str]]:
    """
    Uses the sqlite wrapper class to select and filter rows passed in through lookup_dict.
    Does multiple queries to traverse tables in order to get the sessions rows

    Parameters
    ------------
    lookup_dict: dict
        dictionary containing the column name and the value to search for
    
    Returns
        -a list of dictionaries returned from the query. 
        -an empty list if the speaker is not in any session
    """
    
    # create connections with the tables
    sessions = db_table(constants.SESSIONS_TABLE_NAME, table_defs.sessions_dict)
    speakers = db_table(constants.SPEAKERS_TABLE_NAME, table_defs.speakers_dict)
    sessions_speakers = db_table(constants.SESSIONS_SPEAKERS_TABLE_NAME, table_defs.sessions_speakers_dict)

    # first, lookup the speaker name in the speakers table
    speakers_query_result = speakers.select(constants.SPEAKERS_COLS, lookup_dict)

    # return an empty list if the speaker was not found
    if len(speakers_query_result) == 0:
        return []
    
    # grab the speaker dictionary row if the query returned a value
    speakers_query_result = speakers_query_result[0]

    final_result = []

    if speakers_query_result:

        # dictionary to look up corresponding rows in the sessions_speakers table
        speaker_id_dict = {'speaker_id': str(speakers_query_result['speaker_id'])}

        # query the sessions_speakers table filtering by speaker id
        sessions_speakers_id = sessions_speakers.select(constants.SESSIONS_SPEAKERS_COLS, speaker_id_dict)

        # index to skip over subsessions if they are already added
        latest_subsession_index = 0

        for row in sessions_speakers_id:

            session_row_dict = {}
            session_row_dict['session_id'] = row['session_id']

            # query the sessions table using the session_id returned from sessions_speakers
            parent_result = sessions.select(constants.SESSIONS_COLS, session_row_dict)[0]

            # if this row has already been added, skip it
            if(parent_result['session_id'] > latest_subsession_index):
                final_result.append(parent_result)

            # If this session has any subsessions, search for them and append them to the final result
            if parent_result['session_type'] == 'Session':

                parent_id = parent_result['session_id']
                subsessions = sessions.select(constants.SESSIONS_COLS, {'parent_session_id': parent_id})

                for subsession in subsessions:

                    # keep track of the last subsession's index
                    if(subsession['session_id'] > latest_subsession_index):
                        latest_subsession_index = subsession['session_id']

                    final_result.append(subsession)


    return final_result


def main():
    # connect to the sessions table
    sessions = db_table(constants.SESSIONS_TABLE_NAME, table_defs.sessions_dict)

    lookup_dict = parse_command_line(sys.argv)

    # if user is looking up a speaker, query from the speaker table.
    # else, query from the sessions table
    if "speaker" in lookup_dict.keys():
        speakers_lookup_dict = {}
        speakers_lookup_dict['speaker_name'] = lookup_dict['speaker']

        query_result = select_from_speakers_column(speakers_lookup_dict)
    else:
        query_result = select_from_sessions_columns(lookup_dict)

    # format and print the query to the console
    print_query_result(query_result)



if __name__ == "__main__":
    main()
    



