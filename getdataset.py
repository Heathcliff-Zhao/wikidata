from bs4 import BeautifulSoup

with open("F:/Download/enwiki-20230320-pages-articles-multistream1.xml-p1p41242/enwiki-20230320-pages-articles-multistream1.xml", 'r', encoding='utf-8') as f:
    xml_file = f.read()

soup = BeautifulSoup(xml_file, 'xml')

texts = soup.find_all('text')
textwithgallery = []

for i in range(len(texts)):
    pos=texts[i].text.find("== Gallery ==")
    if pos!=-1:
        textwithgallery.append(i)

tgt_incontext_list = []
tgt_gallery_list = []
# for i in range(len(textwithgallery)):
for i in range(1,2):
    lp = texts[textwithgallery[i]].text.find("<gallery>")
    rp = texts[textwithgallery[i]].text.find("</gallery>")
    # print(lp,rp)
    gallery_ori_str=texts[textwithgallery[i]].text[lp:rp]
    gallery_ori_str=gallery_ori_str.strip('<gallery>')
    gallery_ori_str=gallery_ori_str.strip('</gallery>')
    # tgt_gallery_list.append(gallery_ori_str.split("\n\n"))
    tgt_gallery_list.append([ele for ele in gallery_ori_str.split("\n") if ele != ''])
# for i in range(3):
    incontextimg = []
    startpos = 0
    endpos=texts[textwithgallery[i]].text.find('Gallery')

    while(startpos<endpos):
        pos = texts[textwithgallery[i]].text.find('[[File:',startpos,endpos)
        if pos!=-1:
            incontextimg.append(pos)
            startpos = pos+1
        else:
            break
    imagewithcaption = []
    for pos in incontextimg:
        amark=False
        bmark=False
        stack=[]
        for left in range(pos,endpos):
            if texts[textwithgallery[i]].text[left] == '[' and not amark:
                amark=True
            elif texts[textwithgallery[i]].text[left] == '[' and amark:
                amark=False
                stack.append('[[')
            elif texts[textwithgallery[i]].text[left] == ']' and not bmark:
                bmark=True
            elif texts[textwithgallery[i]].text[left] == ']' and bmark:
                bmark=False
                stack.pop()
            if len(stack)==0 and left-pos>3:
                imagewithcaption.append(texts[textwithgallery[i]].text[pos:left+1])
                break
    tgt_incontext_list.append(imagewithcaption)
print(tgt_incontext_list)
print(tgt_gallery_list)