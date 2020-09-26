import pandas
from pymongo import MongoClient
import json
import datetime
import pandas as pd
import pymongo


def mongocol_to_dataframe(mongocol):

    output_df = pandas.DataFrame()
    for dic in mongocol:
        if len(dic.keys()):
            temp_df = pandas.DataFrame(dic, index=[0])
            output_df = pandas.concat([output_df, temp_df])
    return output_df


class MongoBase:

    def __init__(self, db_owner, database, collection):
        self.db_owner = db_owner
        self.database = database
        self.collection_name = collection
        self.collection = collection
        self.openDB()

    def openDB(self):
        if self.db_owner == 'amy':
            user = 'root'
            passwd = 'utf8utf8'
            host = 'jztx.tpddns.cn'
            port = '27011'
            auth_db = 'admin'
            # uri = "mongodb://localhost"
            uri = "mongodb://" + user + ":" + passwd + "@" + host + ":" + port + "/" + auth_db + "?authMechanism=SCRAM-SHA-1"
        elif self.db_owner == 'local':
            user = 'terry'
            passwd = 'utf8utf8'
            host = 'localhost'
            port = '27017'
            auth_db = 'admin'
            uri = "mongodb://" + user + ":" + passwd + "@" + host + ":" + port + "/" + auth_db + "?authMechanism=SCRAM-SHA-1"
        elif self.db_owner == 'amy_inside':
            user = 'root'
            passwd = 'utf8utf8'
            host = '192.168.0.21'
            port = '27017'
            auth_db = 'admin'
            uri = "mongodb://" + user + ":" + passwd + "@" + host + ":" + port + "/" + auth_db + "?authMechanism=SCRAM-SHA-1"
        self.con = MongoClient(uri, connect=False)
        self.db = self.con[self.database]
        self.collection = self.db[self.collection]

    def readDB(self, filter_con={}, filter_con_2={}):
        data_list = self.collection.find(filter_con, filter_con_2)
        data = pd.DataFrame(list(data_list))
        return data

    def insertDB(self, df):
        self.collection.insert_many(json.loads(df.T.to_json()).values())
        print(
            format(self.collection_name) + '_update_time: ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f'))

    def dropDB(self, filter_con={}):
        result = self.collection.delete_many(filter_con)
        print('Delete_num: ' + str(result.deleted_count))

    def closeDB(self):
        self.con.close()

    def get_index(self, col):
        self.collection.create_index([(col, pymongo.ASCENDING)])

    def dropSheet(self):
        self.collection.drop()
