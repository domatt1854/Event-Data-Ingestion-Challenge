#!/usr/bin/env python3

# sqlite wrapper class
# to create and connect to the database
from db_table import db_table

# python modules for table definitions and constants
import table_definitions as table_defs
import agenda_constants as constants

# for reading and parsing spreadsheets
import xlrd

# to grab command line arguments
import sys

# to extract text from an html tag
from html2text import html2text

import os

"""
This program extracts data from a spreadsheet file and creates a relational database that fits the data format
of an event spreadsheet passed in from the command line. It then populates the database using the extracted data.
"""
    
class AgendaToDatabase():
    """
    This class handles reading in the spreadsheet. Parsing the spreadsheet and populating the database.
    """

    def __init__(self, spreadsheet_file: str, skip_num_rows: int) -> None:
        """
        Initializes AgendaToDatabase by grabbing the first sheet of agenda.xls' 

        Parameters
        ------------
        excel_file: str
            the name of the spreadsheet that contains the data for an event's agenda

        skip_num_rows: int
            the number of rows to skip to reach the headers in agenda.xls
        """
    
        # open the spreadsheet and connect to the first sheet
        events_workbook = xlrd.open_workbook(spreadsheet_file)
        self.event_sheet = events_workbook.sheet_by_index(0)

        self.skip_num_rows = skip_num_rows


    def create_tables(self) -> None:
        """
        Creates the tables and provides a connection to the tables.
        The tables will be saved in "interview_test.db"
        """
        # create the tables and inserts them into the database "interview_test.db"
        self.speakers = db_table(constants.SPEAKERS_TABLE_NAME, table_defs.speakers_dict)
        self.sessions = db_table(constants.SESSIONS_TABLE_NAME, table_defs.sessions_dict)
        self.sessions_speakers = db_table(constants.SESSIONS_SPEAKERS_TABLE_NAME, table_defs.sessions_speakers_dict)


    def get_cell_value(self, row: int, col: int) -> str:
        """ 
        Wrapper function for cell_value. Access a cell in the agenda.xls sheet.

        Parameters
        -------------
        row: int
            the row in the event sheet to access
        col: int
            the column in the event sheet to access
        

        Returns: the value in the cell

        """
        val = self.event_sheet.cell_value(row, col)
        
        return val
    
    def sanitize_string(self, val:str) -> str:
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

        chars_to_sub = ['\n', '\r', '\t', '&nbsp']

        quotes = ["'", '"']

        for char in chars_to_sub:
            val = val.replace(char, ' ')

        for quote in quotes:
            val = val.replace(quote, '')


        # remove trailing and leading whitespace
        val = val.strip()


        return val


    def populate_database(self) -> None:
        """
        Parses data of an agenda spreadsheet file and populates tables in the database
        """

        # contains every speaker and their corresponding id
        speakers_dict = dict()

        # primary key indices to set foreign keys
        sessions_pk_index = 1
        parent_session_index = 1
        speakers_pk_index = 1


        row_index = self.skip_num_rows

        while( row_index < self.event_sheet.nrows):

            # each dictionary will be used to create a row in each table
            sessions_row_dict = dict()
            speakers_dict_row = dict()
            
            sessions_row_dict['date'] = self.get_cell_value(row_index, 0)
            sessions_row_dict['time_start'] = self.get_cell_value(row_index, 1)
            sessions_row_dict['time_end'] = self.get_cell_value(row_index, 2)
            sessions_row_dict['session_type'] = self.get_cell_value(row_index, 3)
            
            # clean long texts before inserting
            title = self.get_cell_value(row_index, 4)
            location = self.get_cell_value(row_index, 5)
            description = self.get_cell_value(row_index, 6)
            speakers = self.get_cell_value(row_index, 7)

            title = self.sanitize_string(title)
            location = self.sanitize_string(location)
            description = html2text(str(description))
            description = self.sanitize_string(description)

            sessions_row_dict['title'] = title
            sessions_row_dict['location'] = location
            sessions_row_dict['description'] = description
            

            if(sessions_row_dict['session_type'] == "Session"):
                # keep track of the session index in case it has subsessions
                parent_session_index = sessions_pk_index
                parent_session_title = title
                sessions_row_dict['parent_session_id'] = None
            else:
                # refer to the parent session's PK index if the row is a subsession
                sessions_row_dict['parent_session_id'] = parent_session_index
                sessions_row_dict['session_type'] = "Subsession of " + parent_session_title


            if speakers != "":
                speakers = speakers.split("; ")

                for speaker in speakers:
                    sessions_speaker_dict_row = dict()

                    if speaker not in speakers_dict.keys():

                        # keep track of new speakers encountered
                        speakers_dict[speaker] = speakers_pk_index

                        speakers_dict_row['speaker_name'] = self.sanitize_string(speaker)
                        speakers_pk_index = self.speakers.insert(speakers_dict_row) + 1

                    # add the current session_id and speaker_id to the sessions_speakers table
                    sessions_speaker_dict_row['speaker_id'] = speakers_dict[speaker]
                    sessions_speaker_dict_row['session_id'] = sessions_pk_index
                    self.sessions_speakers.insert(sessions_speaker_dict_row)
                    
            
            sessions_pk_index = self.sessions.insert(sessions_row_dict) + 1


            row_index += 1

    
def main():

    # remove the database file if it already exists.
    database_filename = 'interview_test.db'

    if(os.path.exists(database_filename)):
        os.remove(database_filename)

    # check if the commandline is valid
    if(len(sys.argv) != 2):
        raise TypeError("import_agenda expected 2 arguments. {} was given".format(len(sys.argv)))
    
    # grabbing the spreadsheet filename from the command line
    spreadsheet_file = sys.argv[1]

    # rows to skip before reading in data
    num_skip_rows = 15

    # begin reading in data and populating the database
    agenda_to_database = AgendaToDatabase(spreadsheet_file, num_skip_rows)
    agenda_to_database.create_tables()
    agenda_to_database.populate_database()



if __name__ == "__main__":
    main()
    
    