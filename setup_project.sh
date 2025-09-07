#!/bin/bash

# Root folder
PROJECT_ROOT="contra-costa-knowledge-bot"
mkdir -p $PROJECT_ROOT
cd $PROJECT_ROOT

# -----------------------
# Backend structure
# -----------------------
mkdir -p backend/app/{models,routes,services,utils,data}
mkdir -p backend/tests
touch backend/app/{__init__.py,main.py,config.py}
touch backend/app/models/query.py
touch backend/app/routes/ask.py
touch backend/app/services/{embedding.py,retrieval.py,generation.py}
touch backend/app/utils/{chunking.py,logger.py}
touch backend/app/data/{documents.json,contracosta.index}
touch backend/tests/test_retrieval.py
touch backend/{requirements.txt,README.md}

# -----------------------
# Frontend structure
# -----------------------
mkdir -p frontend/{public,src/{components,pages,services}}
touch frontend/public/index.html
touch frontend/src/components/{QuestionInput.jsx,AnswerCard.jsx}
touch frontend/src/pages/Home.jsx
touch frontend/src/services/api.js
touch frontend/src/{App.jsx,index.js}
touch frontend/{package.json,README.md}

# -----------------------
# Docs
# -----------------------
mkdir -p docs
touch docs/{architecture-diagram.png,data-plan.md,project-plan.md}

# -----------------------
# Root files
# -----------------------
touch .env.example .gitignore README.md

echo "✅ Project folder structure created successfully!"
