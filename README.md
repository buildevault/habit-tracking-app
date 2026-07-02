# Habit Tracking Application

The proposed solution is a reliable command-line interface habit tracking application built with Python and SQLite. Its purpose is to track daily and weekly habits, monitor the streaks, and gain meaningful insights on habit adoption and progress over time.

---

## Requirements

- Python 3.7 or later.
- pytest (only required to run the unit test suite).

---

## Installation

The app uses the following standard library modules (no installation needed):

- sqlite3
- dataclasses
- datetime
- typing

In order to run the tests, pytest should be installed thanks to the following command:

```
python3 -m pip install pytest
```

---

## Running the app

In your terminal, navigate to the folder containing the files and run:

```
python3 app.py
```

The main menu will automatically open as follows:

```
Habit Tracker Command Line Interface

Enter   'Create'     to start tracking a habit
Enter   'Delete'     to stop tracking a habit
Enter   'Complete'   to mark a habit as done
Enter   'Analysis'   to access the analysis module

Enter   'Test'       to insert or remove predefined test habits
Enter   'Exit'       to exit the program
```

Then, type any of the listed keywords and press enter to navigate to the corresponding feature.

---

## Managing habits

### Create a habit
1. From the main menu, type `Create` and press enter.
2. Enter a name for your habit.
3. Enter its periodicity: `daily` or `weekly`.

The habit is saved and will persist across sessions.

### Delete a habit
1. From the main menu, type `Delete` and press enter.
2. The list of currently tracked habits will be displayed.
3. Enter the name of the habit you want to stop tracking.

The habit and its associated logs will be removed.

### Complete a habit and streak calculation
1. From the main menu, type `Complete` and press enter.
2. The list of currently tracked habits will be displayed.
3. Enter the name of the habit you have completed.

Your streak will be updated automatically.

- If you completed the habit in the previous period, your streak increases by 1.
- If you missed the previous period, your streak resets to 1.
- If you have already completed the habit in the given period, an error message is displayed.

---

## The analysis module

From the main menu, type `Analysis` to open the analysis menu. The analysis menu is composed of five features as well as the ability to return to the main menu. Navigation relies on the same principle as accessing the default features. Type any of the listed keywords and press enter to navigate.

The table below shows a description of each available feature in the analysis module:

| Keyword       | Description                                                      |
| ------------- | ---------------------------------------------------------------- |
| `Preview`     | List all currently tracked habits                                |
| `Periodicity` | List all habits with the same periodicity                        |
| `Streak`      | Show the longest current streak across all habits                |
| `Habit`       | Show the longest streak ever achieved for a given habit          |
| `Struggle`    | Show the habit you struggled the most within the last four weeks |
| `Back`        | Return to the main menu                                          |

---

## Predefined habits

The app ships with five test habits with four previous weeks of tracking data. 

- From the main menu, type `Test` to insert them.
- Then, type `Test` again to remove them. 

These predefined habits serve a dual purpose. First, they allow the user to test the app and explore its features. Additionally, those habits are used when running the unit test suite.

---

## Unit test suite

In order to run the unit test suite:

1. Ensure you are located in the folder containing both the app.py and apptest.py files in your terminal.
2. Ensure pytest is installed as previosuly mentioned.

Then, run:

```
python3 -m pytest apptest.py -v
```

The apptest file will automatically use the predefined habits for testing purposes.
Each line in the output shows the test name and whether it passed or failed.

---

## Data persistence

All habit data is automatically saved to a local SQLite database file named `habits.db` and will persist between sessions. This means that closing and reopening the application will not affect the history of the tracked habits.

---

## Project structure

The project is structured on the following architecture:

```
habit-tracking-app/
├── app.py          # Main application
├── apptest.py      # Unit test suite
├── habits.db       # SQLite database (created automatically on first run)
└── README.md       # Current file
```
