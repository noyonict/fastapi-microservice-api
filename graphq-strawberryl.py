import strawberry


from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter




async def get_root_value():
    return Query(name="Patrick")




@strawberry.type
class Query:
    name: str




schema = strawberry.Schema(Query)


graphql_app = GraphQLRouter(
    schema,
    root_value_getter=get_root_value,
)


app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")

