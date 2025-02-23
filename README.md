# 🚀 CRAVE Trinity Backend (FastAPI + Clean Architecture)  

## 🌟 Overview  

CRAVE Trinity Backend is a **modular, Dockerized FastAPI application** built with **clean architecture** principles. It is designed to **track and analyze user cravings** and integrates multiple external services, including:  

- 🛢 **PostgreSQL** for structured data storage  
- 🧠 **Pinecone** for vector-based retrieval (Batch 3)  
- 🤖 **Llama 2 with LoRA integration** for AI-powered insights (Batch 4)  

This repository demonstrates an **end-to-end system**—from **initial setup** and **database migrations** to **AI model inference with LoRA adapters**.  

---

## 🏗 Architecture & Batches  

The project is organized into **batches**, breaking the development process into structured steps:  

### 🔹 Batch 1 – Initial Setup  
📌 Clone the repository, install dependencies, and configure the environment.  
🔧 Initialize **PostgreSQL** and apply **Alembic** database migrations.  
📂 **Key files:** `.env`, `requirements.txt`, `alembic.ini`  

### 🔹 Batch 2 – Backend & Database Integration  
🛠 Develop **FastAPI** REST endpoints following **clean architecture**.  
📊 Implement **database models, repositories, and use-case layers** for craving tracking.  
📂 **Key files:** `app/api/`, `app/core/`, `app/infrastructure/database/`  

### 🔹 Batch 3 – External Services Integration  
📡 Connect to **Pinecone** for **vector storage & retrieval**.  
🤖 Integrate **OpenAI embeddings** for craving analysis.  
📂 **Key files:** `app/infrastructure/vector_db/`, `app/infrastructure/external/openai_embedding.py`  

### 🔹 Batch 4 – Llama 2 with LoRA Integration  
🦙 Load and fine-tune **Llama 2** using **LoRA adapters**.  
🔍 Deploy AI inference endpoints for **craving insights**.  
📂 **Key files:** `app/models/llama2_model.py`, `app/infrastructure/llm/llama2_adapter.py`  

---

## ⚡ Quick Start  

### ✅ Prerequisites  

Before you begin, ensure you have the following installed:  

- 🐳 **Docker & Docker Compose** for containerized setup  
- 🐍 **Python 3.11** (if running locally)  
- 🤗 **Hugging Face CLI** (if using private models, run `huggingface-cli login`)  

### 📥 Clone the Repository  

```bash
git clone git@github.com:The-Obstacle-Is-The-Way/crave-trinity-backend.git
cd crave-trinity-backend
```

### 🔧 Configure Environment Variables  

Create a `.env` file in the project root with the necessary credentials:  

```env
SQLALCHEMY_DATABASE_URI=postgresql://postgres:password@db:5432/crave_db
PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENV=us-east-1-aws
PINECONE_INDEX_NAME=crave-embeddings
OPENAI_API_KEY=your_openai_api_key_here
```

### 🏗 Build & Run with Docker Compose  

```bash
docker-compose up --build
```

This will:  
✅ Build the **FastAPI** backend container  
✅ Start the **PostgreSQL** database  
✅ Expose ports **8000** (API) & **5432** (Database)  

### 🔄 Run Database Migrations  

Inside the container (or locally, if configured):  

```bash
alembic upgrade head
```

This ensures the **database schema** is up to date.  

---

## 🧪 Testing the Application  

### 🔬 API Endpoints  

Once running, test the **craving logging API** with:  

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{"user_id":1, "description":"Chocolate craving", "intensity":8}' \
http://localhost:8000/cravings
```

### 📡 Pinecone Integration  

Inside the **FastAPI** container, verify the Pinecone index:  

```bash
docker exec -it crave_trinity_backend-fast-api-1 python -c \
"from app.infrastructure.vector_db.pinecone_client import init_pinecone; \
init_pinecone(); import pinecone; print('List of indexes:', pinecone.list_indexes())"
```

Ensure `crave-embeddings` exists and is ready for use.  

### 🤖 Run Llama 2 with LoRA Inference (Batch 4)  

```bash
docker exec -it crave_trinity_backend-fast-api-1 python app/models/llama2_model.py
```

This loads **Llama 2 + LoRA adapters** and runs a **test inference prompt**.  

---

## 🛠 Technical Details  

- 🐳 **Dockerized Setup**  
  - The backend is containerized with **Python 3.11-slim** for efficiency.  

- 🛢 **Database**  
  - Uses **PostgreSQL**, managed via **Alembic** migrations.  

- 📡 **External Services**  
  - **Pinecone** for **vector storage & retrieval**.  
  - **OpenAI** for **text embeddings** and craving analysis.  

- 🤖 **AI Model (Batch 4)**  
  - **Llama 2** runs via **Hugging Face Transformers**.  
  - **LoRA adapters** fine-tune AI insights with **PEFT**.  

---

## 🛣 Roadmap & Future Enhancements  

🔜 **Batch 5** – Analytics dashboard & craving trend visualization  
📊 **Batch 6** – Performance optimizations (GPU inference, rate limiting)  
🔒 **Security Enhancements** – OAuth, data anonymization, and logging improvements  
🚀 **Scaling** – Kubernetes deployment (`infra/k8s`)  

---

## 📂 File Structure  

```plaintext
.
├── Dockerfile
├── docker-compose.yml
├── README.md
├── alembic.ini
├── app/
│   ├── api/           # API endpoints
│   ├── config/        # Settings & logging
│   ├── core/          # Business logic (use cases)
│   ├── infrastructure/# Database, external APIs, vector DBs
│   ├── models/        # AI model handling (Llama2 + LoRA)
├── infra/             # Deployment configs (AWS, K8s, Docker)
├── main.py            # Application entry point
├── requirements.txt   # Dependencies
└── tests/             # Unit & integration tests
```

---

## 🤝 Contributing  

1️⃣ **Fork** the repository  
2️⃣ **Create** a feature branch (`git checkout -b feature/your-feature`)  
3️⃣ **Commit** your changes (`git commit -m "Added feature X"`)  
4️⃣ **Push** & open a pull request  

---

## 📜 License  

This project is licensed under the **MIT License**.  
