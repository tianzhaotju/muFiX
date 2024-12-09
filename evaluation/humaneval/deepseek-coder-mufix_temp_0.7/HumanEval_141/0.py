import re

def file_name_check(file_name):
    """
    Create a function which takes a string representing a file's name, and returns 'Yes' if the the file's name is valid, and returns 'No' otherwise.
    A file's name is considered to be valid if and only if all the following conditions are met:
    - There should not be more than three digits ('0'-'9') in the file's name.
    - The file's name contains exactly one dot '.'
    - The substring before the dot should not be empty, and it starts with a letter from the latin alphapet ('a'-'z' and 'A'-'Z').
    - The substring after the dot should be one of these: ['txt', 'exe', 'dll']
    """
    if file_name.count('.') != 1:
        return 'No'
    if re.match(r'^[a-zA-Z]', file_name.split('.')[0]) is None:
        return 'No'
    if re.search(r'\d{4,}', file_name.split('.')[0]) is not None:
        return 'No'
    if file_name.split('.')[1] not in ['txt', 'exe', 'dll']:
        return 'No'
    return 'Yes'