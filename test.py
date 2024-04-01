# from pymongo import MongoClient

# mongo_connectionStr = 'mongodb://10.200.10.181:27017/'
# Mongo_db = 'Device_log_monitoring'
# collection_name = '3.6.4.rc.2_3633090953'

# def remove_duplicates():
#     try:
#         client = MongoClient(mongo_connectionStr)
#         db = client[Mongo_db]
#         collection = db[collection_name]

#         pipeline = [
#             # Group by fields other than _id
#             {"$group": {
#                 "_id": {
#                     "session_ID": "$session_ID" # Replace field1, field2, etc. with actual field names
            
#                     # Add more fields as needed
#                 },
#                 "doc_ids": {"$push": "$_id"},
#                 "count": {"$sum": 1}
#             }},
#             # Match groups with more than one document (i.e., duplicates)
#             {"$match": {
#                 "count": {"$gt": 1}
#             }}
#         ]

#         # Get duplicate documents' IDs
#         duplicates = list(collection.aggregate(pipeline))

#         # Remove duplicates, keeping only the first occurrence
#         for duplicate in duplicates:
#             del duplicate['doc_ids'][0]  # Keep the first occurrence, remove the rest
#             for doc_id in duplicate['doc_ids']:
#                 collection.delete_one({"_id": doc_id})
        
#         print('Duplicates removed successfully')

#     except Exception as e:
#         print("Exception in MongoDB:", e)

# # remove_duplicates()
# a = {'ass':0,'asass':2}
# print(list(a.keys())[0])

from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://10.200.10.181:27017/')
db = client['Device_log_monitoring']
collection = db['3.6.4.rc.2_3633090953']

# Define the dates to keep
dates_to_keep = ['2024-03-12', '2024-03-13', '2024-03-15']

# Delete documents that don't have 'date' field matching the specified dates
result = collection.delete_many({'date': {'$nin': dates_to_keep}})

print(f"Deleted {result.deleted_count} documents.")
