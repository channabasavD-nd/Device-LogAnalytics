# from pymongo import MongoClient

# mongo_connectionStr = 'mongodb://10.200.10.181:27017/'
# Mongo_db = 'Device_log_tracebacks'
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

# from pymongo import MongoClient

# # Connect to MongoDB
# client = MongoClient('mongodb://10.200.10.181:27017/')
# db = client['Device_log_tracebacks']
# collection = db['3.6.4.rc.2_3633090953']

# # Define the dates to keep
# dates_to_keep = ['2024-03-12', '2024-03-13', '2024-03-15']

# # Delete documents that don't have 'date' field matching the specified dates
# result = collection.delete_many({'date': {'$nin': dates_to_keep}})

# print(f"Deleted {result.deleted_count} documents.")
import re

# Input line
line = '1713309952021: 2261055: AS: I: 5168: 5378: Outward - Session Change. New session Registered, Length = 61, Name = 0_trip0044_part0007d6_13.0270_77.7610_0.0_1713309951972_y.mkv, StartFrameCnt = 0'
line2 = '1712302624832: 324706: AS: I: 5074: 5638: Outward - Session Change. New session Registered, Length = 82, Name = /home/iriscli/files/0_trip065b_part00232c_44.9634_-92.7247_0.0_1712302624715_y.mkv, StartFrameCnt = 0'
pattern = r'\d+: \d+: AS: I: \d+: \d+: (.*ward) - Session Change.*0(_trip.*_y).*'

# Search for the pattern in the line
match = re.search(pattern, line)

# If a match is found
if match:
    # Extract the name
    name = match.group(1)
    print(type(name))
    print("Name:", name)
else:
    print("Pattern not found in the line.")
# from pymongo import MongoClient

# # Connect to MongoDB
#  # Replace 'your_database_name' with your database name
# client = MongoClient(mongo_connectionStr)
# db = client[Mongo_db]

# collection_names = db.list_collection_names()

# # Iterate through each collection
# for collection_name in collection_names:
#     # Get the collection object
#     collection = db[collection_name]
    
#     # Specify the query to find documents with the old field name
#     query = {"analyticsService.Outward session drop": {"$exists": True}}
    
#     # Specify the update operation
#     update = {"$rename": {"analyticsService.Outward session drop": "analyticsService.Outward_session_drop"}}
    
#     # Update the documents in the collection
#     result = collection.update_many(query, update)
    
#     # Print the number of documents updated
#     print(f"Collection '{collection_name}': Number of documents updated:", resultnt)a = 
# collections = db.list_collection_names()

# # Iterate through each collection
# for collection_name in collections:
#     collection = db[collection_name]
    
#     # Check if the collection is empty
#     if collection.estimated_document_count() == 0:
#         # Delete the empty collection
#         db.drop_collection(collection_name)
#         print(f"Collection '{collection_name}' deleted because it was empty.")

# # Close the MongoDB connection
# client.close()



from pymongo import MongoClient

# # Connect to the MongoDB database
# client = MongoClient('mongodb://10.200.10.181:27017/')
# db = client['Device_log_tracebacks']

# # Get a list of all collection names in the database
# collection_names = db.list_collection_names()

# # Iterate through each collection
# for collection_name in collection_names:
#     if collection_name == '3633000227_2024-04-05':
#         continue
#     collection = db[collection_name]
    
#     # Update each document in the collection
#     collection.update_many({}, {'$set': {'inferenceInertial_sessionID':{}}})
