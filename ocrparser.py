import json
import datetime


__author__ = 'jhh283'
__version__ = '1.0'


class OCR():
    def __init__(self, annotation_files=None):
        print 'Loading and preparing annotations...'
        time_t = datetime.datetime.utcnow()
        ocr_data = []
        for file in annotation_files:
            loaded_anns = json.load(open(file))
            assert type(ocr_data) == list, 'results in not an array of objects'
            ocr_data.append(loaded_anns)

        imgToAnns = {ann['image_id']: [] for file in ocr_data for ann in file}
        for file_id, file in enumerate(ocr_data):
            for ann_id, ann in enumerate(file):
                imgToAnns[ann['image_id']] += [((file_id, ann_id), ann)]

        self.ocr_data = ocr_data
        self.imgToAnns = imgToAnns
        print 'DONE (t=%0.2fs)' % ((datetime.datetime.utcnow() - time_t).total_seconds())

    def getAllImgIds(self):
        return self.imgToAnns.keys()

    def getAnnsFromIds(self, imgIds=[]):
        imgIds = imgIds if type(imgIds) == list else [imgIds]
        anns = {imgId: [] for imgId in imgIds if imgId in self.imgToAnns}
        for imgId in imgIds:
            if imgId in self.imgToAnns:
                anns[imgId] += self.imgToAnns[imgId]
        return anns

if __name__ == "__main__":
    annotations_dir = '../annotations/ocr_annotations'
    files = ['annotation-val.json', 'annotation-train.json', 'annotation-test.json']
    o = OCR([annotations_dir + '/' + file for file in files])
    print len(o.getAllImgIds())
    print o.getAnnsFromIds(192186)
