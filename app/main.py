from fastapi import FastAPI
from redis import Redis

app = FastAPI()

# Direct connection configuration for Redis
redis_client = Redis(host="redis", port=6379, db=0)

@app.get("/user/{user_id}/stats")
def get_user_stats(user_id: str):
    total_orders = redis_client.get(f"user:{user_id}:total_orders") or 0
    cumulative_spend = redis_client.get(f"user:{user_id}:cumulative_spend") or 0
    return {
        "user_id": str(user_id),
        "order_count": int(total_orders),
        "total_spend": float(cumulative_spend)
    }
#http://localhost:8000/user/U11/stats



@app.get("/global/stats")
def get_global_stats():
    total_orders = redis_client.get("global:total_orders") or 0
    cumulative_spend = redis_client.get("global:cumulative_spend") or 0
    return {
        "total_orders": int(total_orders),
        "total_revenue": float(cumulative_spend)
    }
#http://localhost:8000/global/stats