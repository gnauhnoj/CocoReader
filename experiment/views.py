from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, Http404
from pymongo import MongoClient
from random import sample, choice, shuffle
from view_helpers import build_img_dict, get_random_caption
from django.views.decorators.csrf import csrf_exempt
import models
import json
import numpy as np
import logging

logger = logging.getLogger(__name__)

databaseName = 'coco'
client = MongoClient('localhost', 27017)

db = client[databaseName]
anns = db['annotations']
images = db['images']
categories = db['categories']
captions = db['captions']
ocr = db['ocr']
users = db['experiment_user']


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
    img = build_img_dict(rand_image_id, anns, ocr, images, categories)

    return HttpResponse(json.dumps(img))


def get_random_ocr(request):
    # sample OCR
    ocr_imgs = ocr.distinct('image_id')
    rand_image_id = sample(ocr_imgs, 1)[0]
    img = build_img_dict(rand_image_id, anns, ocr, images, categories)
    return HttpResponse(json.dumps(img))


def get_survey_options(request, img_id):
    img_id = int(img_id)
    results = []

    # good caption
    good_caps = list(captions.find({'image_id': img_id}, {'caption': 1, 'image_id': 1, 'id': 1}))
    results.append((get_random_caption(good_caps), 2))

    # get captions
    cats = anns.find({'image_id': img_id}, {'category_id': 1})
    cats = list(set([annot['category_id'] for annot in cats]))

    # similar caption
    N_CAT = 2 if len(cats) > 1 else len(cats)
    sample_cats = sample(cats, N_CAT)
    # this is not efficient, probably can do this in mongo but confusing
    img_pool = [set([cat['image_id'] for cat in list(anns.find({'category_id': cat}, {'image_id': 1}))]) for cat in sample_cats]
    img_int = list(set.intersection(*img_pool))
    similar_caps_i = choice(img_int)
    similar_caps = list(captions.find({'image_id': similar_caps_i}, {'caption': 1, 'image_id': 1, 'id': 1}))
    results.append((get_random_caption(similar_caps), 1))

    # bad caption
    bad_cap_i = choice(list(anns.find({'category_id': {'$nin': cats}}, {'image_id': 1})))['image_id']
    bad_caps = list(captions.find({'image_id': bad_cap_i}, {'caption': 1, 'image_id': 1, 'id': 1}))
    results.append((get_random_caption(bad_caps), 0))
    shuffle(results)

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
    return HttpResponse(json.dumps({"file_name": img_loc}))


def get_user_score(request, username):
    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        user = models.User(username=username)
        user.save()
    out = {
        'username': user.username,
        'score': user.score
    }
    return HttpResponse(json.dumps(out))


# @csrf_exempt
def update_score(request, username):
    score = request.POST.get('score')
    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        raise Http404('Something went wrong. Contact admin.')
    user.score += int(score)
    user.save()
    out = {
        'username': user.username,
        'score': user.score
    }
    return HttpResponse(json.dumps(out))


def get_leaderboard(request):
    top_users = list(users.find().sort([('score', -1)]).limit(10))
    top_users = [{'username': user['username'], 'score': user['score']} for user in top_users]
    return HttpResponse(json.dumps(top_users))


def update_score_helper(username, caption_type, image_outcome, image_response, caption_outcome):
    # +1 point if get_survey_options[1] != 0
    # +1 point if get_survey_options[1] != 0 && get_survey_image == get_random_image && answer is yes
    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        raise Http404('Something went wrong. Contact admin.')
    score = 0
    if caption_type != 0:
        score += 1
        if image_outcome:
            score += 1
        elif image_response == 'false' and not caption_outcome:
            score += 1
    user.score += score
    user.save()
    return score


# @csrf_exempt
def record_outcome(request):
    username = request.POST.get('username')
    image_id = int(request.POST.get('image_id'))
    captions_used = int(request.POST.get('captions_used'))
    double_used = int(request.POST.get('double_used'))

    caption_type = request.POST.get('caption_type')
    caption_image_id = int(request.POST.get('caption_image_id'))
    image_response = request.POST.get('image_response')
    caption_outcome = (caption_image_id == image_id)
    # TODO: what should image_response be
    image_outcome = (image_response == 'true') and caption_outcome

    try:
        user = models.User.objects.get(username=username)
    except models.User.DoesNotExist:
        # raise Http404('Somethingg went wrong. Contact admin.')
        # TODO: change back once leaderboard is built out on client-side
        user = models.User(username=username)
        user.save()
    image_user = models.ImageUser(username=username, image_id=image_id, captions_used=captions_used, caption_outcome=caption_outcome, double_used=double_used, image_outcome=image_outcome)
    image_user.save()
    score = update_score_helper(username, int(caption_type), image_outcome, image_response, caption_outcome)
    out = {
        'username': image_user.username,
        'image_id': image_user.image_id,
        'captions_used': image_user.captions_used,
        'caption_outcome': image_user.caption_outcome,
        'image_outcome': image_user.image_outcome,
        'double_used': image_user.double_used,
        'score': score
    }
    return HttpResponse(json.dumps(out))


def get_next_user_num(request):
    out = str(users.count())
    return HttpResponse(out)
