import sqlite3                          # Import to allow operations on .db databases
from dataclasses import dataclass       # Import to create a class constructor automatically
from typing import Literal              # Import to restrict value to specific possibilities
from datetime import date, timedelta    # Import to work with calendar dates and time periods



@dataclass      # Generate the class constructor automatically
class Habit:    # Define the data model of a habit and its attributes
    name: str                                   # Habit name
    frequency: Literal["daily", "weekly"]       # Frequency of the habit (daily or weekly)
    created_at: str                             # First tracking date of the habit
    streak: int                                 # Current streak duration



def connect_db():   
    """
    Purpose: connect to the database and create the tables
    Parameters: None
    Returns: connection to save changes and cursor to execute SQL queries
    """

    connection = sqlite3.connect("habits.db")   # Open or create the habits.db file
    query = connection.cursor()                 # Create a cursor object to execute SQL queries

    query.execute(
    """
    CREATE TABLE IF NOT EXISTS habits (                                     -- Create the table storing habits data if it does not already exist
        id INTEGER PRIMARY KEY AUTOINCREMENT,                               -- Unique identifier for each habit, which automatically increments
        name TEXT NOT NULL UNIQUE,                                          -- Name of the habit, unique and must exist
        frequency TEXT NOT NULL CHECK(frequency IN ('daily', 'weekly')),    -- Periodicity of the habit, either daily or weekly
        created_at TEXT NOT NULL,                                           -- Date of the habit creation
        streak INTEGER DEFAULT 0,                                           -- Initialization of the current streak at 0
        longest_streak INTEGER DEFAULT 0                                    -- Initialization of the longest streak ever achieved at 0
    )
    """)

    query.execute(
    """
    CREATE TABLE IF NOT EXISTS habit_logs (             -- Create the table storing habits completion logs if it does not already exist
        id INTEGER PRIMARY KEY AUTOINCREMENT,           
        habit_id INTEGER NOT NULL,                      -- Reference to the habit the log is associated to
        completed_at TEXT NOT NULL,                     -- Completion date of the habit
        UNIQUE(habit_id, completed_at),                 -- Prevent duplicate completions for the same habit in the same period
        FOREIGN KEY(habit_id) REFERENCES habits(id)     -- Link between a log entry and its parent habit in the habits table
    )
    """)

    connection.commit()         # Save both tables to the database
    return connection, query    # Return the connection and cursor



# ------------------------ #
# --- Helper functions --- #
# ------------------------ #



def get_current(frequency):

    """
    Purpose: convert the current date in the habit corresponding frequency
    Argument: frequency (str), either daily or weekly
    Return: a string representing the current period
    """

    today = date.today()            # Retrieve the date of today
                    
    if frequency == "daily":                  
        return today.isoformat()    # Return today in YYYY-MM-DD format            

    elif frequency == "weekly":                 
        year, week, _ = today.isocalendar()     # Retrieve the current year and week number     
        return f"{year}-W{week}"                # Return the current week in YYYY-Www format     



def get_previous_period(frequency):
    """
    Purpose: retrieve the previous period relative to today based on the habit frequency
    Parameters: frequency (str), either daily or weekly
    Returns: a string representing the previous period.
    """

    today = date.today()

    if frequency == "daily":
        yesterday = today - timedelta(days=1)       # Subtract one day
        return yesterday.isoformat()                # Return yesterday in YYYY-MM-DD format

    elif frequency == "weekly":
        last_week = today - timedelta(weeks=1)      # Subtract one week
        year, week, _ = last_week.isocalendar()     # Retrieve the year and week number of last week
        return f"{year}-W{week}"                    # Return last week in YYYY-Www format



# ------------------------------------------- #
# --- Predefined habits and tracking data --- #
# ------------------------------------------- #



