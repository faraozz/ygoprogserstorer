import requests
import json
import os
import os.path
import PySimpleGUI as sg
from PIL import Image
import io

databaselink = "https://db.ygoprodeck.com/api/v7/cardinfo.php"



def download_all_cards():
    response = get_request(databaselink)
    #save to file
    with open("allcards.txt", "w") as outfile:
        json.dump(response.json()['data'], outfile, indent=4)

def read_all_cards():
    with open("allcards.txt", "r") as json_file:
        allcards = json.load(json_file)
    return allcards


def loadydkfile(filename, weight_hashmap):
    f = open(filename,"r")
    #string of ids seperated by commas. used for the request

    for id in f:
        if id[0] == "#" or id[0] == "ï" or id[0] == "!":
            pass
        else:
            if int(id[:len(id)-2]) in weight_hashmap:
                weight_hashmap[int(id[:len(id)-2])] +=1
            else:
                weight_hashmap[int(id[:len(id)-2])] = 1

    #remove last ","
    return weight_hashmap


def loadallydkfiles():
    weight_hashmap = {}
    #loop through all ydk files and perform loadydkfile
    for filename in os.listdir("ydkfiles"):
        if filename.endswith(".ydk"):
            weight_hashmap = loadydkfile("ydkfiles/"+ str(filename), weight_hashmap)

    print(weight_hashmap)
    return weight_hashmap

def get_cardlist_from_id(allcards, weight_hashmap):
    resulted_list = []

    for id, nr_copies in weight_hashmap.items():
        for card in allcards:
            if card['id'] == id:
                for iteration in range(0, nr_copies):
                    resulted_list.append(card)

    return resulted_list


def get_request(target):
    return requests.get(target)



def download_images(card_list):
    #create images folder if there is no
    if os.path.isdir("images"):
        pass
    else:
        os.mkdir("images")
        os.mkdir("images_small")

    #check what previous images are stored
    storedimages= {}
    for imagename in os.listdir("images"):
        storedimages[imagename] = True

    print("STORED IMAGES: ", storedimages)
    #now check for the new images
    for card in card_list:
        if str(card['id'])+".jpg" in storedimages:
            pass
        else:
            response_small = get_request("https://storage.googleapis.com/ygoprodeck.com/pics_small/"+str(card['id'])+ ".jpg")
            response = get_request("https://storage.googleapis.com/ygoprodeck.com/pics/"+str(card['id'])+ ".jpg")
            f_small = open("images_small/" + str(card['id']) + "_small.jpg", "wb")
            f_small.write(response_small.content)
            f_small.close()
            f = open("images/" + str(card['id']) + ".jpg", "wb")
            f.write(response.content)
            f.close()



    #for card_id in card_list:




def main():
    if os.path.isfile("allcards.txt"):
        print("allcards.txt already downloaded")
        pass
    else:
        print("downloading allcards.txt")
        download_all_cards()
        print("download completed")

    allcards = read_all_cards()
    weight_hashmap = loadallydkfiles()
    resulted_list = get_cardlist_from_id(allcards, weight_hashmap)
    print(resulted_list)

    print("*******************")

    #download all the cards' images
    download_images(resulted_list)

    print("************************")

    layout_list = []
    for card_nr in range(0, len(resulted_list)):
        layout_list.append(sg.Image(key="IMAGE"+str(card_nr)))

    # First the window layout in 2 columns
    layout_list.append(sg.Listbox(values = [], enable_events=True, size=(40, 20), key="-IMAGE LIST2-"))

    file_types = [("JPEG (*.jpg)", "*.jpg"), ("All files (*.*)", "*.*")]
    cards_viewer_all = [
        layout_list,
        [
            sg.Text("Image File"),
            sg.Input(size=(25, 1), enable_events=True, key="-FILE-"),
            sg.FileBrowse(file_types=file_types),
            sg.Button("Load Image"),
        ],
        [
        sg.Listbox(values = [], enable_events=True, size=(40, 20), key="-FILE LIST-")
        ]
    ]

    cards_viewer_specific =[

        [sg.Text("Choose an image from list on left:")],
        [sg.Text(size=(40, 1), key="-TOUT-")],
        [sg.Image(key="-IMAGE-")],
    ]
    layout = [
        [sg.Column(cards_viewer_all), sg.VerticalSeparator(), sg.Column(cards_viewer_specific),]
    ]
    window = sg.Window("Image Viewer", layout)
    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        filename = values["-FILE-"]
        if os.path.exists(filename):
            for image_nr in range(0, len(layout_list)-1):
                image = Image.open(values["-FILE-"])
                image.thumbnail((400, 400))
                bio = io.BytesIO()
                image.save(bio, format="PNG")
                window["IMAGE"+str(image_nr)].update(data=bio.getvalue())

    window.close()
if __name__ == "__main__":
    main()
