import logging
from typing import List

from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from model_hub.db.database_manager import DatabaseManager
from model_hub.db.models import Model


class MongoManager(DatabaseManager):
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

    async def connect_to_database(self, path: str):
        logging.info("Connecting to MongoDB.")
        self.client = AsyncIOMotorClient(
            path,
            maxPoolSize=10,
            minPoolSize=10)
        self.db = self.client.main_db
        logging.info("Connected to MongoDB.")

    async def close_database_connection(self):
        logging.info("Closing connection with MongoDB.")
        self.client.close()
        logging.info("Closed connection with MongoDB.")

    async def get_models(self) -> List[Model]:
        models_list = []
        models_q = self.db.models.find()
        async for post in models_q:
            models_list.append(Model(**post, id=post['_id']))
        return models_list

    async def get_model(self, model_url: str) -> Model:
        model_q = await self.db.models.find_one({'_id': ObjectId(model_url)})
        if model_q:
            return Model(**model_q, id=model_q['_id'])

    async def delete_model(self, model_url: str):
        await self.db.models.delete_one({'_id': ObjectId(model_url)})

    async def update_model(self, model_url: str, post: Model):
        await self.db.models.update_one({'_id': ObjectId(model_url)},
                                       {'$set': post.dict(exclude={'id'})})

    async def add_model(self, model: Model):
        await self.db.models.insert_one(model.dict(exclude={'id'}))