#!/usr/bin/env python3

import argparse
import subprocess
from urllib.request import urlopen
import json

def CreateDictionary(packageName, version):
    res = {}
    for key in packageName:
        for value in version:
            res[key] = value
            version.remove(value)
            break
    return dict(res)

def ProcessArgs(image_version):
    result = subprocess.run(['syft', 'packages', '%s:%s' % (image, image_version)], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8').split()

    packageName = output[0::3]
    packageName.pop(0)

    version = output[1::3]
    version.pop(0)

    return CreateDictionary(packageName, version)

def VerifyInput(image, firstT, secondT):
    dockerUrl = "https://registry.hub.docker.com/v1/repositories/%s/tags"%image
    try:
        response = urlopen(dockerUrl)
    except:
        print(f"Image '{image}' is not valid! Please verify your input.")
        quit()

    data_json = json.loads(response.read())

    if ((len(firstT) > 1) and (len(secondT) > 1)):
        if (str(firstT) not in str(data_json)):
            print(f"{firstT} is not a valid tag, at least not for '{image}'.")
            quit()
            
        if (str(secondT) not in str(data_json)):
            print(f"{secondT} is not a valid tag, at least not for '{image}'.")
            quit()
    else:
        print("Invalid tags.")
        quit()

def PrintDifferences(tags1, tags2):
    newPackages = []
    for key in tags1:
        if ( key in tags2 ):
            print(f"{key}:\n {tags1[key]} [{firstT}] -> {tags2[key]} [{secondT}]\n")
        else:
            newPackages.append(key)
    print(f"Packages that are in {image}/{firstT} but are not in {image}/{secondT}:\n {newPackages}")

parser = argparse.ArgumentParser(description="This tool is used to find the major package updates from different tags of the same image.")

parser.add_argument('--image', required = True, type = str, help = "Docker image that you want to compare")
parser.add_argument('--first-tag', required = True, type = str, help = "First tag of the image you want to compare")
parser.add_argument('--second-tag', required = True, type = str, help = "Second tag of the image you want to compare")

parsedArgs = parser.parse_args()

VerifyInput(parsedArgs.image, parsedArgs.first_tag, parsedArgs.second_tag)

image = parsedArgs.image
firstT = parsedArgs.first_tag
secondT = parsedArgs.second_tag

tags1 = ProcessArgs(firstT)
tags2 = ProcessArgs(secondT)

PrintDifferences(tags1, tags2)
