## Event Management System

- The Event Management System is a web-based project developed using Python (Flask) for the backend and Supabase (PostgreSQL) for database management.
- It is designed to streamline event creation, registration, and participant management while providing a visually engaging and interactive user interface.
- The system combines a clean frontend experience with a structured backend workflow, enabling organisers to create events, generate registration links, and manage participants efficiently.

## Overview

- The system supports user authentication, allowing users to sign up and log in to access a personalized dashboard. By default, users are registered as participants, with the option to upgrade to an organiser role from the profile section. User data and event information are securely stored in a Supabase-hosted PostgreSQL database.
- Logged-in users can create events by entering essential details such as event name, date, time, and venue. Once created, events automatically appear on the dashboard under the “All Events” section. Each event generates a unique, shareable registration link that can be distributed to participants.
- Participants can register for an event without creating an account by simply providing their email address. Upon successful registration, the system generates a unique ticket ID and a QR code. This QR code, along with the event details, is emailed to the participant and can be used for verification during the event.
- Additional features include a profile section for viewing user information and upgrading roles, secure logout functionality, and an interactive chatbot integrated into the interface to enhance user engagement. All registrations, events, and user interactions are managed through Supabase, ensuring reliable data storage and accessibility.