def insert_test_data(cursor, conn):
    """
    Purpose: insert 5 predefined habits and 35 days of previous tracking data from today.
    35 days was chosen to ensure the last four complete weeks are always covered regardless of the current day of the week.
    Parameters: cursor and connection to update and save changes to the database
    """

    today = date.today()

    def days_ago(n):                                    # Return a daily date n days before today
        return (today - timedelta(days=n)).isoformat()  # Subtract n days and return the date correctly formatted

    def weeks_ago(n):                   # Return a weekly date n weeks before today
        d = today - timedelta(weeks=n)  # Subtract n weeks from today
        year, week, _ = d.isocalendar()
        return f"{year}-W{week}"

    cursor.execute(
        """
        INSERT OR IGNORE INTO habits (name, frequency, created_at, streak, longest_streak)
        VALUES
            ('test habit: drink water', 'daily',  ?, 5, 7),
            ('test habit: read',        'daily',  ?, 2, 3),
            ('test habit: exercise',    'daily',  ?, 0, 2),
            ('test habit: clean room',  'weekly', ?, 4, 5),
            ('test habit: review budget','weekly',?, 0, 2)
        """,
        (days_ago(35), days_ago(35), days_ago(35), weeks_ago(5), weeks_ago(5))   # Set the creation date to 35 days ago for all habits
    )

    # drink water habit with a current streak of 5
    for n in [0, 1, 2, 3, 4, 6, 8, 9, 11, 13, 14, 15, 17, 19, 20, 22, 24, 25, 27, 29, 30, 32, 34, 35]:
        cursor.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_at) VALUES ((SELECT id FROM habits WHERE name = 'test habit: drink water'), ?)",
            (days_ago(n),)  # Insert a completion for each n days ago
        )

    # read habit with a current streak of 2
    for n in [0, 1, 5, 7, 8, 14, 15, 21, 22, 27, 30, 32, 35]:
        cursor.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_at) VALUES ((SELECT id FROM habits WHERE name = 'test habit: read'), ?)",
            (days_ago(n),)
        )

    # exercise habit with a broken streak (0)
    for n in [3, 10, 17, 25, 32]:
        cursor.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_at) VALUES ((SELECT id FROM habits WHERE name = 'test habit: exercise'), ?)",
            (days_ago(n),)
        )

    # clean room habit with a current streak of 4
    for n in [0, 1, 2, 3, 4]:
        cursor.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_at) VALUES ((SELECT id FROM habits WHERE name = 'test habit: clean room'), ?)",
            (weeks_ago(n),)
        )

    # review budget habit with a broken streak (0)
    for n in [0, 2, 4]:
        cursor.execute(
            "INSERT OR IGNORE INTO habit_logs (habit_id, completed_at) VALUES ((SELECT id FROM habits WHERE name = 'test habit: review budget'), ?)",
            (weeks_ago(n),)
        )

    conn.commit()



def remove_test_data(cursor, conn):
    """
    Purpose: remove the predefined habits and their logs from the database
    """
    
    test_habits = (         # Tuple of the predefined habit names to remove
        "test habit: drink water",
        "test habit: read",
        "test habit: exercise",
        "test habit: clean room",
        "test habit: review budget"
    )

    cursor.execute(         # Delete associated logs
        """
        DELETE FROM habit_logs 
        WHERE habit_id IN (
            SELECT id
            FROM habits
            WHERE name IN (?, ?, ?, ?, ?)
        )
        """,
        test_habits
    )

    cursor.execute(         # Delete habits
        """
        DELETE FROM habits
        WHERE name IN (?, ?, ?, ?, ?)
        """,
        test_habits
    )

    conn.commit()



def toggle_test_data(cursor, conn):
    """
    Purpose: insert test data if not present, if present remove it
    """

    cursor.execute(
    "SELECT COUNT(*) FROM habits WHERE name IN ('test habit: drink water', 'test habit: read', 'test habit: exercise', 'test habit: clean room', 'test habit: review budget')"
    )                                                # Check how many of the 5 predefined habits are already inserted
    already_inserted = cursor.fetchone()[0] == 5     # True only if all 5 predefined habits are present

    if already_inserted:                
        remove_test_data(cursor, conn)
        print("Predefined test habits and logs removed successfully!")
    else:
        insert_test_data(cursor, conn)
        print("Predefined test habits and logs inserted successfully!")



