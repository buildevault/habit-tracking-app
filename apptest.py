import sqlite3                          # Import to interact with the database
import pytest                           # Import to allow to run the test suite
from unittest.mock import patch         # Import to simulate a user input during tests
from app import get_current, create_habit, delete_habit, mark_habit_done, view_habits, insert_test_data, same_periodicity_habits, specific_longest_streak  # Import of the functions to test
from datetime import date, timedelta    # Import to work with calendar dates and time periods



# -------------------------- #
# --- Temporary database --- #
# -------------------------- #



@pytest.fixture                          
def db():
    """Purpose: create a temporary in-memory database (fixture) populated with the 5 predefined habits for each test.
    Each test requiring a database will have its own clear copy
    """
        
    conn = sqlite3.connect(":memory:")      # Create a temporary database, removed after the tests
    cursor = conn.cursor()                  # Allow to execute SQL queries
    # Create the habits table with the same structure as the real database
    cursor.execute("""
        CREATE TABLE habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly')),
            created_at TEXT NOT NULL,
            streak INTEGER DEFAULT 0,
            longest_streak INTEGER DEFAULT 0
        )
    """)
    # Create the habit_logs table with the same structure as the real database
    cursor.execute("""
        CREATE TABLE habit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            completed_at TEXT NOT NULL,
            UNIQUE(habit_id, completed_at),
            FOREIGN KEY(habit_id) REFERENCES habits(id)
        )
    """)
    conn.commit()                       # Save the database structure
    insert_test_data(cursor, conn)      # Load the 5 predefined habits and their logs of tracking data
    return conn, cursor
 
 
 
# ------------------------------ #
# --- Helper functions tests --- #
# ------------------------------ #
 
 
 
def test_one_daily_format():
    """
    Purpose: check if the get_current function returns today's date in YYYY-MM-DD format for daily habits.
    """

    result = get_current("daily")                   # Call the get_current function with daily frequency
    assert result == date.today().isoformat()       # Check if it returns today in YYYY-MM-DD format
 
def test_two_weekly_format():
    """
    Purpose: check if the get_current function returns today's date in YYYY-Www format for weekly habits.
    """

    result = get_current("weekly")                  # Call the get_current function with weekly frequency
    today = date.today()
    year, week, _ = today.isocalendar()             # Retrieve the current year and week number
    assert result == f"{year}-W{week}"              # Check if it returns the current week in YYYY-Www format
 
 
 
# ------------------------------------------------ #
# --- Default habit management functions tests --- #
# ------------------------------------------------ #
 

  
def test_three_create_habit(db): 
    """
    Purpose: check if create_habit inserts a new habit into the database.
    Arguments: request a database fixture
    """

    conn, cursor = db                                               # Unpack the connection and cursor from the fixture
    with patch("builtins.input", side_effect=["test", "daily"]):                # Set an hypothetic daily test habit
        create_habit(cursor, conn)                                              # Call the function to create a habit
    cursor.execute("SELECT name, frequency FROM habits WHERE name = 'test'")    # Query the database for the test habit
    row = cursor.fetchone()
    assert row is not None      # Check the habit was actually inserted
    assert row[0] == "test"     # Check the name was stored in the correct place
    assert row[1] == "daily"    # Check the frequency was stored in the correct place
 
 
def test_four_delete_habit(db):
    """
    Purpose: check if delete_habit removes an existing habit from the database.
    """

    conn, cursor = db
    with patch("builtins.input", return_value="test habit: drink water"):                   # Set an hypothetic user input of the name of the habit name to delete
        delete_habit(cursor, conn)                                                          # Call the function to delete the habit
    cursor.execute("SELECT COUNT(*) FROM habits WHERE name = 'test habit: drink water'")    # Query the database for the deleted habit
    count = cursor.fetchone()[0]
    assert count == 0                                                                       # Check the absence of the habit
 
def test_five_mark_habit_done_inserts_log(db):
    """
    Purpose: check if mark_habit_done inserts a completion log into the database.
    In order for this test to pass, we need to run it with a habit having no completion data for today (e.g. exercise)
    """
        
    conn, cursor = db
    cursor.execute("SELECT COUNT(*) FROM habit_logs")                       # Count existing logs from predefined data
    initial_count = cursor.fetchone()[0]                                    # Store the initial log count
    with patch("builtins.input", return_value="test habit: exercise"):      # Set an hypothetic user input of the name of the habit name to mark as completed
        mark_habit_done(cursor, conn)                                       # Call the function to mark the habit as done
    cursor.execute("SELECT COUNT(*) FROM habit_logs")                       # Query the habit_logs table for the presence of a log
    new_count = cursor.fetchone()[0]                                        # Store the new log count after completion
    assert new_count == initial_count + 1                                   # Check if exactly one log entry was inserted
 
