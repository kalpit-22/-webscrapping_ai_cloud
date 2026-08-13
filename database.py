import os
import datetime
import certifi
from motor.motor_asyncio import AsyncIOMotorClient

# Fallback to local MongoDB if not provided (useful for local dev)
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI, tlsCAFile=certifi.where())

# Database and Collection
db = client.research_agent
logs_collection = db.research_logs

async def save_research_log(question: str, report: str, sources_used: int, total_tokens: int):
    """Save the full research input, output, and metrics to the database."""
    log_entry = {
        "timestamp": datetime.datetime.utcnow(),
        "question": question,
        "report": report,
        "sources_used": sources_used,
        "total_tokens_used": total_tokens,
    }
    
    try:
        await logs_collection.insert_one(log_entry)
        print(f"💾 Saved log to database for question: {question}")
    except Exception as e:
        print(f"⚠ Failed to save log to database: {e}")

async def get_research_logs(limit: int = 50):
    """Fetch the most recent research logs from the database."""
    cursor = logs_collection.find().sort("timestamp", -1).limit(limit)
    logs = await cursor.to_list(length=limit)
    
    # Convert ObjectId and datetime to JSON serializable strings
    for log in logs:
        log["_id"] = str(log["_id"])
        log["timestamp"] = log["timestamp"].isoformat()
        
    return logs
