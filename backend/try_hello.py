from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="FastAPI hello")


class OrderRequest(BaseModel):
    """The shape of the data we expect. FastAPI checks every request against it."""

    item: str
    quantity: int = Field(gt=0, description="Must be greater than zero")


class OrderResponse(BaseModel):
    message: str
    total_items: int


@app.get("/hello")
def hello():
    return {"message": "hello"}


@app.get("/hello/{name}")
def hello_name(name: str, shout: bool = False):
    # {name} comes from the URL path; shout comes from ?shout=true in the query string
    text = f"hello {name}"
    return {"message": text.upper() if shout else text}


@app.post("/orders", response_model=OrderResponse)
def create_order(order: OrderRequest):
    if order.item.strip().lower() == "forbidden":
        # HTTPException turns into a proper HTTP error response
        raise HTTPException(status_code=400, detail="That item cannot be ordered")
    return OrderResponse(
        message=f"Ordered {order.quantity} x {order.item}",
        total_items=order.quantity,
    )