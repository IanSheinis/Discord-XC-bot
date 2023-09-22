import json
import os

"""
Import from and retrieve json data
"""

class NotAFile(Exception):

    """
    When inserted file is not a file
    """

    pass


class NotJson(Exception):

    """
    When not a json file
    """

    pass


class Retrieval:

    """
    Retrieve from json file
    """

    data: dict


    @staticmethod
    def retrieve(fName: str) -> dict:

        if not os.path.isfile(fName):
            raise NotAFile
        
        if fName[-5:] != ".json":
            raise NotJson
        
        with open(fName) as f:
            Retrieval.data = json.load(f)

        return Retrieval.data


    @staticmethod
    def send(fName: str, data: dict) -> None:
        
        if fName[-5:] != ".json":
            raise NotJson
        
        with open(fName, 'w') as f:
            Retrieval.data = json.dump(data, f, indent=2)

        Retrieval.data = data




        

        