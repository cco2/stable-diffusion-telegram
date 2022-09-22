import os
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, __version__
from dotenv import load_dotenv
from time import sleep

load_dotenv()
connect_str = os.getenv('AZURE_STORAGE_CONNECTION_STRING')
local_path = os.getcwd()

def get_difference(cur_list, new_list):
    print("start get_difference()")
    for blob in new_list:
        print("searching " + blob.name)
        found = False
        testblob = blob
        for blob in cur_list:
            print("searching cur_list " + blob.name)
            if blob.name == testblob.name:
                found = True
                print("FOUND!")
                break
        print("loop done")
        if found == False:
            print("Found new blob " + testblob.name)
            return testblob

try:
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    container_name = "hackathon"
    container_client = blob_service_client.get_container_client(container_name)
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        print("\t" + blob.name)
    cur_blob_list = blob_list
    while(True):
        sleep(2)
        for blob in cur_blob_list:
            print("\t" + blob.name)
        new_blob_list = container_client.list_blobs()
        diff_blob = get_difference(cur_blob_list, new_blob_list)
        if diff_blob == None:
            print("Set is empty")
        else:
            print("Set is not empty")
            print("diff blob = " + diff_blob.name)
    
        cur_blob_list = new_blob_list

        #for blob in diff_blob_list:
        #    print("\t" + blob.name)
        #if len(unique) == 0:
        #    print("Set is empty")
        #else:
        #    print("Set is not empty")

    #download_file_path = os.path.join(local_path, str.replace(local_file_name ,'.txt', 'DOWNLOAD.txt'))
    #container_client = blob_service_client.get_container_client(container= container_name) 
    #print("\nDownloading blob to \n\t" + download_file_path)

    #with open(download_file_path, "wb") as download_file:
    #    download_file.write(container_client.download_blob(blob.name).readall())

except Exception as ex:
    print('Exception:')
    print(ex)