# --------------------------------------- #
# --- Core habit management functions --- #
# --------------------------------------- #



def create_habit(cursor, conn):     
    """
    Purpose: prompt the user to create a new habit
    """

    name = input("Enter the habit's name: ").strip().lower()                        # Prompt the user to enter a habit name, remove any whitespaces and convert it to lowercases
    frequency = input("Enter its periodicity (daily/weekly): ").lower().strip()     # Prompt the user to select the habit frequency (either daily or weekly)

    if frequency not in ["daily", "weekly"]:                    # If the frequency entered by the user does not correspond to what can be chosen
        print("Please select between daily or weekly.")         # An error message is outputed
        return                                                  # The fucntion is exited

    created_at = get_current(frequency)                      # The current frequency is passed as an argument to the helper function, created_at will store the day of calling formated date

    habit = Habit(name=name, frequency=frequency, created_at=created_at, streak=0)      # Create a habit object and assign the corresponding values to its attributes

    try:                            # Attempt to insert the new habit into the database     
        cursor.execute(
            "INSERT INTO habits (name, frequency, created_at) VALUES (?, ?, ?)",
            (habit.name, habit.frequency, habit.created_at)
        )

        conn.commit()        
        print("New habit created successfully!")    # Display a success message to the user

    except sqlite3.IntegrityError:  # Catch a database integrity error (for instance duplicate name)
        print("An error has occurred. \nPlease verify that a habit does not already exist with the same information.")     # Display an error message to the user



def delete_habit(cursor, conn):
    """
    Purpose: prompt the user to select the habit to stop tracking (delete)
    """

    habits = view_habits(cursor)    # Call the function to display all currently tracked habits

    if not habits:  # If no habits are tracked
        return      # The function is exited

    else :          # If there are indeed habits tracked
        habit_name = input("\nEnter the name of the habit to stop tracking: ").strip().lower() # The user is prompted to enter the name of the habit to delete

        cursor.execute(     # Delete all logs associated with the habit
            "DELETE FROM habit_logs WHERE habit_id = (SELECT id FROM habits WHERE name = ?)",
            (habit_name,)
        )

        cursor.execute(     # Delete the habit matching the entered name from the database
            "DELETE FROM habits WHERE name = ?",
            (habit_name,)
        )

        conn.commit()   

        if cursor.rowcount == 0:                    # If no habit correspond to the entered name
            print("No habit found with that name.") # The corresponding error message is displayed

        else:                                       # If a habit correspond to the entered name and was thus deleted
            print("Habit deleted successfully.")    # The corresponding success message is displayed



def mark_habit_done(cursor, conn):
    """
    Purpose: prompt the user to select the habit to mark as done
    """

    habits = view_habits(cursor)  # Display the currently tracked habits

    if not habits:  
        return      

    else:         
        habit_name = input("\nEnter the name of the habit you have completed: ").strip().lower() 

        cursor.execute(     # Retrieve the habit matching the entered name
            "SELECT id, name, frequency, streak FROM habits WHERE name = ?",
            (habit_name,)
        )

        habit = cursor.fetchone()   # The habit details are stored in a temporary variable

        if habit is None:   # If no habit correspond to the entered name
            print("No habit was found with the given name.")    # A corresponding message is outputed
            return                                              # The function is exited

        habit_id, name, frequency, streak = habit           # The habit details are unpacked

        completed_at = get_current(frequency)               # Request and store the current completion date 
        previous_period = get_previous_period(frequency)    # Request and store the previous period date 
    
        try:

            cursor.execute(     # Store the current completion period in the habit_logs table
                "INSERT INTO habit_logs (habit_id, completed_at) VALUES (?, ?)",
                (habit_id, completed_at)
            )

            cursor.execute(     # Check if the habit was completed during the previous period
                """
                SELECT 1 FROM habit_logs
                WHERE habit_id = ? AND completed_at = ?
                """,
                (habit_id, previous_period)
            )

            previous_done = cursor.fetchone()

            if previous_done:               # If the habit has been completed in the previous period
                new_streak = streak + 1     # Its streak is increased by one

            else:                           # If the habit has not been completed in the previous period (the streak has been broken)
                new_streak = 1              # The streak is reseted to one

            cursor.execute(     # The current and longest streak values are updated accordingly
                """
                UPDATE habits
                SET streak = ?,
                longest_streak = MAX(longest_streak, ?)
                WHERE id = ?
                """,
                (new_streak, new_streak, habit_id)
            )

            conn.commit()

            print(f"The habit '{name}' was marked as done for {completed_at}.")

        except sqlite3.IntegrityError:  # If the habit was already marked as completed for this period
            print(f"The habit '{name}' is already marked as done for {completed_at}.")  # The corresponding message is displayed



