from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis_om import get_redis_connection, HashModel


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

class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def get_products():
    return [get_individual_product(pk) for pk in Product.all_pks()]


def get_individual_product(product_id: str):
    product = Product.get(product_id)
    return {
        'id': product.pk,
        'name': product.name,
        'price': product.price,
        'quantity': product.quantity
    }


@app.post("/products")
def create_product(product: Product):
    return product.save()


@app.get("/products/{product_id}")
def get_product(product_id: str, q: Optional[str] = None):
    return get_individual_product(product_id)

@app.delete("/products/{product_id}")
def get_product(product_id: str):
    return Product.delete(product_id)