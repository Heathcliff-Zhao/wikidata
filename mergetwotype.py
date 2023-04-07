from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import requests
import re
import time


proxy='127.0.0.1:7898'
proxies={
        'http': 'http://'+proxy,
        'https': 'http://'+proxy
        }
# def process(ele: str, mode: str) -> dict:
def process(ele: str) -> dict:
    # assert mode in ['gallery', 'in-context'], 'mode should be gallery or in-context'
    # segs = ele.split("|")
    # for example, an .odd file is not a valid image file
    tgt_format = ['.jpg', '.png', '.svg', '.tif', '.tiff', '.jpeg', '.JPG', '.PNG', '.SVG', '.JPEG', '.TIF', '.TIFF']
    resolution=[]
    ele = ele.strip('[[').strip(']]')
    ele = ele.strip(' ')
    first_segpos = ele.find("|")
    image_ori_url = 'https://zh.wikipedia.org/wiki/' + ele[:first_segpos].replace(' ', '_').strip('[[').strip(' ')
    # image_ori_url='https://commons/wikimedia.org/wiki/'+ele[:first_segpos].replace(' ','_').strip('[[').strip(' ')
    flag = False
    for format in tgt_format:
        if image_ori_url.endswith(format):
            flag = True
            break
    if not flag:
        return {}
    # get url of image can be downloaded
    try:
        response=requests.get(image_ori_url,proxies=proxies)
    except:
        time.sleep(5)
        try: 
            response=requests.get(image_ori_url,proxies=proxies)
        except:
            time.sleep(1)
            return {}
    # response=requests.get(image_ori_url,proxies=proxies)
    # print(response.status_code)
    # print(image_ori_url)
    soup=BeautifulSoup(response.content,'html.parser')
    # print(soup)
    imglist=soup.find_all('a',class_='mw-thumbnail-link')
    # print(imglist[-1])
    if len(imglist)==0:
        return {}
    image_url='https:'+imglist[-1]['href']
    # image_url=imglist[-1]['href']
    resolution=imglist[-1].text.split('×')
    resolution[1]=resolution[1].strip(' ')
    resolution[1]=resolution[1].strip('像素')
    resolution[1]=resolution[1].strip('pixels')
    resolution[0]=resolution[0].strip(' ')
    resolution[1]=resolution[1].strip(' ')
    resolution[0]=int(resolution[0].replace(',',''))
    resolution[1]=int(resolution[1].replace(',',''))
    caption=ele[first_segpos+1:]
    caption=caption.replace('{{','').replace('}}','')
    caption=caption.strip(' ').lstrip('thumb').strip(' ').lstrip('|').lstrip('right').strip(' ').lstrip('|').strip(' ').lstrip('left').strip(' ').lstrip(
            '|').strip(' ').lstrip('center').strip(' ').lstrip('|').lstrip('upright=0.9').strip(' ').lstrip('|').strip(' ').rstrip('(').strip(' ').lstrip(
            'thumb').strip(' ').lstrip('|').replace('thumb|','').replace('right|','').replace('left|','').replace('center|','').replace(
            'upright=0.9|','').replace('thumb |','').replace('right |','').replace('left |','').replace('center |','').replace(
            'upright=0.9 |','').replace('thumb |','').replace('right |','').replace('left |','').replace('center |','')
    trash_pos=caption.find('px|')
    if trash_pos!=-1:
        caption=caption[trash_pos+3:]
    fi_pos = image_ori_url.find('wiki/File:')
    filename_caption = image_ori_url[fi_pos + 10:-4].replace('_', ' ') if image_ori_url[-4] == '.' else image_ori_url[
                                                                                        fi_pos + 10:-5].replace('_',
                                                                                                                ' ')
    filter_pos = caption.find('|')
    if filter_pos != -1 and filter_pos<8:
        caption = caption[filter_pos + 1:]
    caption = caption.replace("[", "").replace("]", "")
    caption = re.sub(r'<ref.*?</ref>', '', caption)
    
    extract_pattern = re.compile(r'<div.*?>(.*?)</div>')
    tmp=re.search(extract_pattern,caption)
    if tmp != None:
        caption=re.search(extract_pattern,caption).group(1)
    if caption.startswith('alt='):
        caption = caption[4:]
    if caption.endswith('px') and (caption.strip().strip('px').strip().isdigit() or caption.strip().strip('px').strip().replace('x','').isdigit()):
        caption=''
    return {'image_url': image_url, 'image_resolution': resolution, 'caption': caption, 'filename_caption': filename_caption, 'image_info_url': image_ori_url}


with open(
        "../enwiki/enwiki-20230320-pages-articles-multistream1.xml",
        'r', encoding='utf-8') as f:
    xml_file = f.read()

soup = BeautifulSoup(xml_file, 'xml')

texts = soup.find_all('text')
titles = soup.find_all('title')
res = []
for i in tqdm(range(926,len(texts))):
# for i in tqdm(range(67,68)):
    # for i in range(60,70):
    now = {}
    now['title'] = titles[i].text
    pos = texts[i].text.find("== Gallery ==")
    gallery_example = []
    if pos != -1:
        lp = texts[i].text.find("<gallery>")
        rp = texts[i].text.find("</gallery>")
        gallery_ori_str = texts[i].text[lp:rp]
        gallery_ori_str = gallery_ori_str.strip('<gallery>')
        gallery_ori_str = gallery_ori_str.strip('</gallery>')
        gallery_example = [process(ele) for ele in gallery_ori_str.split("\n") if ele != '']
        while {} in gallery_example:
            gallery_example.remove({})
    now['gallery'] = gallery_example

    incontextimgpos = []
    startpos = 0
    endpos = texts[i].text.find('<gallery>')
    if endpos == -1:
        endpos = len(texts[i].text)
    while (startpos < endpos):
        pos = texts[i].text.find('[[File:', startpos, endpos)
        if pos != -1:
            incontextimgpos.append(pos)
            startpos = pos + 1
        else:
            break
    imagewithcaption = []
    for pos in incontextimgpos:
        amark = False
        bmark = False
        stack = []
        for left in range(pos, endpos):
            if texts[i].text[left] == '[' and not amark:
                amark = True
            elif texts[i].text[left] == '[' and amark:
                amark = False
                stack.append('[[')
            elif texts[i].text[left] == ']' and not bmark:
                bmark = True
            elif texts[i].text[left] == ']' and bmark:
                bmark = False
                stack.pop()
            if len(stack) == 0 and left - pos > 3:
                ele = process(texts[i].text[pos:left + 1])
                if ele != {}:
                    imagewithcaption.append(ele)
                break
    now['image-caption'] = imagewithcaption
    if len(now['gallery']) != 0 or len(now['image-caption']) != 0:
        res.append(now)
# print(res)
    if i%5==0:
        with open('res.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False)
print(len(res))
