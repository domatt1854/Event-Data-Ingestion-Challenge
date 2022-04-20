#!/usr/bin/env python3

import unittest
import lookup_agenda as lookup
import agenda_constants as constants

"""
This program checks if a query returned by lookup_agenda.py is correct.
It does so by checking if the the session data returned matches the desired rows.

Before running this file, check to see if "interview_test.db" already exists. If it does not,
run import_agenda.py to create the database.

"""

class TestLookupAgenda(unittest.TestCase):

    def test_parse(self):
        """
        This method checks if the program can parse multiple command line args and concatenate them correctly
        """

        print("\n****** TESTING parse_command_line() ******")
        self.assertEqual(lookup.parse_command_line(['lookup_agenda.py', 'speaker', 'Carl', 'A.', 'Waldspurger']), {"speaker": "Carl A. Waldspurger"})
        self.assertEqual(lookup.parse_command_line(['lookup_agenda.py', 'time_start', '11:00 AM']), {"time_start": "11:00 AM"})
        self.assertEqual(lookup.parse_command_line(
            ['lookup_agenda.py', 'description', 'Kick', 'off', 'the', 'day', 'with', 'our', 'warm', 'up', 'workshops!']),
            {"description": "Kick off the day with our warm up workshops!"}
        )
    
        print("****** PASSED *******\n")

    def test_lookup_speakers(self):
        """
        This test checks if speakers are queried correctly. It does so by checking the length of the query and the locations of the query returned.
        """

        print("****** TESTING select_from_speakers_column *******")

        # lookup values to test
        lookup_dicts = (
            {"speaker_name": "Carl A. Waldspurger"}, # Session with Subsessions
            {"speaker_name": "Guruduth Banavar"}, # Single Session
            {"speaker_name": "Luis Ceze"},
            {"speaker_name": "Shan Lu"}, # Session with Subsessions
            {"speaker_name": "Keshav Pingali"},
            {"speaker_name": "Jared Wu"} # speaker does not exist within table
        )

        # manually verified data to test result against
        lookup_lengths = (5, 2, 3, 4, 6, 0)

        lookup_locations = (
            ['Room 201', 'Coral 1', 'Coral 2', 'Coral 3', 'Coral 4'],
            ['South Pacific Ballroom', 'South Pacific Ballroom'],
            ['Grand Ballroom B', '', 'Coral 2'],
            ['', 'Coral 1', 'Coral 2', 'Coral 3'],
            ['', 'Room 300', '', '', '', 'Coral 1'],
            []
        )
        
        # iterrate through the returned results and compare them
        for index, lookup_dict in enumerate(lookup_dicts):
            print("testing {}".format(lookup_dict))

            query_result = lookup.select_from_speakers_column(lookup_dict)

            # extract all the locations from the query
            locations = [row['location'] for row in query_result]
            
            self.assertEqual(len(query_result), lookup_lengths[index])
            self.assertEqual(locations, lookup_locations[index])

        print("****** PASSED *******\n")

    def test_lookup_dates(self):
        """
        This tests if the number of rows returned by the dates match the number of rows
        found in the spreadsheet.
        """
        
        print("****** TESTING DATE LOOKUP ******")
        date_dicts = [
            {"date": "06/16/2018"},
            {"date": "06/17/2018"},
            {"date": "06/18/2018"}
        ]

        number_of_rows_dates = [19, 30, 15]

        # extract all the locations from the query
        for index, date in enumerate(date_dicts):
            print("testing {}".format(date))
            self.assertEqual(len(lookup.select_from_sessions_columns(date)), number_of_rows_dates[index])
        
        print("****** PASSED *******\n")

    def test_lookup_time_start(self):
        """
        This tests if the if lookups on the columns time_start and time_end work correctly by checking the lengths
        of each returned query.

        """
        print("****** TESTING DATE TIMES ******")

        time_dicts = [
            {"time_start": "08:30 AM"},
            {"time_start": "11:45 AM"},
            {"time_start": "02:15 PM"},
            {"time_start": "10:00 PM"}, 
            {"time_end": "02:50 PM"}, # This time is used for 2 sessions with many subsessions
            {"time_end": "11:15 AM"},
            {"time_end": "10:50 AM"},
            {"time_end": "09:00 PM"} 
        ]
        
        time_dicts_lengths = [3, 2, 1, 0, 10, 2, 3, 0]

        # extract all the locations from the query
        for index, time_dict in enumerate(time_dicts):
            print("testing {}".format(time_dict))
            self.assertEqual(len(lookup.select_from_sessions_columns(time_dict)), time_dicts_lengths[index])

        print("****** PASSED ******\n")


    def test_lookup_title(self):
        """
        This test tests if lookup titles returns the correct locations for the queries. 
        Also tests if the query returns subsessions correctly
        """
        print("****** TESTING TITLES ******")

        title_dicts = [
            {'title': 'Break'},
            {'title': 'Session 5A: Storage systems:'},
            {'title': 'Finding the Limit: Examining the Potential and Complexity of Compilation Scheduling for JIT-Based Runtime Systems'},
            {'title': 'Session 7A: Software reliability and testing II'}, # Session with Subsession
            {'title': 'Triple-A: A Non-SSD Based Autonomic All-Flash Array for Scalable High Performance Computing Storage Systems'},
            {'title': 'Software Demo'} # in case where no event with the title exists
        ]

        title_locations = [
            ['Coral Lounge', 'Coral Lounge', 'Lobby', 'Lobby', 'Coral Lounge', 'Lobby', 'Coral Lounge'],
            ['Room 201', '', '', '', ''],
            [''], # returned session has no location
            ['', 'Coral 1', 'Coral 2', 'Coral 3'],
            [''], 
            [] # no results returned
        ]

        for index, title_dict in enumerate(title_dicts):

            print("testing {}".format(title_dict))

            # extract all the locations from the query
            query_result = lookup.select_from_sessions_columns(title_dict)
            locations = [row['location'] for row in query_result]

            self.assertEqual(locations, title_locations[index])

        print("****** PASSED *******\n")


    def test_lookup_description(self):
        """
        This tests if the locations returned are correct for descriptions of varying size.
        Descriptions can be found in agenda_constants.py.
        """

        print("******* TESTING DESCRIPTIONS *******")

        # descriptions are quite long, so they are kept in the constants folder
        descriptions = constants.test_descriptions

        # Clean the input as the lookup program would
        descriptions = [lookup.sanitize_string(desc) for desc in descriptions]

        description_dicts = [
            {"description": descriptions[0]},
            {"description": descriptions[1]},
            {"description": descriptions[2]},
            {"description": descriptions[3]},
            {"description": descriptions[4]}
        ]


        description_locations = [
            ['South Pacific Ballroom'],
            ['Grand Ballroom B'],
            ['Room 201', 'Coral 1', 'Coral 2', 'Coral 3', 'Coral 4'],
            ['South Pacific Ballroom', 'South Pacific Ballroom'],
            ['Coral 2']
        ]

        for index, desc_dict in enumerate(description_dicts):
            print("Testing {}".format(descriptions[index][:10] + " ..."))

            # extract all the locations from the query
            query_result = lookup.select_from_sessions_columns(desc_dict)
            locations = [row['location'] for row in query_result]

            self.assertEqual(locations, description_locations[index])

        print("******* PASSED *******\n")

if __name__ == "__main__":
    unittest.main()