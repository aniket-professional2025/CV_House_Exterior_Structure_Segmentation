# CV_House_Exterior_Structure_Segmentation
This is the second project of my professional journey as an AI/ML developer. This project is developed for a client having good reputations in the market since last 10-15 years. This project is for the same client with the Room interior segmentation project.

## Problem Statement:
Given an exterior image of a building, my task is to segment different structures of the building (as shown in Stable Diffusion Web UI) and then using the paths of those segmentation masks, my goal is to make an interface where we can merge or split the segmentatation masks as we wish 

## WorkFlow:
Building Exterior Images --> SAM model --> Binary Mask Creation --> Making a .svg file for each Exterior Image (One .svg file will contain all the paths of the segmentation masks that are generated from one exterior image) --> Supply the .svg files to the application building team --> Use UI-UX, html, css, javascript, react to build the application and the interface.

#### SAM:
SAM or Segment Anything Model is a powerful segmentation tool developed by Facebook Meta is used to segment anything that is present in a image

#### SVG Image Generation:
It is a type of XML file with a specified height and width that contains different paths of different sections of the images. Now, for my project,I have created one .svg files for each exterior imges. Each .svg file contains all the paths of the segmentation masks images that are generated from one exterior image.

#### Next Steps:
The .svg files will be processed by the application building team and hence an interface will be created.