# --------------------------------- #
# --- Analysis module functions --- #
# --------------------------------- #



def view_habits(cursor):
    """
    Purpose: display all currently tracked habits from the database.
    """

    cursor.execute("SELECT name, frequency, created_at FROM habits")    # Retrieve all habits and their details
    habits = cursor.fetchall()  # Store each row of the table in a temporary variable

    if not habits:                             
        print("No habits currently tracked.")  
        return []                               

    else:                                               # If there are indeed habits currently tracked
        print("\nYou are currently tracking:\n") 
        for name, frequency, created_at in habits:      # Loop through all habits and unpack each value
            print(f"{name} - {frequency} (created on {created_at}).")  # Each habit is outputed
        return habits



def same_periodicity_habits(cursor):
    """
    Purpose: prompt the user to select a frequency and display all habits matching it.
    """  

    frequency_habit = input("\nEnter the periodicity of the habits you want to retrieve (daily/weekly):").strip().lower()    # Prompt the user to enter the desired periodicity
    cursor.execute(     # Retrieve the habits matching the entered frequency
        "SELECT name, created_at, streak, longest_streak FROM habits WHERE frequency = ?",
        (frequency_habit,)
    )

    habits = cursor.fetchall()  # Store all matching habits in a temporary variable

    if not habits:                             
        print("No habits currently tracked.")   
        return []                               
    
    else:                       # If at least one habit is tracked with the given periodicity
        print(f"\n{frequency_habit} habit(s):\n")
        for name, created_at, streak, longest_streak in habits:
            print(f"{name} - created on {created_at} - "f"current streak: {streak} - "f"longest streak: {longest_streak}")
        return habits



def current_longest_streak(cursor):
    """
    Purpose: retrieve the habit with the highest current streak for both daily and weekly habits.
    If multiple habits share the longest streak, they will all be displayed.
    """

    cursor.execute(
        """
        SELECT name, streak
        FROM habits
        WHERE frequency = 'daily'       -- Filter daily habits only
        AND streak = (SELECT MAX(streak) FROM habits WHERE frequency = 'daily')     -- Match the highest streak among daily habits
        """
    )
    # Retrieve all the daily habits sharing the highest current streak

    daily_result = cursor.fetchall()    # Store results in a temporary variable

    cursor.execute(
        """
        SELECT name, streak
        FROM habits
        WHERE frequency = 'weekly'      -- Filter weekly habits only
        AND streak = (SELECT MAX(streak) FROM habits WHERE frequency = 'weekly')    -- Match the highest streak among weekly habits
        """
    )
    # Retrieve all the weekly habits sharing the highest current streak

    weekly_result = cursor.fetchall()   # Store results in a temporary variable

    print("\nLongest streaks:\n")

    if daily_result:                                                        # If at least one daily habit is tracked
        print(f"Longest daily streak: {daily_result[0][1]} day(s).")        # Print the streak duration
        for name, streak in daily_result:                                   # Loop through all habits sharing the top streak
            print(f"  - {name}")                                            # Print the habit name
    else:                                                                   # If no daily habit is tracked
        print("No daily habits currently tracked.")                         # The user is informed with a message                

    if weekly_result:
        print(f"Longest weekly streak: {weekly_result[0][1]} week(s).")
        for name, streak in weekly_result:
            print(f"  - {name}")
    else:
        print("No weekly habits currently tracked.")



