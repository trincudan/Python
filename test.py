#!/usr/bin/env python3

import argparse
import subprocess
from urllib.request import urlopen
import json

parser = argparse.ArgumentParser(description="This tool is used to find the major package updates from different tags of the same image.")

parser.add_argument('--image', required = True, type = str, help = "Docker image that you want to compare")
parser.add_argument('--first-tag', required = True, type = str, help = "First tag of the image you want to compare")
parser.add_argument('--second-tag', required = True, type = str, help = "Second tag of the image you want to compare")

parsedArgs = parser.parse_args()

def main(image, firstT, secondT):
    
    def VerifyInput(image, firstT, secondT):        # Given arguments needs to be verified before doing anything else
        dockerUrl = "https://registry.hub.docker.com/v1/repositories/%s/tags"%image     # We will use this URL to see if the [IMAGE] exists
        try:
            response = urlopen(dockerUrl)       # Checking if the [IMAGE] exists + basic error handling
        except:
            print(f"Image '{image}' is not valid! Please verify your input.")
            quit()

        data_json = json.loads(response.read())     # We load in ${data_json} all the tags of the specified [IMAGE]

        if ((len(firstT) > 1) and (len(secondT) > 1)):  # This being a JSON, i've added this condition to exclude inputs lile {[,],.,',", etc.}
            if (str(firstT) not in str(data_json)):     # Checking if the [FIRST_TAG] is in this list
                print(f"{firstT} is not a valid tag, at least not for '{image}'.")
                quit()
                
            if (str(secondT) not in str(data_json)):
                print(f"{secondT} is not a valid tag, at least not for '{image}'.")
                quit()
        else:
            print("Invalid tags.")
            quit()
            
    def ProcessArgs(image_version):     # Given arguments are processed taking out the information that we need (packageName and his version) and put them in two separate lists
        result = subprocess.run(['syft', 'packages', '%s:%s' % (image, image_version)], stdout=subprocess.PIPE)
        output = result.stdout.decode('utf-8').split()

        packageName = output[0::3]
        packageName.pop(0)      # Here we just take out the first element from the list, because it's the column name ("Package")

        version = output[1::3]
        version.pop(0)          # Same for this one too

        return CreateDictionary(packageName, version)       # We are building a dictionary as {"Package-Name:Version"}

    def CreateDictionary(packageName, version):     # No comment on this function, pretty basic dictionary creation
        res = {}
        for key in packageName:
            for value in version:
                res[key] = value
                version.remove(value)
                break
        return dict(res)

    def PrintDifferences(tags1, tags2):     # The simplest solution that i could found for this exercise; comparing two dictionaries to see the differences
        newPackages = []
        for key in tags1:
            if ( key in tags2 ):        # If a package exists in both dictionaries, print the versions
                print(f"{key}:\n {tags1[key]} [{firstT}] -> {tags2[key]} [{secondT}]\n")
            else:
                newPackages.append(key)
        print(f"Packages that are in {image}/{firstT} but are not in {image}/{secondT}:\n {newPackages}")       # This is a bonus one; I thought that would be a nice feature to
                                                                                                                # see the packages that were eliminated through different versions
    VerifyInput(parsedArgs.image, parsedArgs.first_tag, parsedArgs.second_tag)

    image = parsedArgs.image
    firstT = parsedArgs.first_tag
    secondT = parsedArgs.second_tag

    tags1 = ProcessArgs(firstT)
    tags2 = ProcessArgs(secondT)

    PrintDifferences(tags1, tags2)

if __name__ == "__main__":
    main(parsedArgs.image, parsedArgs.first_tag, parsedArgs.second_tag)
