from django.shortcuts import render
from django.http import HttpResponse
from pymongo import MongoClient
from random import sample, choice
import json

databaseName = 'coco'
client = MongoClient('localhost', 27017)

db = client[databaseName]
anns = db['annotations']
images = db['images']
categories = db['categories']
captions = db['captions']
ocr = db['ocr']


# Create your views here.
def index(request):
    return HttpResponse('This is an experiment for COCO reader')


def annotations(request):
    a = anns.find_one()
    return HttpResponse(a)


def get_random_image(request):
    N_CAT = 3

    # sample N_CAT categories
    cats = anns.distinct('category_id')
    sample_cats = sample(cats, N_CAT)

    # image ids with either combination of the N_CAT categories
    img_ids = []
    for cat in sample_cats:
        img_ids += list(anns.find({'category_id': cat}, {'image_id': 1, '_id': 0}))

    # pick a random image
    rand_image_id = sample(img_ids, 1)[0]['image_id']

    img_anns = list(anns.find({'image_id': rand_image_id}))
    img_ocr = list(ocr.find({'image_id': rand_image_id}))

    img = {}
    img['image_id'] = rand_image_id
    img['bboxes'] = []
    img['file_name'] = images.find_one({'id': rand_image_id})['file_name']
    img['ocr'] = []

    for ia in img_anns:
        bb = {}
        bb['category_id'] = ia['category_id']
        bb['category_name'] = categories.find_one({'id': ia['category_id']})['name']
        bb['bbox'] = {}
        bb['bbox']['x'] = ia['bbox'][0]
        bb['bbox']['y'] = ia['bbox'][1]
        bb['bbox']['w'] = ia['bbox'][2]
        bb['bbox']['h'] = ia['bbox'][3]
        img['bboxes'] += [bb]
        if ia['iscrowd'] is 0:
            img['RLE'] = False
        else:
            img['RLE'] = True
        img['segmentation'] = ia['segmentation']

    # alternatively we can just use the same bboxes object - but need to standardize
    # can add filters for score...
    for io in img_ocr:
        bb = {}
        bb['string'] = io['utf8_string']
        bb['score'] = io['score']
        bb['bbox'] = {}
        bb['bbox']['x'] = io['bbox'][0]
        bb['bbox']['y'] = io['bbox'][1]
        bb['bbox']['w'] = io['bbox'][2]
        bb['bbox']['h'] = io['bbox'][3]
        bb['bbox']['a'] = io['bbox'][4]
        img['ocr'] += [bb]

    return HttpResponse(json.dumps(img))


def get_random_caption(caps):
    single_cap = choice(caps)
    temp = {}
    temp['image_id'] = single_cap['image_id']
    temp['caption'] = single_cap['caption']
    return temp


def get_survey_options(request, img_id):
    img_id = int(img_id)
    results = []

    # good caption
    good_caps = list(captions.find({'image_id': img_id}, {'caption': 1, 'image_id': 1}))
    results.append(get_random_caption(good_caps))

    # get captions
    cats = anns.find({'image_id': img_id}, {'category_id': 1})
    cats = list(set([annot['category_id'] for annot in cats]))

    # similar caption
    # alternatively, take a fraction of the cats...
    N_CAT = 2
    sample_cats = sample(cats, N_CAT)
    # this is not efficient, probably can do this in mongo but confusing
    img_pool = [set([cat['image_id'] for cat in list(anns.find({'category_id': cat}, {'image_id': 1}))]) for cat in sample_cats]
    img_int = list(set.intersection(*img_pool))
    similar_caps_i = choice(img_int)
    similar_caps = list(captions.find({'image_id': similar_caps_i}, {'caption': 1, 'image_id': 1}))
    results.append(get_random_caption(similar_caps))

    # bad caption
    bad_cap_i = choice(list(anns.find({'category_id': {'$nin': cats}}, {'image_id': 1})))['image_id']
    bad_caps = list(captions.find({'image_id': bad_cap_i}, {'caption': 1, 'image_id': 1}))
    results.append(get_random_caption(bad_caps))

    # order is [good, similar, bad]
    # do query for imgs - need some heuristic
    return HttpResponse(json.dumps(results))


def get_survey_image(request, img_id):
    # cap_id = int(cap_id)
    # img_id = captions.find_one({'id': cap_id})['image_id']
    # find the image filename using image id
    img_id = int(img_id)
    img_loc = images.find_one({'id': img_id})['file_name']
    # return image location
    return HttpResponse(json.dumps({"file_name":img_loc}))