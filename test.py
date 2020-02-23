from pymongo import MongoClient

url_server = 'mongodb+srv://Artur:Clashofclans00@mongo-qiim9.gcp.mongodb.net/test?retryWrites=true&w=majority'
client_mongo = MongoClient(url_server)
database = client_mongo['web-test']
urls_collection = database['url-data']

data = {'link': 'https://www.python.org', 'words': [{'keyword': 'python', 'amount': 61, 'percent': 8.243243243243244}]}

new = [{'keyword': 'python', 'amount': 61, 'percent': 8.243243243243244},
       {'keyword': 'java', 'amount': 0, 'percent': 0}]

q = urls_collection.find_one({'link': 'https://www.python.org'})
q['words'].append(5)
print(q)
#x = urls_collection.insert_one(data)
#urls_collection.update_one({'link': 'https://www.python.org'}, {'$set': {'words': new}})


