import mimetypes
import time

import os
import requests
import sys
from flask import request

from common.blueprint import Blueprint
from common.utils.json_utils import query_list_to_dict
from api.user.models import DownloadData
from common.connection import add_item
from common.response import success, failure
import threading

user_api = Blueprint('user', __name__, url_postfix='user')

@user_api.route('/download', methods=['GET'])
def download():
    try:
        #getting thr file from arugument.
        url = request.args['url']

        #getting the basic information from url.
        r = requests.get(url, stream=True)
        content_type = r.headers['content-type']
        extension = mimetypes.guess_extension(content_type)
        ts = int(time.time())
        #getting the content length from response
        total_length = r.headers.get('content-length')
        #download start time .
        start = time.clock()
        #creaing local path with timestamp for store url.
        local_url = "storage/file_" + str(ts) + "" + str(extension)

        #storing basic information in table.
        d_data = DownloadData()
        d_data.file_name = local_url
        d_data.file_length = int(total_length)
        d_data.start_time = start
        res = add_item(d_data)

        #taking the last inserted unique inserted id from table
        download_id = res.id
        dic = {}
        dic["unique_id"] = download_id
        # fileDownload(url, local_url, start)

        #Downloading function calling in thread.
        t1 = threading.Thread(target=fileDownload, args=(url,local_url,start, ))
        t1.start()

        #returning the inserted record unique id
        return success("Success",dic)
    except Exception as err:
        return failure("Fail" + str(err))

def fileDownload(url,local_url,start):
    try:
        #Open the local file in write mode
        with open(local_url, "wb") as wordlist:
            #Opening the url using the requests
            response = requests.get(url, stream=True)
            #getting the total length of the file from response.
            total_length = response.headers.get('content-length')

            #checking the condetion if lenght of file is empty or not
            if total_length is None:
                wordlist.write(response.content)
            else:
                #else downloading the file
                downloaded = 0
                total_length = int(total_length)
                #iterating the response with chunk_size=1024
                for data in response.iter_content(chunk_size=1024):
                    #to caluclate how much data downloaded till.
                    downloaded += len(data)
                    #Writing data to local file.
                    wordlist.write(data)

                    #to show progress bar while running thread.
                    done = int(50 * downloaded / total_length)
                    sys.stdout.write("\r[%s%s] %s bps" % ('=' * done, ' ' * (50 - done), downloaded // (time.clock() - start)))
                    sys.stdout.flush()
        return 1
    except Exception as err:
        print(err)
        return 0

@user_api.route('/status', methods=['GET'])
def status():
    try:
        #Accepting the is as from args
        id = request.args['id']
        #Querying to databse based on id
        result = DownloadData.query.filter_by(id=id)
        result = query_list_to_dict(result)

        #checking wheather result is there or not for the given id.
        if len(result) > 0:
            dic = {}
            #assinging result dict to item keyword.
            item = result[0]
            #Strong donloaded data till in downloaded_data
            downloaded_data = 0
            if item["file_name"] is not None:
                #getting the file size which we have stored earlier to check downloaded data till.
                downloaded_data = os.path.getsize(item["file_name"])
            dic["downloaded_file_size"] = downloaded_data

            #taking the length of the file from db which we inserted earlier.
            length = 0
            if item["file_length"] is not None:
                length = item["file_length"]
            dic["total_file_size"] = length

            # taking the downloaded start time from db which we inserted earlier.
            start_time = 0
            if item["start_time"] is not None:
                start_time = item["start_time"]
            # dic["start_time"] = start_time

            #Caluclating remaining data
            remaining_data = length - downloaded_data

            #Assigning status based on remaining_data
            if remaining_data != 0:
                dic["status"] = "Downloadig."
            else:
                dic["status"] = "Completed."
            dic["remaining_file_size"] = remaining_data

            #Caluclating Speed based on starting time of download and downloaded data
            speed = downloaded_data // (time.clock() - start_time)
            # dic["speed"] = speed

            # Caluclating Estimated time to complete download using speed and remaining data
            expected_time = remaining_data / speed
            expected_time = round(expected_time,2)
            dic["estimated_time_to_complete"] = str(expected_time) + " Sec"

            #returning the response
            return success("Success",dic)
        else:
            return failure("Data not found",400)
    except Exception as err:
        return failure("Fail" + str(err))