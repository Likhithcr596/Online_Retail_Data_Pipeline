# Online Retail Data Pipeline

## Overview
This project implements a data pipeline for an online retail platform. It processes customer order events, updates aggregated statistics, and exposes a REST API for retrieving user-specific and global statistics. The pipeline uses AWS SQS for event ingestion, a Python-based worker for data processing, Redis for caching, and FastAPI for the REST API.

---

## Pipeline Steps

### 1. **Ingest Order Events (from SQS)**
- Events are ingested from an SQS queue using a Python-based worker script (`worker.py`).
- SQS serves as a decoupling layer, allowing the system to handle bursts of traffic without overwhelming downstream services.

---

### 2. **Process Events**
- **Validation:** The worker validates events to ensure required fields like `user_id` and `amount` are present.
- **Aggregation:**
  - Updates fields such as total orders and cumulative spend per user and globally.
- **Cleaning:**
  - Handles missing or malformed fields.
  - Normalizes data as needed or drops invalid records.

---

### 3. **Store Aggregated Statistics (into Redis)**
- Redis is used as the cache layer for maintaining statistics:
  - **User-level statistics:** Cumulative spend and total orders for each user.
  - **Global statistics:** Aggregated metrics like total cumulative spend and order count.
- **Key Design:**
  - Keys are structured hierarchically for efficient retrieval and management:
    - `user:<user_id>:<stat>`
    - `global:<stat>`

---

### 4. **Expose REST API (via FastAPI)**

The REST API provides endpoints to retrieve user-specific and global statistics.

#### **Endpoints**

1. **User-Specific Stats**  
   - **Endpoint:** `/user/{user_id}/stats`  
   - **Description:** Returns statistics for a specific user.  
   - **Example Request:**  
     ```
     GET http://localhost:8000/user/U18/stats
     ```  

    ![image](https://github.com/user-attachments/assets/cdfd3603-85ce-4e41-a358-971bbd0b9fe2)


   - **Example Response:**  
     ```json
     {
       "user_id": "U18",
       "order_count": 3,
       "total_spend": 969.69
     }
     ```

2. **Global Stats**  
   - **Endpoint:** `/stats/global`  
   - **Description:** Returns overall platform statistics.  
   - **Example Request:**  
     ```
     GET http://localhost:8000/global/stats
     ```  
   - **Example Response:**  
     ```json
     {
       "total_orders": 10,
       "total_revenue": 788.87
     }
     ```
      ![image](https://github.com/user-attachments/assets/d85c767e-f9ef-46fa-9956-29d8f474e4b9)


---

## Design Diagram
```
+-----------------------------------+
|          REST API (FastAPI)       |
|      (Retrieve statistics)        |
+-----------------------------------+
                ^
                |
                v
       +-------------------+
       |     Redis Cache    |
       | (Aggregated stats) |
       +-------------------+
                ^
                |
                v
       +-------------------+
       |   Worker(s)       |
       |  (Processes SQS   |
       |  messages and     |
       |  updates Redis)   |
       +-------------------+
                ^
                |
                v
       +-------------------+
       |     SQS Queue     |
       | (Decouples API    |
       |  from workers)    |
       +-------------------+
                ^
                |
                v
+-----------------------------------+
|        Order Events Source        |
|  (Events published to SQS Queue)  |
+-----------------------------------+
```


---

## System Behavior Example

1. **User places an order:**
   - An event (e.g., `{"user_id": "123", "amount": 100}`) is published to the SQS queue.

2. **Worker processes the event:**
   - Updates Redis:
     - `user:U11:cumulative_spend = 100`
     - `user:U11:total_orders = 1`
     - `global:cumulative_spend = 100`
     - `global:total_orders = 1`

3. **User retrieves stats via API:**
   - API fetches data from Redis:
     - For `user:U11` → `{
  "user_id": "U11",
  "order_count": 1,
  "total_spend": 100.0
}`
     - For global stats → `{ "total_revenue": 100, "total_orders": 1 }`

---

## Key Benefits
- **Modular Design:** Each component (SQS, worker, Redis, API) is independent, enabling easy updates or scaling.
- **Resilient Architecture:** Decoupling via SQS ensures robustness under high traffic.
- **Efficient Retrieval:** Redis caching ensures low-latency data access for API requests.

---

## Getting Started
1. Clone the repository.
   ```bash
   git clone https://github.com/Likhithcr596/Online_Retail_Data_Pipeline.git
   cd Online_Retail_Data_Pipeline
3. Build and run the Docker containers:
   ```bash
   docker-compose up --build
   ```
4. Populate the SQS queue with sample data
Use the provided Python script in the scripts folder to send messages to the
   ```bash
   python init/populate_sqs.py
   ```
5. Access the FastAPI API at.
   ```bash
   http://localhost:8000
   ```
![image](https://github.com/user-attachments/assets/250d0d47-f10f-4993-8325-c27595b3301e)


![image](https://github.com/user-attachments/assets/ef6739e3-a6f2-4c7b-b83f-f5e95f36cdfd)

---

