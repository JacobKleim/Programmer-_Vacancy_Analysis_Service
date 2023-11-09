# Programmer_Vacancy_Analysis_Service

# Project Description
   This service allows you to get an average salary for programming languages using statistics collected on Headhunter and SuperJob.

## Technologies and tools
 - Python 3.9.10

## How to use
1. Clone this repository and go to the project folder:
   ```bash
   cd /c/project_folder # for example
   ```
   ```bash
   git clone github.com/JacobKleim/Programmer_Vacancy_Analysis_Service
   ```
   ```bash
   cd /c/project_folder/Programmer_Vacancy_Analysis_Service
   ```

2. Create a .env file with parameters:
   ```
   SJ_TOKEN=Secret key for your SJ account
   ```
   
3. Сreate and activate a virtual environment:
   ```
   python -m venv venv
   ```
   ```bash
   source venv/Scripts/activate
   ```

4. Install dependencies:
   ```
   python -m pip install --upgrade pip
   ```
   ```
   pip install -r requirements.txt
   ```

5. Start the project:
   
   ```
   python programming_languages_salary.py
   ```