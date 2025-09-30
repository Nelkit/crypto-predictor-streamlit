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
36120-25sp-group6-at3-streamlit/
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

## How to Setup
1. Clone this repository to your local machine:
   ```bash
   git clone https://github.com/Nelkit/36120-25sp-group6-at3-streamlit
   cd 36120-25sp-group6-at3-streamlit
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

## How to Run the Program
Run the following command in your terminal:
```bash
streamlit run app/main.py
```
This will launch the Streamlit app in your default web browser. Follow the on-screen instructions to perform currency conversions.