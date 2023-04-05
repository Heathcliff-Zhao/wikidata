from bs4 import BeautifulSoup
import json
from tqdm import tqdm
import requests
import re


all_format = set()
# def process(ele: str, mode: str) -> dict:
def process(ele: str) -> dict:
    # assert mode in ['gallery', 'in-context'], 'mode should be gallery or in-context'
    # segs = ele.split("|")
    # TODO: make sure the file format is in image format
    # for example, an .odd file is not a valid image file
    # tgt_format = ['.jpg', '.png', '.svg', '.jpeg', '.JPG', '.PNG', '.SVG', '.JPEG']

    ele = ele.strip('[[').strip(']]')
    ele = ele.strip(' ')
    first_segpos = ele.find("|")
    if ele[:first_segpos][-4]=='.':
        all_format.add(ele[:first_segpos][-4:])
    else:
        all_format.add(ele[:first_segpos][-5:])
    image_ori_url = 'https://zh.wikipedia.org/wiki/' + ele[:first_segpos].replace(' ', '_').strip('[[').strip(' ')
    flag = False
    # for format in tgt_format:
    #     if image_ori_url.endswith(format):
    #         flag = True
    #         break
    # if not flag:
    #     return {}
    # there
    # response=requests.get(image_ori_url)
    # soup=BeautifulSoup(response.text,'html.parser')
    # imglist=soup.find_all('img',class_='mw-thumbnail-link')
    # if len(imglist)==0:
    #     return {}
    # image_url='https:'+imglist[-1]['href']
    bigbracketpos = ele.find('{{')
    # TODO: use replace() to drop the params in the beginning of the caption
    if bigbracketpos != -1:
        caption = ele[first_segpos + 1:bigbracketpos]
    else:
        caption = ele[first_segpos + 1:]
    caption=caption.strip(' ').lstrip('thumb').strip(' ').lstrip('|').lstrip('right').strip(' ').lstrip('|').strip(' ').lstrip('left').strip(' ').lstrip(
            '|').strip(' ').lstrip('center').strip(' ').lstrip('|').lstrip('upright=0.9').strip(' ').lstrip('|').strip(' ').rstrip('(').strip(' ').lstrip(
            'thumb').strip(' ').lstrip('|').replace('thumb|','').replace('right|','').replace('left|','').replace('center|','').replace(
            'upright=0.9|','').replace('thumb |','').replace('right |','').replace('left |','').replace('center |','').replace(
            'upright=0.9 |','').replace('thumb |','').replace('right |','').replace('left |','').replace('center |','')
    trash_pos=caption.find('px|')
    if trash_pos!=-1:
        caption=caption[trash_pos+3:]
    # if mode == 'in-context':
    #     caption=ele[first_segpos+1:].strip('thumb|').strip('right').strip('|').strip('left').strip('|').strip('center').strip('upright=0.9').strip('|')
    # elif mode == 'gallery':
    #     caption=ele[first_segpos+1:].strip('thumb|').strip('right').strip('|').strip('center').strip('upright=0.9').strip('|')
    # filename_caption=''
    fi_pos = image_ori_url.find('wiki/File:')
    filename_caption = image_ori_url[fi_pos + 10:-4].replace('_', ' ') if image_ori_url[-4] == '.' else image_ori_url[
                                                                                        fi_pos + 10:-5].replace('_',
                                                                                                                ' ')
    filter_pos = caption.find('|')
    if filter_pos != -1 and filter_pos<8:
        caption = caption[filter_pos + 1:]
    caption = caption.replace("[", "").replace("]", "")
    # remove <ref> </ref>
    # TODO: remove <ref> </ref> in the caption with re library, because it is more memory efficient
    # remove <ref> </ref> in the caption with re library in string like: The original ''Fountain (Duchamp)|Fountain'' by Marcel Duchamp, 1917, photographed by Alfred Stieglitz at the 291 (art gallery)|291 after the 1917 Society of Independent Artists exhibit. Stieglitz used a backdrop of ''The Warriors'' by Marsden Hartley to photograph the urinal. The exhibition entry tag can be clearly seen.<ref name=\"Tomkins, p. 186\">Tomkins, ''Duchamp: A Biography'', p. 186.</ref>
    caption = re.sub(r'<ref.*?</ref>', '', caption)
    # refpos = caption.find('<ref>')
    # while refpos != -1:
    #     refendpos=caption.find('</ref>', refpos)
    #     caption = caption[:refpos]# + caption[refendpos + 6:]
    #     refpos = caption.find('<ref>')
    # TODO: remove <div> </div> like <div class=\"center\">The '''symmetric difference''' of ''A'' and ''B''</div>
    if caption.startswith('alt='):
        caption = caption[4:]
    return {'image_url': image_ori_url, 'caption': caption, 'filename_caption': filename_caption, 'image_info_url': image_ori_url}


with open(
        "F:/Download/enwiki-20230320-pages-articles-multistream1.xml-p1p41242/enwiki-20230320-pages-articles-multistream1.xml",
        'r', encoding='utf-8') as f:
    xml_file = f.read()

soup = BeautifulSoup(xml_file, 'xml')

texts = soup.find_all('text')
titles = soup.find_all('title')
res = []
for i in tqdm(range(len(texts))):
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
print(len(res))
# print(res)
print(all_format)