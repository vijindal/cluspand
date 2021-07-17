import json

class fileIO:
    def write(structData,file_name):
    # open output file for writing
        with open(file_name, 'w') as filehandle:
            json.dump(structData, filehandle)
    def read(file_name):
        with open(file_name) as file:
            structData = json.load(file)
        return structData