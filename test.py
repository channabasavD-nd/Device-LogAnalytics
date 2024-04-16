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
line = '2024-04-05 14:11:56,729 - root - INFO - We are going to operate on the obsdata file  metadata file /home/iriscli/ND_INPUT/0_trip15ec_part0687bc_40.6701_-73.7857_0.0_1712326201793_ymetadata.txt and output folder /home/iriscli/ND_OUTPUT/0_trip15ec_part0687bc_40.6701_-73.7857_0.0_1712326201793_y'
pattern = r'.*root - INFO - We are going to operate on.*0(_trip.*_y).*'

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
#     print(f"Collection '{collection_name}': Number of documents updated:", result.modified_count)a = 
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