def specific_longest_streak(cursor):    
    """
    Purpose: prompt the user to select a habit to display its longest ever achieved streak.
    """

    habits = view_habits(cursor)  # Display all currently tracked habits

    if not habits:  # If no habits are tracked
        return      # The function is exited

    else:           # If at least one habit is tracked
        habit_name = input("\nEnter the name of the habit you want to see the longest streak: ").strip().lower()    # Prompt the user to enter the name of the desired habit

        cursor.execute(
            "SELECT longest_streak, frequency FROM habits WHERE name = ?",  # Retrieve the longest streak and frequency of the habit
            (habit_name,)
        )

        result = cursor.fetchone()  # Store the result in a temporary variable

        if result is None:                              # If no habit matches the entered name
            print("No habit found with that name.")     # The user is informed
            return

        else:                                           # If a habit matches the entered name
            longest_streak, frequency  = result         # The longest streak and frequency are unpacked

        if frequency == "daily":    # If the habit is daily
            print(f"The longest streak for the {habit_name} habit is {longest_streak} day(s).")
        else:                       # If the habit is weekly
            print(f"The longest streak for the {habit_name} habit is {longest_streak} week(s).")



def struggle_last_four_weeks(cursor):
    """
    Purpose: retrieve and display the least completed daily and weekly habit during the previous four complete weeks (excluding the current week).
    If multiple habits share the lowest completion count, they will all be displayed.
    """

    end_date = (date.today() - timedelta(days=date.today().isocalendar()[2])).isoformat()           # Last Sunday (end of previous week)
    start_date = (date.today() - timedelta(days=date.today().isocalendar()[2] + 27)).isoformat()    # 28 days before that

    cursor.execute(
        """
        WITH daily_counts AS (
            SELECT habits.name, COUNT(habit_logs.id) AS completion_count    -- Count completions per daily habit last four weeks
            FROM habits
            LEFT JOIN habit_logs
            ON habits.id = habit_logs.habit_id
            AND habit_logs.completed_at BETWEEN ? AND ?                     -- Only count completions within last four weeks
            WHERE habits.frequency = 'daily'                                -- Only count completions for daily habits
            GROUP BY habits.id
        )
        SELECT name, completion_count
        FROM daily_counts
        WHERE completion_count = (SELECT MIN(completion_count) FROM daily_counts)   -- Keep only habits with the lowest count
        """,
        (start_date, end_date)          # Pass the date range calculated above
    )

    daily_result = cursor.fetchall()    # Store all matching habits in a temporary variable

    last_four_weeks = []                            # Build a list of the previous four ISO week strings 
    for n in range(1, 5):                           # Loop through the last 4 complete weeks (excluding current week)
        d = date.today() - timedelta(weeks=n)       # Compute the date n weeks ago
        year, week, _ = d.isocalendar()             # Retrieve the year and week number of that date
        last_four_weeks.append(f"{year}-W{week}")   # Add the formatted ISO week string to the list

    placeholders = ",".join(["?"] * len(last_four_weeks))      # Generate a placeholder for each week

    cursor.execute(
    f"""
    WITH weekly_counts AS (
        SELECT habits.name, COUNT(habit_logs.id) AS completion_count            -- Count completions per weekly habit over the last four weeks
        FROM habits
        LEFT JOIN habit_logs
        ON habits.id = habit_logs.habit_id
        AND habit_logs.completed_at IN ({placeholders})                         -- Only count completions within the last four weeks
        WHERE habits.frequency = 'weekly'                                       -- Filter to weekly habits only
        GROUP BY habits.id
    )
    SELECT name, completion_count
    FROM weekly_counts
    WHERE completion_count = (SELECT MIN(completion_count) FROM weekly_counts)  -- Keep only habits with the lowest count
    """,
    last_four_weeks       # Pass the list of the last four ISO weeks
    )

    weekly_result = cursor.fetchall()          

    print("\nHabits struggled the most within the last four complete weeks:\n")

    if daily_result:                            # If at least one daily habit has data
        print(f"Daily habit(s) with the lowest completion count: {daily_result[0][1]} daily completion(s)")
        for name, count in daily_result:        # Loop through all habits sharing the lowest count
            print(f"  - {name}")
    else:
        print("No daily habit data available.")

    if weekly_result:                           # If at least one weekly habit has data
        print(f"Weekly habit(s) with the lowest completion count: {weekly_result[0][1]} weekly completion(s)")
        for name, count in weekly_result:       # Loop through all habits sharing the lowest count
            print(f"  - {name}")
    else:
        print("No weekly habit data available.")



