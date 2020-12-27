from pymongo import MongoClient
import asyncio
import mysql.connector as connector
import queue
import json


class DB:
    def __init__(self, queue):
        f = open('config.json', 'r')
        self.config = json.load(f)
        self.queue = queue
        self.loop = asyncio.new_event_loop()
        self.databaseName = self.config.get("DB_NAME")
        self.tableName = self.config.get("DB_TABLE_NAME")

    def start(self):
        def connection():
            config = {
                "user": self.config.get("DB_USERNAME"),
                "password": self.config.get("DB_PASSWORD"),
                "host": self.config.get("MYSQL_SERVER_ADDRESS"),
                "port": 3306,
                'database': self.databaseName
            }
            try:
                c = connector.connect(**config)
                return c
            except:
                print("connection error")
                exit(1)

        cn = connection()
        cur = cn.cursor()
        cur.execute("select version();")
        print(f'Using database version : {cur.fetchone()}')
        self.loop.run_until_complete(self.main(cur))

    async def createTableIfNotExists(self, cur):
        cur.execute(
            f"CREATE TABLE IF NOT EXISTS {self.tableName} (server VARCHAR(255), channel VARCHAR(255), user VARCHAR(255), message VARCHAR(2000))")

    async def createDatabaseIfNotExists(self, cur):
        cur.execute(f"CREATE DATABASE IF NOT EXISTS {self.databaseName};")

    async def main(self, cur):
        await self.createDatabaseIfNotExists(cur)
        await self.createTableIfNotExists(cur)
        while True:
            message = self.queue.get()
            server = message.guild.name
            channel = message.channel.name
            user = message.author.name
            content = message.content
            statement = f'INSERT INTO {self.tableName}(server, channel, user, message) VALUES (%s, %s, %s, %s)'
            cur.execute(statement, (server, channel, user, content))
            self.queue.task_done()
