from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
from random import sample
import json

databaseName = "coco"
client = MongoClient('localhost', 27017)

db = client[databaseName]
anns = db["annotations"]
images = db["images"]
categories = db["categories"]

# Create your views here.
def index(request):
    return HttpResponse("This is an experiment for COCO reader");

def annotations(request):
    a = anns.find_one()
    return HttpResponse(a);

def get_random_image(request):
    N_CAT = 3
    
    # sample N_CAT categories
    cats = anns.distinct("category_id")
    sample_cats = sample(cats, N_CAT)
    
    # image ids with either combination of the N_CAT categories
    img_ids = []
    for cat in sample_cats:
        img_ids += list(anns.find({"category_id": cat},{"image_id": 1, "_id": 0}))
    
    # pick a random image
    rand_image_id = sample(img_ids,1)[0]['image_id']
    
    img_anns = list(anns.find({"image_id": rand_image_id}))
    img = {}
    img['image_id'] = rand_image_id
    img['bboxes'] = []
    img['file_name'] = images.find_one({"id": rand_image_id})["file_name"]
    
    for ia in img_anns:
        bb = {}
        bb["category_id"] = ia["category_id"]
        bb["category_name"] = categories.find_one({"id":ia["category_id"]})["name"]
        bb["bbox"] = {}
        bb["bbox"]["x"] = ia["bbox"][0]
        bb["bbox"]["y"] = ia["bbox"][1]
        bb["bbox"]["w"] = ia["bbox"][2]
        bb["bbox"]["h"] = ia["bbox"][3]
        img["bboxes"] += [bb]

    return HttpResponse(json.dumps(img))
