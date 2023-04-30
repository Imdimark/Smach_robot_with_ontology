from armor_api.armor_client import ArmorClient



def find_substrings(strings_list):
    matched_substrings = []
    for string in strings_list:
        start_index = string.find("#")
        end_index = string.find(">")
        while start_index != -1 and end_index != -1:
            substring = string[start_index + 1 : end_index]
            matched_substrings.append(substring)
            start_index = string.find("#", end_index)
            end_index = string.find(">", start_index)
    print (matched_substrings)
    return matched_substrings


armcli = ArmorClient("example", "ontoRef")
canreach = armcli.call('QUERY','OBJECTPROP','IND',['canReach', 'Robot1'])
find_substrings (canreach.queried_objects)    










   


