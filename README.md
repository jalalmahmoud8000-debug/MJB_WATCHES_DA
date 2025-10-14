# MJB Watch Store

## Project Description

MJB Watch Store is a web application for an online watch store, built using the Django framework in Python. This project aims to provide a robust and scalable e-commerce platform.

## Local Development Setup

This project is configured to run in a Nix-based environment, such as the one provided by Firebase Studio.

1.  **Clone the Repository:**
    ```bash
    git clone <YOUR_REPOSITORY_URL>
    cd <repository-folder>
    ```

2.  **Environment Setup:**
    Opening the project in a compatible IDE will automatically set up the Python virtual environment in a `.venv` directory and install the required dependencies from `mysite/requirements.txt`.

3.  **Activate the Virtual Environment:**
    Before running any Python or Django commands directly in the terminal, you must activate the virtual environment:
    ```bash
    source .venv/bin/activate
    ```

4.  **Database Migrations:**
    Apply the initial database migrations to set up your database schema:
    ```bash
    python mysite/manage.py migrate
    ```

5.  **Run the Development Server:**
    You can start the Django development server using the provided script:
    ```bash
    ./devserver.sh
    ```
    Alternatively, you can use the `web` preview task in your IDE.

## Important Scripts

*   `./devserver.sh`: This script starts the Django development server on the correct port for local development and previewing.
*   `mysite/manage.py`: This is Django's command-line utility for administrative tasks. It is used for running migrations, creating a superuser, running tests, and more.
    *   **Create a superuser:** `python mysite/manage.py createsuperuser`
    *   **Run tests:** `python mysite/manage.py test`
