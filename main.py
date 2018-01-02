import threading
import requests
import Queue as queue
import re
import shutil
import os
from bs4 import BeautifulSoup

NUM_THREAD = 32

def get_cat():
    url = 'http://burst.shopify.com/free-images'
    req = requests.get(url)
    parse_html = BeautifulSoup(req.text, 'lxml')
    cat_div = parse_html.find_all('div', class_=re.compile('grid__item--desktop'))

    img_cat = []
    for div in cat_div:
        try:
            img_cat.append(div.a['href'].replace('/', ''))
        except:
            pass

    return img_cat

def download_img(q):
	while True:
		try:
			link, fol = q.get()
		except queue.Empty:
			break
		else:
			print "Downloading image: " + link
			req = requests.get(link, stream=True)
			if not os.path.exists(fol):
				os.makedirs(fol)
			img_name = './' + fol + '/' + link.split('/')[-1]
			if not os.path.exists(img_name):
				with open(img_name, 'wb') as f:
					shutil.copyfileobj(req.raw, f)
			q.task_done()


def get_imgs_of_cat(cat):
    img_url = 'http://burst.shopify.com/' + cat
    # Get number of pages:
    req = requests.get(img_url)
    parse_html = BeautifulSoup(req.text, 'lxml')
    try:
        pages = int(parse_html.find('span', class_='last').a['href'].split('=')[-1])
        imgs = []
        for p in range(1, pages):
            if (p > 1):
                url = img_url + '?page=' + str(p)
                req = requests.get(url)
                parse_html = BeautifulSoup(req.text, 'lxml')

            img_el = parse_html.find_all('a', class_='photo-tile__image-wrapper')
            for el in img_el:
                try:
                    img_link = el.img['data-srcset'].split(',')[0].split('_')[0] + '_4460x4460.jpg'
                    imgs.append(img_link)
                except:
                    pass
    except:
        pass
    return imgs


img_cats = get_cat()
print
"There are: " + str(len(img_cats)) + ' category'
for c in img_cats:
	
	print "Crawling category: " + c
	imgs = get_imgs_of_cat(c)
	print "There are: " + str(len(imgs)) + ' images in ' + c + ' category'
	q = queue.Queue()
	for i in imgs:
		q.put((i, c,))

	for i in range(NUM_THREAD):
		t = threading.Thread(target=download_img, args=(q,))
		t.start()
	q.join()
		
	print "\n===============\n"