# ----------------------------------------------- #
# --- Command-line interface module functions --- #
# ----------------------------------------------- #



def analysis_menu(cursor):
    """
    Purpose: display the analysis menu and link to the corresponding analysis function.
        """
    while True:
        print("\nAnalysis Menu\n")
        print("Enter   'Preview'       to see currently tracked habits")
        print("Enter   'Periodicity'   to see habits with the same periodicity")
        print("Enter   'Streak'        to see the current longest streak across all habits")
        print("Enter   'Habit'         to see the longest streak achieved of a desired habit")
        print("Enter   'Struggle'      to see the habit you struggled the most within the last four weeks")
        print("Enter   'Back'          to return to the main menu")

        choice = input("\nPlease enter your desired keyword: ").strip().lower()     # Prompt the user to enter a keyword

        if choice == "preview":
            view_habits(cursor)                     # Display all tracked habits
        elif choice == "periodicity":
            same_periodicity_habits(cursor)         # Display habits with the same frequency
        elif choice == "streak":
            current_longest_streak(cursor)          # Display the habit with the highest current streak
        elif choice == "habit":
            specific_longest_streak(cursor)         # Display the longest streak ever achieved of a specific habit
        elif choice == "struggle":
            struggle_last_four_weeks(cursor)        # Display the least completed habit over the last four complete weeks
        elif choice == "back":
            break                                   # Exit the analysis menu and return to the main menu
        else:
            print("Invalid option, please verify your input.")      # Display an error message for unrecognised keywords

def main():
    """
    Purpose: launch the application, connect to the database and display the main menu.
    """

    conn, cursor = connect_db()     # Connect to the database

    while True:
        print("\nHabit Tracker Command Line Interface\n")

        print("Enter   'Create'     to start tracking a habit")
        print("Enter   'Delete'     to stop tracking a habit")
        print("Enter   'Complete'   to mark a habit as done")       
        print("Enter   'Analysis'   to access the analysis module")
        print("\nEnter   'Test'       to insert or remove predefined test habits")
        print("Enter   'Exit'       to exit the program")

        choice = input("\nPlease enter your desired keyword: ").strip().lower()

        if choice == "test":
            toggle_test_data(cursor, conn)          # Insert or remove the predefined test habits and logs
        elif choice == "create":
            create_habit(cursor, conn)              # Start tracking a new habit
        elif choice == "delete":
            delete_habit(cursor, conn)              # Stop tracking an existing habit
        elif choice == "complete":
            mark_habit_done(cursor, conn)           # Mark a habit as completed/done for the current period
        elif choice == "analysis":
            analysis_menu(cursor)                   # Access the analysis module
        elif choice == "exit":
            conn.close()                            # Close the database connection
            break                                   # Exit the program
        else:
            print("Invalid option, please verify your input.")

if __name__ == "__main__":
    main()                                          # Launch the application