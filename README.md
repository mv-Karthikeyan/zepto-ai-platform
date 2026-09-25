\# Zepto Data \& AI Platform



\## Project Overview



This capstone project implements an end-to-end Data and AI platform using Python.



The project contains three major modules:



1\. \*\*Data Pipeline\*\* – Web scraping, data cleaning, SQLite and SQL analysis

2\. \*\*Analytics \& Machine Learning\*\* – Titanic EDA, classification and regression

3\. \*\*Support Assistant\*\* – RAG-based Zepto policy assistant using embeddings, ChromaDB, LangGraph, FastAPI and Docker



\---



\## Repository Structure



```text

zepto-ai-platform/

│

├── data\_pipeline/

│   ├── scraper.py

│   ├── cleaner.py

│   ├── database.py

│   ├── queries.py

│   ├── pandas\_sql.py

│   ├── sql\_queries.txt

│   ├── query\_results/

│   └── README.md

│

├── analytics/

│   ├── 01\_eda.ipynb

│   ├── 02\_modeling.ipynb

│   ├── titanic.csv

│   ├── charts/

│   ├── models/

│   │   └── best\_pipeline.joblib

│   └── README.md

│

├── support\_assistant/

│   ├── docs/

│   │   ├── doc\_01.txt

│   │   ├── doc\_02.txt

│   │   ├── doc\_03.txt

│   │   ├── doc\_04.txt

│   │   ├── doc\_05.txt

│   │   ├── doc\_06.txt

│   │   ├── doc\_07.txt

│   │   └── doc\_08.txt

│   ├── ingest.py

│   ├── retrieval.py

│   ├── graph.py

│   ├── prompts.py

│   ├── models.py

│   ├── llm.py

│   ├── main.py

│   ├── requirements.txt

│   ├── Dockerfile

│   └── README.md

│

├── requirements.txt

├── .gitignore

└── README.md

```



\---



\# Module 1 – Data Pipeline



The Data Pipeline collects book information from \*\*Books to Scrape\*\* using `requests` and `BeautifulSoup`.



The pipeline collects at least 60 books across multiple categories and extracts:



\- Title

\- Price in GBP

\- Star rating

\- Availability

\- Category



\## Data Cleaning



The scraped data is converted into analysis-ready fields.



The following transformations are performed:



\- GBP price is converted to numeric format.

\- Star ratings are converted from text values such as `One`, `Two`, and `Five` to integers from 1–5.

\- Availability is converted into a Boolean `in\_stock` field.

\- Numeric parsing failures are handled using median imputation where applicable.

\- GBP prices are converted to INR using the required fixed conversion:



```text

1 GBP = 105.50 INR

```



Therefore:



```text

price\_inr = price\_gbp × 105.50

```



\## SQLite Database



The cleaned data is stored in a normalized SQLite database.



The main tables are:



```text

categories

\----------

category\_id (Primary Key)

category\_name



books

\-----

book\_id (Primary Key)

title

price\_gbp

price\_inr

rating

in\_stock

category\_id (Foreign Key)

```



This creates a one-to-many relationship between categories and books.



\## SQL Analysis



The SQL section demonstrates:



\- SELECT

\- WHERE

\- ORDER BY

\- LIMIT

\- DISTINCT

\- BETWEEN

\- IN

\- INNER JOIN



The SQL statements are saved in:



```text

data\_pipeline/sql\_queries.txt

```



Query outputs are stored under:



```text

data\_pipeline/query\_results/

```



Pandas `read\_sql` is also used to read SQL results, while `pd.merge` reproduces the SQL JOIN operation for comparison.



\## Run Module 1



From the repository root:



```powershell

python data\_pipeline\\scraper.py

python data\_pipeline\\cleaner.py

python data\_pipeline\\database.py

python data\_pipeline\\queries.py

python data\_pipeline\\pandas\_sql.py

```



Detailed documentation is available in:



```text

data\_pipeline/README.md

```



\---



\# Module 2 – Analytics \& Machine Learning



The Analytics module performs exploratory data analysis and machine learning using the Titanic dataset.



The dataset is loaded once using:



```python

sns.load\_dataset("titanic")

```



and immediately saved to:



```text

analytics/titanic.csv

```



The saved dataset is then used for subsequent analysis.



\## Exploratory Data Analysis



The EDA includes:



\- Dataset shape and structure

\- Descriptive statistics

\- Missing-value percentages

\- Missing-data treatment

\- Age distribution

\- Fare distribution

\- Boxplots

\- IQR-based outlier detection

\- Mean, median and mode analysis

\- Survival analysis by sex and passenger class

\- Boolean masking using `\&` and `|`

\- Correlation analysis

\- Multivariate visualizations

\- Standardization of age and fare



The correlation analysis uses exactly these six columns:



```text

survived

pclass

age

sibsp

parch

fare

```



\## Classification



The classification target is:



```text

survived

```



The dataset is split into training and testing sets using stratification.



Preprocessing is fitted only on training data to prevent data leakage.



The classification models are:



\- Logistic Regression

\- Decision Tree

\- Random Forest



The models are evaluated using:



\- Confusion Matrix

\- Accuracy

\- Precision

\- Recall

\- F1-score

\- ROC curve

\- ROC-AUC



Class imbalance experiments compare:



\- Baseline model

\- `class\_weight="balanced"`

\- SMOTE applied only to training data



Random Forest tuning is performed using `GridSearchCV`.



The tuning process evaluates:



```text

n\_estimators

max\_depth

max\_features

```



and uses out-of-bag evaluation through:



```text

oob\_score=True

```



\## Regression



A multivariate Linear Regression model predicts:



