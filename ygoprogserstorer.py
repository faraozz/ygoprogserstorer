import requests


def loadydkfile(filename):
    f = open(filename,"r")
    #string of ids seperated by commas. used for the request
    string_of_ids = ""
    for id in f:
        if id[0] == "#" or id[0] == "ï" or id[0] == "!":
            pass
        else:
            string_of_ids += id+","



    #remove last ","
    string_of_ids = string_of_ids[:len(string_of_ids)-1]
    #string_of_ids.replace("\n", "")
    print(string_of_ids)
    return string_of_ids



def main():
    string_to_index = loadydkfile("The Duelist Genesis Draft.ydk")
    response = requests.get("https://db.ygoprodeck.com/api/v7/cardinfo.php?id=" + string_to_index)
    print(response.json())
if __name__ == "__main__":
    main()
