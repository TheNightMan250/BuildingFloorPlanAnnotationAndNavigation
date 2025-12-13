from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Literal, Optional
from model.network import Predictor
from model.dataset import ActionStore
from model.trainer import OnlineTrainer
from model.reinforce import Reinforce
from fastapi.middleware.cors import CORSMiddleware


class Event(BaseModel):
    action: Literal["place_room", "pathway_segment"]
    coords: List[List[float]]
    timestamp: float


class Feedback(BaseModel):
    prediction_id: str
    reward: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = ActionStore(max_len=5000)
model = Predictor()
trainer = OnlineTrainer(model, store)
reinforce = Reinforce(model)


@app.post("/api/event")
async def receive_event(evt: Event):
    store.add(evt.dict())
    trainer.train_step()
    return {"ok": True, "count": len(store)}


@app.get("/api/predict")
async def predict():
    actions = store.get_last(20)
    pred = model.predict(actions)
    return pred


@app.post("/api/feedback")
async def feedback(body: Feedback):
    actions = store.get_last(20)
    reinforce.apply(body.reward, actions, body.prediction_id)
    return {"ok": True}


@app.get("/api/health")
async def health():
    return {"status": "ok"}

