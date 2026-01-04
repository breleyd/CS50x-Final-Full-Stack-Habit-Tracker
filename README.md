# Habit Flow
#### Video Demo:  <[https://youtu.be/bW3pX-LRzHI]>
#### Description: HabitFlow is a progressive habit tracker that goes beyond binary "done or not done" habit tracking. It emphasizes visuals and tracks the extent (e.g., duration) of habits, offering a more sustainable approach to habit creation and elimination.

## Table of Contents
- [Features](#features)
- [File Descriptions](#file-descriptions)
- [Backend Logic Overview](#backend-logic-overview)
- [Design Choices](#design-choices)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Acknowledgments](#acknowledgments)

## Features

- **Visual Habit Tracking**:
- Users can track their habits over time by logging the duration of each habit. This offers a more detailed, long-term approach to habit creation and elimination, as opposed to simply marking whether the habit was completed or not.

- **Habit Management**:
  - Users can **add**, **update**, and **remove** habits. They can:
    - Add new habits to their list.
- Update the progress of their habits by logging the duration and date the habit was logged.
    - Remove habits they no longer wish to track.

- **User Authentication**:
- Users can create their accounts to let the data of habits to be private and secure, so each user will be able to view, access, and manipulate only their own habits in a private manner.

## File Descriptions

### Backend files
- **`app.py`**: The backend for HabitFlow is built using Flask (Python) and SQLite. It handles user authentication, data management, and interaction with the database for storing, retrieving, and visualizing habit data. The backend exposes various routes that facilitate these functionalities while maintaining security and scalability.
- **`helpers.py`**: Contains a helper function for validation purposes.
- **`project.db`**: The SQLite database that stores all of the data in HabitFlow. This includes user authentication details and data regarding the user's habit tracking.
    - **Users Table**: Stores the username and hashed password for each user.
    - **Habits Table**: Stores data regarding each user's habits, including the habit name, duration, and timestamp.
- **Habit List Table**: Stores a list of the habits that belong to each user.
- **`requirements.txt`**: Lists all the dependencies required to run the app. Install these dependencies using the command below.

### Frontend files
- **`add.html`**: This page is used for adding new habits to the user's list of habits tracked. It allows the user to enter in the name of the habit that they want to track, and then stores it in the database that corresponds with the user's account. It offers a form to easily create a new habit.
- **`graph.html`**: This page visually displays a graph of a user's habit data over time. It generates a plot showing the duration of the selected habit for each logged date. This graph helps users visually analyze their habit progress and see trends over time. The graph is dynamically generated using data from the database and rendered as an image in the template.
**`: `index.html`:` : the homepage of the application (users are routed directly into this after they've entered the application by clicking any of the other application routing urls within the application), giving it a list of a user's habits upon which they can detail or update progress and bring users to other pages including any for adding or deleting habit entries.
- **`layout.html`**: The base layout template for the whole application. It would include common HTML elements: header, footer, navigation bar. Other pages are made with extending this layout to be similar in structure for each of them: `add.html`, `graph.html`, etc. This template allows easy reusing of common design pieces across the app.
5. **`login.html`**: This page provides a user's ability to log in, that they authenticate themselves and access personal information about their habits. They are asked for the user-name and password, both will be checked against database info. If the log-on is successful, a person should be forwarded to a main page (`index.html`).
- **`register.html`**: This page allows new users to create an account. The user is prompted to input a username, password, and confirmation password. The application then hashes the password for security and stores the new user's information in the database. After successful registration, users are redirected to the login page.
- **`remove.html`**: This page allows users to delete certain habits from their habit tracking list. This page presents a form for the user to choose which habit they want to remove. After confirmation, the selected habit and its related data are deleted from the database.

- **`update.html`**: This is the HTML page that updates the Habit Tracker data. It has the functionality to log against a habit, recording duration and timestamp, and to edit information about a habit if necessary. The changes made to the habit can be saved to the database for future reference.

## Overall Backend Logic

The HabitFlow web application's backend is developed with Flask. It manages its database using SQLite through the CS50 library. The users of this application are able to log in, register, add and remove habits, and see their performance over time in graphical form.

### 1. Flask Configuration
- The application is configured with Flask, storing sessions in the filesystem and utilizing CS50's SQL library to interact with the SQLite database.
- `flask_session` handles session data for the purpose of maintaining user authentication status.

### 2. User Authentication
- **Login**: A user can log in by inputting their credentials - username and password. The password is matched against the hashed password stored in the database using `werkzeug.security`.
- **Logout**: A user can log out, which clears his/her session.
- **Registration**: Users can register an account with a username, password, and confirmation password. The password is hashed before it is stored.

### 3. Habit Management
- **Add Habit**: Users can add a habit by specifying the habit name. The habit will be saved into the database with the relationship to the user.
- **Delete Habit**: Users can remove a habit from the system. This removes all the data associated with that habit.
- **Update Habit**: Users can add data (duration and timestamp) for a habit. If the habit data already exists for a specific timestamp, it is not added again.

### 4. Displaying Habit Data (Graph)
- **Graph Creation**: Upon the selection of a habit by a user, the system pulls data for that habit (timestamp and duration). Use this data to create a graph using `matplotlib`.
    - Convert timestamps to `datetime` objects to ensure proper plotting.
    - Save the graph as a PNG image and encode it as a base64 string to embed it in the HTML.
- The graph is then shown at the frontend via an `<img>` tag.

### 5. Error Handling and Validation
- **User Input Validation**: All the user inputs (like username, password, habit name, duration, timestamp) are validated. Example:
    - Passwords should be minimum 8 characters long and must match the confirmation password.
- Names of habits cannot be empty and their durations must be positive numbers.
    - Timestamps are checked so that no duplicate data is created on the same day.
- **Error Responses**: In case any of the above validation fails, the appropriate error message is returned along with the response. These messages are shown on the frontend as and when required using Javascript.

### 6. Session Management
- `session` object: to store the `user_id` upon successful login and ensure that routes are available only to authenticated users.
- `@login_required` decorator: to protect routes from unauthorized access and redirect them to the login page.

### 7. Flask Routes
- **`/login`**: Handles login and redirects upon successful authentication.
- **`/logout`**: Clears the session and redirects to the login page.
- **`/register`**: Allows new users to create an account.
- **`/` (Home)**: Displays a form for the user to select a habit and view its data graph. On form submission, the habit's data is retrieved, processed, and plotted.
- **`/add`**: Allows the user to add a new habit.
- **`/remove`**: Allows the user to remove an existing habit.
- **`/update`**: Allows the user to update habit data (duration and timestamp).

### 8. Graph Rendering
- The graph is created using `matplotlib`:
    - The X-axis is the timestamp of the habit.
    - The Y-axis is the duration of the habit.
    - The graph dynamically adjusts to the range of data, with axis labels and date formatting for clarity.
- The graph image is encoded as a base64 string and embedded into the HTML template for display.

## Design Choices
- **Database**: The choice of a relational database (SQLite) was made to structure habit and user data in a clear, manageable way. To display the list of habits, a second table (`habit`) containing the names of the habits had to be used.

- **User authentication**: The application requires the users' password to be at least 8 characters in order to enhance the security of accounts.

- **Form Submissions**: To avoid SQL Injection attacks and errors, the input submitted by the forms are also verified from the server side. For instance, just using required attribute is not enough so there is a second layer of verification in `app.py`.

## Setup and Installation

Make sure to install the required dependencies for the backend to work correctly:

```bash
pip install -r requirements.txt
```
To run the application:
```Python
flask run
```
## Acknowledgements

- **Bulma**: Special thanks to [Bulma](https://bulma.io/) for providing a simple and responsive CSS framework.

- **ChatGPT**: Thanks to [ChatGPT](https://chat.openai.com/) for assisting with problem-solving, providing code examples, including the dynamic display of error messages with JavaScript and using matplotlib to plot the habit data graph.