def test_six_mark_habit_done_twice_deny(db):
    """
    Purpose: check if mark_habit_done denies a second completion log for the same habit in the same period.
    """

    conn, cursor = db
    with patch("builtins.input", return_value="test habit: exercise"):          # Mark exercise habit as done once
        mark_habit_done(cursor, conn)                                           
    cursor.execute("SELECT COUNT(*) FROM habit_logs")
    count_after_first = cursor.fetchone()[0]                                    # Query the log count after the first completion
    with patch("builtins.input", return_value="test habit: exercise"):          
        mark_habit_done(cursor, conn)                                           # Attempt to mark it as done again in the same period
    cursor.execute("SELECT COUNT(*) FROM habit_logs")                           
    count_after_second = cursor.fetchone()[0]                                   # Query the log count after the second completion
    assert count_after_first == count_after_second                              # Check if there is only one completion log entered and not two



# ------------------------------------------- #
# --- Analysis menu habit functions tests --- #
# ------------------------------------------- #



def test_seven_return_all_habits(db):               
    """
    Purpose: check if view_habits returns the 5 predefined habits.
    """
                          
    conn, cursor = db
    result = view_habits(cursor)    # Call the original view_habits function
    assert len(result) == 5         # Check if there are indeed 5 habits returned

def test_eight_return_same_periodicity(db): 
    """
    Purpose: check if same_periodicity_habits returns only the 2 predefined weekly habits.
    """
                                    
    conn, cursor = db
    with patch("builtins.input", return_value="weekly"):    # Set an hypothetic user input for a weekly frequency
        result = same_periodicity_habits(cursor)            # Call the same_periodicity_habits function
    assert len(result) == 2                                 # Check if only the 2 predefined weekly habits are returned

def test_nine_longest_weekly_streak(db):        
    """
    Purpose: check if the weekly habit with the highest current streak is correctly identified.
    """
                                     
    conn, cursor = db
    cursor.execute(                                 # Query the weekly habit with the highest current streak
        "SELECT name FROM habits WHERE frequency = 'weekly' ORDER BY streak DESC LIMIT 1"
    )
    result = cursor.fetchone()[0]                   # Store the name of the habit with the highest streak
    assert result == "test habit: clean room"       # Check if correct habit was identified

def test_ten_specific_longest_streak(db):                
    """
    Purpose: check if specific_longest_streak returns the correct longest streak for a given habit.
    """
                         
    conn, cursor = db
    with patch("builtins.input", return_value="test habit: drink water"):       # Set an  hypothetic user input of a habit name
        specific_longest_streak(cursor)                                         # Call the specific_longest_streak function
    cursor.execute("SELECT longest_streak FROM habits WHERE name = 'test habit: drink water'")  # Query the longest streak for the habit
    result = cursor.fetchone()[0]                   # Store the longest streak value of the habit
    assert result == 7                              # Check if it matches the predefined longest streak of seven
 
def test_eleven_struggle_last_four_weeks(db):          
    """
    Purpose: check if the least completed daily habit is correctly identified.
    """
                         
    conn, cursor = db
    end_date = (date.today() - timedelta(days=date.today().isocalendar()[2])).isoformat()           # Last Sunday
    start_date = (date.today() - timedelta(days=date.today().isocalendar()[2] + 27)).isoformat()    # 28 days before that
    cursor.execute(
        """
        SELECT habits.name, COUNT(habit_logs.id) AS completion_count    
        FROM habits
        LEFT JOIN habit_logs ON habits.id = habit_logs.habit_id         
        AND habit_logs.completed_at BETWEEN ? AND ?                     -- Only count completions within the last four weeks
        WHERE habits.frequency = 'daily'                                -- Filter to daily habits only
        GROUP BY habits.id                                              -- Group results by habit
        ORDER BY completion_count ASC                                   -- Sort by completion count in ascending order
        LIMIT 1                                                         -- Retrieve only the habit with the lowest count
        """,
        (start_date, end_date)          # Pass the date range of the last four complete weeks
    )
    result = cursor.fetchone()                      # Store the habit with the lowest completion count
    assert result is not None                       # Check if a result was returned
    assert result[0] == "test habit: exercise"      # Check if the test habit: exercise habit was indeed the least completed habit