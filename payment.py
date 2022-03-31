from typing import Optional
from urllib.request import Request

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.background import BackgroundTasks
from redis_om import get_redis_connection, HashModel
import requests, time


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_methods=['*'],
    allow_headers=['*']
)

redis = get_redis_connection(
    host="redis-14488.c292.ap-southeast-1-1.ec2.cloud.redislabs.com",
    port=14488,
    password="gkyCGQcxp7aAlW3DlClBujdjT0UebhAK",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str  # pending, completed, refunded

    class Meta:
        database = redis


@app.post('/orders')
async def create(request: dict, background_task: BackgroundTasks):  # id, quantity
    # body = await request.json()
    product = requests.get('http://localhost:8000/products/%s' % request['id']).json()
    order = Order(
        product_id=product['id'],
        price=product['price'],
        fee=product['price'] * 0.2,
        total=product['price'] * 1.2 * request['quantity'],
        quantity=request['quantity'],
        status='pending',
    )
    order.save()
    background_task.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = 'completed'
    redis.xadd('order_completed', order.dict(), '*')
    order.save()


def get_individual_order(order_id: str):
    order = Order.get(order_id)
    return order


@app.get('/orders')
def get_orders():
    return [get_individual_order(order_id) for order_id in Order.all_pks()]


@app.get('/orders/{pk}')
def get_orders(pk: str):
    return Order.get(pk)


@app.delete('/orders/{pk}')
def get_orders(pk: str):
    return Order.delete(pk)

