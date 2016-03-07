import numpy as np
from random import choice


def build_img_dict(img_id, anns, ocr, images, categories):
    img_anns = list(anns.find({'image_id': img_id}))
    img_ocr = list(ocr.find({'image_id': img_id}))

    img = {}
    img['image_id'] = img_id
    img['bboxes'] = []
    img['file_name'] = images.find_one({'id': img_id})['file_name']
    img['ocr'] = []
    img['segmentation'] = []

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
        # type list means polygons
        if (type(ia['segmentation']) == list):
            # a single object can have multiple polygons in case of overlap
            # append each to the segmentation list with coordinates and category name
            for seg in ia['segmentation']:
                # reshape to make list of (x,y) coordinates of the polygon
                img['segmentation'] += [{"points": np.array(seg).reshape((len(seg)/2), 2).tolist(), "category_name": bb['category_name']}]
        else:
            img['segmentation'] += ia['segmentation']

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
    return img


def get_random_caption(caps, avoid=None):
    single_cap = choice(caps)
    if avoid is not None:
        while single_cap in avoid:
            single_cap = choice(caps)
    temp = {}
    temp['image_id'] = single_cap['image_id']
    temp['caption'] = single_cap['caption']
    temp['caption_id'] = single_cap['id']
    return temp