```text

fare

```



Regression performance is evaluated using:



\- MAE

\- RMSE

\- R²

\- Adjusted R²

\- Residual analysis



\## Model Persistence



The selected fitted preprocessing and classifier pipeline is saved using Joblib:



```text

analytics/models/best\_pipeline.joblib

```



The saved pipeline is reloaded and used to make a prediction from raw passenger input.



Detailed documentation is available in:



```text

analytics/README.md

```



\---



\# Module 3 – Zepto Support Assistant



The Support Assistant implements a Retrieval-Augmented Generation workflow using eight local Zepto policy documents.



\## Architecture



```text

Zepto Policy Documents

&#x20;       |

&#x20;       v

Sentence Transformers

all-MiniLM-L6-v2

&#x20;       |

&#x20;       v

Vector Embeddings

&#x20;       |

&#x20;       v

ChromaDB

&#x20;       |

&#x20;       v

User Question

&#x20;       |

&#x20;       v

LangGraph

&#x20;       |

&#x20;       v

classify\_intent

&#x20;      / \\

&#x20;     /   \\

policy     general

&#x20;  |          |

&#x20;  v          v

retrieve\_   direct\_

and\_answer  answer

&#x20;  |

&#x20;  v

Top-3 ChromaDB Retrieval

&#x20;  |

&#x20;  v

Mock / Optional Real LLM

&#x20;  |

&#x20;  v

Pydantic Validation

&#x20;  |

&#x20;  v

FastAPI /ask

```



\## Policy Corpus



Eight policy documents are stored under:



```text

support\_assistant/docs/

```



They cover areas including:



\- Delivery

\- Returns and refunds

\- Membership

\- Order tracking

\- Cancellation

\- Damaged or missing items

\- Gift cards

\- Support hours



\## Embeddings and Retrieval



The embedding model is:



```text

sentence-transformers/all-MiniLM-L6-v2

```



The embeddings are stored locally using ChromaDB.



For policy questions, the system performs real vector similarity retrieval and returns the top three matching policy documents.



\## LangGraph



The workflow contains three named nodes:



```text

classify\_intent

retrieve\_and\_answer

direct\_answer

```



`classify\_intent` determines whether the question is a policy question or a general question.



Policy questions are routed to `retrieve\_and\_answer`.



General questions are routed to `direct\_answer`.



\## Mock LLM Mode



The default graded mode is:



```text

MOCK\_LLM=1

```



Mock mode does not make external LLM API calls.



Policy questions use real ChromaDB retrieval and produce a deterministic answer based on the most relevant retrieved document.



General questions return:



```text

I can only answer questions about Zepto policies right now.

```



\## Optional Real LLM



The optional real LLM mode can be enabled with:



```text

MOCK\_LLM=0

```



Groq is used for the optional LLM integration.



Structured responses are validated using Pydantic. The real LLM path supports an initial validation attempt plus up to two retries if validation fails.



\## Response Schema



The API response follows:



```json

{

&#x20; "answer": "string",

&#x20; "sources": \["doc\_01"],

&#x20; "confidence": 0.95

}

```



`confidence` is constrained to the range `0.0` to `1.0`.



\## Run Module 3



Install Module 3 dependencies:



```powershell

pip install -r support\_assistant\\requirements.txt

```



Create embeddings and populate ChromaDB:



```powershell

python -m support\_assistant.ingest

```



Run in mock mode:



```powershell

$env:MOCK\_LLM="1"

```



Start FastAPI:



```powershell

uvicorn support\_assistant.main:app --host 0.0.0.0 --port 8000

```



Example request:



```json

{

&#x20; "query": "What is the delivery fee?"

}

```



A general-question example:



```json

{

&#x20; "query": "Who won the cricket match yesterday?"

}

```



Detailed documentation is available in:



```text

support\_assistant/README.md

```



\---



\# Docker



The Support Assistant can also run inside Docker.



Build the image from the repository root:



```powershell

docker build -f support\_assistant/Dockerfile -t zepto-support .

```



Run the container:



```powershell

docker run --rm -p 8000:8000 -e MOCK\_LLM=1 zepto-support

```



If port 8000 is already occupied:



```powershell

docker run --rm -p 8001:8000 -e MOCK\_LLM=1 zepto-support

```



The `/ask` endpoint is then available through the mapped local port.



\---



\# Installation



Create a virtual environment:



```powershell

python -m venv venv

```



Activate it in PowerShell:



```powershell

Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process

.\\venv\\Scripts\\Activate.ps1

```



Install project dependencies:



```powershell

pip install -r requirements.txt

```



\---



\# Technologies Used



\- Python

\- Pandas

\- NumPy

\- Requests

\- BeautifulSoup

\- SQLite

\- Matplotlib

\- Seaborn

\- Scikit-learn

\- Imbalanced-learn

\- Joblib

\- Sentence Transformers

\- ChromaDB

\- LangGraph

\- Pydantic

\- FastAPI

\- Groq

\- Docker

\- Git

\- GitHub



\---



\# Git Workflow



Development was performed using feature branches.



The repository includes:



```text

feature/data-pipeline

feature/analytics

feature/support-assistant

```



Each major module was developed through feature commits and merged into the `main` branch.



This provides a clear Git history demonstrating feature-branch development and integration.



\---



\# Project Summary



This project demonstrates an end-to-end Data and AI workflow.



The Data Pipeline transforms web data into structured relational data. The Analytics module performs EDA, classification, imbalance handling, hyperparameter tuning, regression and model persistence. The Support Assistant demonstrates local embeddings, vector retrieval, graph-based routing, structured AI responses, FastAPI deployment and Docker containerization.

