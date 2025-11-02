# AMLA-AT3-Crypto Streamlit App (Group 6)
> Streamlit application for visualizing cryptocurrency data and ML predictions (AMLA AT3)
> 
--------

## 🧩 Project Overview

This repository contains a Streamlit app for displaying historical and predictive information about selected cryptocurrencies: Bitcoin, Ethereum, XRP, and Solana.  

Each student in the group contributes a separate tab showing their selected data and ML model predictions. The app fetches historical data via API calls and uses pre-trained ML models to predict the next-day HIGH price for each token.

The goal is to provide an interactive dashboard that integrates data visualization and machine learning predictions, ready for deployment.

--------

## 🗂 Repository Structure

```
36120-25SP-group6-AT3-streamlit/
│
├── app/
│   └── main.py              # Main Streamlit application code
│
├── students/
│   ├── student1.py          # Streamlit components and logic for Student 1
│   ├── student2.py          # Streamlit components and logic for Student 2
│   ├── student3.py          # Streamlit components and logic for Student 3
│   └── student4.py          # Streamlit components and logic for Student 4
│
├── pyproject.toml           # Python project configuration and dependencies
├── requirements.txt         # List of Python packages to install
├── Dockerfile               # Docker instructions to build and run the Streamlit app
└── github.txt               # Link to the Github repository for the app
```

## 🧑‍💻 How to Setup
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/Nelkit/36120-25SP-group6-AT3-streamlit
   cd 36120-25SP-group6-AT3-streamlit
   ```
2. Ensure you have Python 3.11 or later installed. You can use Python 3.11.4 with pyenv:
   ```bash
   pyenv install 3.11.4
   pyenv local 3.11.4
   ```
   
3. Install Poetry (if not installed)
    ``` bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

4. Install dependencies using Poetry:
   ```bash
   poetry install
   ```
   Or, if using pip:
   ```bash
   pip install -r requirements.txt
   ```
5. (Optional) Activate your virtual environment if not already active.
    ```bash
    poetry env activate
    ```

## 🚀 How to Run the Program
Run the following command in your terminal:
```bash
streamlit run app/main.py
```
This will launch the Streamlit app in your default web browser.

## 🧪 Testing
To run the test suite for the Ethereum module:

### Run all tests

```bash
poetry run pytest test_ethereum.py
```

### Run with verbosity

```bash
poetry run pytest test_ethereum.py -v
```

### Run with coverage

```bash
poetry run pytest test_ethereum.py --cov=students/ethereum --cov-report=html
```

### Run a specific test class

```bash
poetry run pytest test_ethereum.py::TestHelpers -v
```

## 🐳 Docker Deployment
To run the app using Docker:

1. Build the Docker image:
   ```bash
   docker build -t crypto-dashboard .
   ```

2. Run the container:
   ```bash
   docker run -p 80:80 crypto-dashboard
   ```

The app will be available at http://localhost:80.

## 📂 Branching Strategy

To keep our work organized, each student will create their own branch to work on their assigned cryptocurrency.

### Rules

1. **Main branch (`main`)**  
   - Contains the stable version of the app.  
   - Do not develop directly on this branch.
2. **Individual branches**  
   - Each student creates a branch from `main` using this format:  
     ```
     <name>-<cryptocurrency>
     ```
     Example: `nelkit-ethereum`

### Workflow
1. Create your branch from main:

    ```
    git checkout main
    git pull origin main
    git checkout -b nelkit-ethereum
    ```
2. Work on your assigned section (students/student_<student_id>.py).
3. Commit changes frequently with clear messages.
4. Push your branch and open a Pull Request (PR) to main.
5. Team member reviews and approves the PR before merging.

> Tip: Keep your branch up to date with main before merging to avoid conflicts.