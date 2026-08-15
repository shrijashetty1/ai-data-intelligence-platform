# \# AI Data Intelligence Platform

# 

# An AI-powered natural language analytics platform that allows users to ask questions about business data in plain English and receive SQL queries, database results, and concise business insights.

# 

# \## Overview

# 

# The AI Data Intelligence Platform converts natural language questions into PostgreSQL queries using a local LLM, executes the generated SQL against a PostgreSQL database, and presents the results through a React-based web interface.

# 

# \### Example

# 

# A user can ask:

# 

# > What are the top 3 products by sales?

# 

# The platform:

# 

# 1\. Understands the natural language question

# 2\. Generates a PostgreSQL `SELECT` query

# 3\. Validates the generated SQL

# 4\. Executes the query against PostgreSQL

# 5\. Displays the query results

# 6\. Generates a concise business insight

# 

# \## Features

# 

# \- Natural language data queries

# \- AI-generated PostgreSQL SQL

# \- SQL safety validation

# \- PostgreSQL database integration

# \- Business insight generation

# \- React-based analytics interface

# \- Query result visualization

# \- Generated SQL display

# \- Copy SQL functionality

# \- Loading and error handling

# \- Local LLM inference using Ollama

# 

# \## Architecture

# 

# ```text

# User

# &#x20; |

# &#x20; v

# React Frontend

# &#x20; |

# &#x20; | HTTP Request

# &#x20; v

# FastAPI Backend

# &#x20; |

# &#x20; +--------------------+

# &#x20; |                    |

# &#x20; v                    v

# Ollama LLM          PostgreSQL

# &#x20; |                    |

# &#x20; |                    |

# &#x20; +--------+-----------+

# &#x20;          |

# &#x20;          v

# &#x20;     Query Results

# &#x20;          |

# &#x20;          v

# &#x20;   Business Insight

# &#x20;          |

# &#x20;          v

# &#x20;     React UI

Tech Stack

Frontend

React

Vite

JavaScript

CSS

Backend

Python

FastAPI

Uvicorn

LangChain

Ollama

Database

PostgreSQL

psycopg2

AI

Ollama

Qwen 3 1.7B

Project Structure

ai-data-intelligence-platform/

│

├── backend/

│   ├── app/

│   │   ├── ai\_service.py

│   │   ├── database.py

│   │   ├── main.py

│   │   └── query\_service.py

│   │

│   └── requirements.txt

│

├── frontend/

│   ├── src/

│   │   ├── assets/

│   │   ├── App.jsx

│   │   ├── App.css

│   │   ├── index.css

│   │   └── main.jsx

│   │

│   ├── package.json

│   └── vite.config.js

│

├── .gitignore

└── README.md

How It Works

1\. Natural Language Question



The user enters a question such as:



What is the total revenue from all orders?

2\. SQL Generation



The backend sends the question and database schema to the local LLM.



Example generated query:



SELECT SUM(orders.total\_amount) AS total\_revenue

FROM orders;

3\. SQL Validation



The generated query is checked to ensure that only read-only SQL statements are executed.



The application rejects operations such as:



INSERT

UPDATE

DELETE

DROP

ALTER

CREATE

TRUNCATE

GRANT

REVOKE

4\. PostgreSQL Execution



The validated query is executed against the PostgreSQL database.



5\. Results



The backend converts database rows into JSON-compatible results.



6\. Business Insight



The returned data is passed to the AI layer to generate a concise business explanation based only on the query results.



Database Schema



The current application uses the following tables:



Customers

customer\_id

name

email

city

signup\_date

Products

product\_id

product\_name

category

price

Orders

order\_id

customer\_id

product\_id

quantity

order\_date

total\_amount

Relationships

orders.customer\_id -> customers.customer\_id





orders.product\_id -> products.product\_id

Running Locally

Prerequisites



Make sure the following are installed:



Python 3.10+

Node.js

PostgreSQL

Ollama

Git

Clone the Repository

git clone https://github.com/shrijashetty1/ai-data-intelligence-platform.git





cd ai-data-intelligence-platform

Backend Setup



Navigate to the backend:



cd backend



Create a virtual environment:



python -m venv venv



Activate it on Windows:



venv\\Scripts\\activate



Install dependencies:



pip install -r requirements.txt



Start the FastAPI server:



uvicorn app.main:app --reload



The API will run at:



http://127.0.0.1:8000



FastAPI documentation:



http://127.0.0.1:8000/docs

Ollama Setup



Install Ollama and pull the model:



ollama pull qwen3:1.7b



Verify the model:



ollama list



Start Ollama if required:



ollama serve

Frontend Setup



Open another terminal and navigate to:



cd frontend



Install dependencies:



npm install



Start the development server:



npm run dev



The frontend will normally be available at:



http://localhost:5173

