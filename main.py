from enum import Enum
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from bson.objectid import ObjectId
from fastapi.middleware.cors import CORSMiddleware

class ModelName(str, Enum):
    alex = "alex"
    bob = "bob"
    lenny = "lenny"

app = FastAPI()
# Allow all origins for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = MongoClient("mongodb://localhost:27017")

db = client["votes"]
collection = db["votes"]

user = client["users"]
usr_coll = user["users"]

class Vote(BaseModel):
    name: str
    count: int

class User(BaseModel):
    username: str
    email: str
    passwd: str
    #motor_owned: [motor_1, motor_2]


class Motor(BaseModel):
    name: str
    series: str
    location: str

@app.get("/")
async def root():
    return {"message": "Hello API"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}

@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alex:
        return {"model_name" : model_name, "message": "Hello alex."}
    
    if model_name.value == "lenny":
        return {"Hello": "lenny"}
    
    return {"None"}

#Create
@app.post("/votes/")
async def create_vote(vote: Vote):
    result = collection.insert_one(vote.dict())
    return {
        "id": str(result.inserted_id),
        "name": vote.name,
        "count": vote.count,
    }

#Read
@app.get("/votes/{vote_id}")
async def read_vote(vote_id: str):
    vote = collection.find_one({"_id": ObjectId(vote_id)})
    if vote:
        return {"id": str(vote["_id"]), "name": vote["name"], "count": vote["count"]}
    else:
        raise HTTPException(status_code=404, detail="Vote not found")
    
#Update
@app.put("/votes/{vote_id}")
async def update_vote(vote_id: str, vote: Vote):
    result = collection.update_one(
        {"_id": ObjectId(vote_id)}, {"$set": vote.dict(exclude_unset=True)}
    )
    if result.modified_count == 1:
        return {"id": vote_id, "name": vote.name, "count": vote.count}
    else:
        raise HTTPException(status_code=404, detail="Vote not found")
    
#Delete
@app.delete("/votes/{vote_id}")
async def delete_vote(vote_id: str):
    result = collection.delete_one({"_id": ObjectId(vote_id)})
    if result.deleted_count == 1:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=404, detail="Vote not found")

#Create user //Register
@app.post("/user/")
async def create_user(user: User):
    result = usr_coll.insert_one(user.dict())
    return {
        "id": str(result.inserted_id),
        "username": user.username,
        "email": user.email,
        "passwd": user.passwd,
    }

#Login verify user data from db
@app.get("/login/{email}")
async def login_with_id(email: str):
    user = usr_coll.find_one({"email": email})
    if user:
        return {"id": str(user["_id"]), "username": user["username"], "passwd": user["passwd"]}
    else:
        raise HTTPException(status_code=404, detail="Please check your email or password.")
