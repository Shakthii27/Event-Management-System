## Event Management System 
- This project is an MVP for an Event Management System, built using Python (Flask) and SQL.  
- It allows users to create accounts, manage events, generate shareable registration links, and collect participant details and store it in database. 
- The application uses a modern user interface to make the experience visually engaging, while keeping the backend logic simple and easy to understand.  

## Overview 
- The system supports user authentication, where users can either log in with an existing account or create a new account from the same page.
- Authentication is handled using Flask sessions, ensuring that only logged-in users can access the dashboard and create events.  
- Once logged in, users can create events by providing basic details such as the event name, date, time, and venue.
- These events are stored consequently in an SQL database and can be viewed anytime from the dashboard or the View Events page.  
- Each event automatically generates a unique, shareable registration link. This link can be sent to participants, who can register for the event without needing to create an account.
- Participants provide their name, phone number, and email address, which are then stored securely in the database.  
- After successful registration, participants are shown a clear confirmation page indicating that their spot has been reserved.  
