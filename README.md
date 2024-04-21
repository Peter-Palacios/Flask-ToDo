
# Final Project – To-Do List – Flask & Mabl Research


### Program Functionalities (with applicable Flask usages, as well as Mabl tesing possibilities):
**Task Management:**
- Actions:
  - Users can add new tasks to their to-do list, or delete existing ones.
  - Each task can include notes.
  - Users can specify due dates for tasks.
- Flask:
    -  Create routes for adding/deleting/completing tasks.
    - Use “Flask forms” to handle user-input for adding/deleting/completing tasks.
- Mabl:
    - Verify tasks are successfully created/deleted/completed.

**List Management:**
- Users can view their list of tasks:
  - Displayed with titles, details, notes, & due dates.
- Flask:
  - Use the routes to display user’s list of tasks.
-Mabl:
  - Confirm tasks are displayed correctly after being created.

**Search & Filter Functionality:**
- Actions:
    - Users can filter by due dates, completion status, or keyword(s).
- SQL:
  - Use SQL queries to filter, using user-input.
- Mabl:
  - Verify that the displayed tasks match specified criteria.

**User Authentication:**
- Users can create an account, log in, & log out. Only users with an account can access/use the to-do list program.
-   Flask:
  - “Flask-Login” extension:
- Manages user sessions and authentication.
- Stores user info in an SQLite database. Use “Flask-SQLAlchemy” to interact with the database.
- Mabl:
  - Verify user accounts are created successfully.
  - Test situations like incorrect login credentials, or successful registry.
