from typing import Optional, Any

import uvicorn
from fastapi import FastAPI, Path, Query, Body
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

app = FastAPI()


class Response(BaseModel):
    code: int
    msg: str
    data: Any


class Item(BaseModel):
    name: str
    price: float


inventory = {
    1: Item(name="milk", price=3.99)
}

# serve static
app.mount(path="/static", app=StaticFiles(directory="./static"), name="static")


@app.get("/")
def items():
    return Response(
        code=200,
        msg="",
        data=inventory,
    )


# path param "/item/1", "item/2"
@app.get("/item/{id}")
def item_by_id(id: Optional[int] = Path(default=None, description="id of item")):
    if id not in inventory:
        return Response(
            code=404,
            msg="item id not found",
            data=None,
        )
    return Response(
        code=200,
        msg="",
        data=inventory[id]
    )


# query param "/item?name=milk", "item?name=egg"
@app.get("/item")
def item_by_name(name: str = Query(default=None, description="name of item")):
    for item in inventory.values():
        if item.name == name:
            return Response(
                code=200,
                msg="",
                data=item
            )
    return Response(
        code=404,
        msg="item name not found",
        data=None,
    )


# query param and request body "/create?id=3", body Item
@app.post("/create")
def create_item(
        id: int = Query(default=None, description="id of item"),
        item: Item = Body(default=None, description="item"),
):
    if id in inventory:
        return Response(
            code=403,
            msg="item id exists",
            data=None,
        )
    inventory[id] = item
    return Response(
        code=200,
        msg="",
        data=item,
    )


if __name__ == "__main__":
    uvicorn.run(app, port=3000)
