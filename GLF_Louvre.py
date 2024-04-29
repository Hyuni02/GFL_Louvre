import io
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Frame, Button, Label, font
from PIL import Image, ImageTk

# 웹 페이지에서 데이터 가져오기
url = 'https://iopwiki.com/wiki/T-Doll_Index'
response = requests.get(url)
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, 'html.parser')
spans = soup.find_all('span', 'pad')
imgs = soup.find_all('img', 'doll-image')

# title 값을 저장할 리스트
titles = []
urls = []
links = []
fullimgs = []

# 전역 변수로 이미지 참조를 저장할 리스트 추가
global_images = []  # 캐릭터 썸네일
global_sprites = []  # 스킨 원본
global_sprites_thumb = []  # 스킨 썸네일

# class='pad'인 span 태그 하위에 있는 a 태그의 title을 리스트에 추가
for span in spans:
    a_tag = span.find('a')
    if a_tag and 'title' in a_tag.attrs:
        titles.append(a_tag['title'])
        links.append(a_tag['href'])
        # print(a_tag['title'])

for img in imgs:
    if img and 'src' in img.attrs:
        urls.append(img['src'])
        # print(img['src'])

# Tkinter 창 설정
window = Tk()
window.title("GFL_Louvre")
window.resizable(False, False)

# 현재 페이지 번호
current_page = 0

# 버튼을 표시할 프레임
frame = Frame(window)
frame.pack(expand=True, fill='both')

# 스킨을 표시할 프레임
frame2 = Frame(window)
frame2.pack(expand=True, fill='both')


# 메인화면
def display_main():
    update_buttons(current_page)
    window.geometry("768x240")


# 스킨 상세보기
def display_detail_list(_idx=0):
    loading_start()
    clear_display()
    window.geometry("1024x642")

    btn_main = Button(frame, text="back",
                      command=lambda: [print("Press btn : back"), display_main()])
    btn_main.grid(row=0, column=0, sticky='w', padx=10)

    global global_sprites_thumb
    for i in range(len(global_sprites_thumb)):
        if i % 2 == 1:
            continue
        button = Button(frame, image=global_sprites_thumb[i],
                        command=lambda _i=i: display_detail_list(_i))
        button.grid(row=1, column=int(i / 2), padx=10, pady=10)  # padx와 pady는 버튼 사이의 간격 조정
        # button.grid(row=1, column=i, padx=10, pady=10)  # padx와 pady는 버튼 사이의 간격 조정
    display_detail(_idx)
    loading_end()


# 선택한 스킨 표시
def display_detail(_idx):
    global global_sprites
    button = Button(frame2, image=global_sprites[_idx], command=lambda: print(fullimgs[_idx]))
    button.grid(row=0, column=0, padx=10, pady=10)
    button2 = Button(frame2, image=global_sprites[_idx + 1], command=lambda: print(fullimgs[_idx + 1]))
    button2.grid(row=0, column=1, padx=10, pady=10)


# 로딩 시작
def loading_start():
    # loading 메시지 표시
    global loading_label
    loading_label = Label(frame, text="loading....", font=font.Font(size=29))
    loading_label.place(relx=0.5, rely=0.5, anchor="center")  # 메시지를 중앙에 배치
    window.update_idletasks()


# 로딩 종료
def loading_end():
    global loading_label
    loading_label.destroy()


# 프레임 내의 모든 위젯 제거
def clear_display():
    for widget in frame.winfo_children():
        widget.destroy()


# 선택한 페이지 보기(메인화면)
def update_buttons(page=0):
    print(f"Update Page : {page}")
    global current_page
    global global_images  # 전역 이미지 리스트 사용 선언
    clear_display()

    current_page = page
    global_images.clear()  # 페이지가 업데이트될 때마다 이미지 리스트를 초기화

    loading_start()

    # 현재 페이지의 항목으로 버튼 생성, 페이지당 항목 수를 5개로 조정
    for i in range(page * 5, min((page + 1) * 5, len(titles))):
        _img = fetch_image("https:" + urls[i])[0]
        global_images.append(_img)  # 이미지 객체를 전역 리스트에 추가하여 참조 유지
        button = Button(frame, image=_img,
                        command=lambda _url=links[i]: get_detailpage(_url))
        # .grid()를 사용하여 버튼을 가로로 배치, column은 i % 5로 설정하여 한 줄에 최대 5개까지만 배치
        button.grid(row=0, column=i % 5, padx=10, pady=10)  # padx와 pady는 버튼 사이의 간격 조정

    loading_end()

    # 페이지 넘김 버튼 (이전 페이지)
    if page > 0:
        btn_prev = Button(frame, text="Previous",
                          command=lambda: [print("Button Click : Previous"), update_buttons(page - 1)])
        btn_prev.grid(row=1, column=0, sticky='w', padx=10)

    # 페이지 넘김 버튼 (다음 페이지)
    if (page + 1) * 5 < len(titles):
        btn_nxt = Button(frame, text="Next",
                         command=lambda: [print("Button Click : Next"), update_buttons(page + 1)])
        btn_nxt.grid(row=1, column=4, sticky='e', padx=10)


# url에서 이미지 다운로드
def fetch_image(_url):
    print("Fetch Image from " + _url)
    response_img = requests.get(_url)
    image = response_img.content
    pil_image = Image.open(io.BytesIO(image))
    pil_image_thumb = pil_image.resize((120, 120))
    pil_image_skin = pil_image.resize((360, 360))
    return ImageTk.PhotoImage(pil_image), ImageTk.PhotoImage(pil_image_thumb), ImageTk.PhotoImage(pil_image_skin)


# 선택한 캐릭터 스킨 불러오기 및 표시
def get_detailpage(_url):
    loading_start()
    print('https://iopwiki.com/' + _url)
    response_detail = requests.get('https://iopwiki.com/' + _url)
    response_detail.encoding = 'utf-8'
    soup_detail = BeautifulSoup(response_detail.text, 'html.parser')
    thumbs = soup_detail.find_all('a', 'image')
    global global_sprites
    global_sprites.clear()
    global global_sprites_thumb
    global_sprites_thumb.clear()
    global fullimgs
    fullimgs.clear()

    for thumb in thumbs:
        img_tag = thumb.find('img')
        if img_tag and 'src' in img_tag.attrs:
            thumb_url = 'https://iopwiki.com/' + img_tag['src']
            if _url[6:] not in thumb_url:
                # print('invalid url - not for this character')
                continue
            if '.jpg' in thumb_url:
                # print("invalid url - not character sprite")
                continue
            if '.jpeg' in thumb_url:
                # print("invalid url - not character sprite")
                continue
            if '_S.png' in thumb_url:
                # print("character concept sheet")
                continue
            if 'Censored' in thumb_url:
                # print("Censored sprite")
                continue
            # print(f"original URL : {thumb_url}")
            img_url = thumb_url.replace('/thumb', '')
            fullimg_url = img_url[:img_url.find('.png') + 4]
            fullimgs.append(fullimg_url)
            _img = fetch_image(fullimg_url)
            global_sprites.append(_img[2])
            global_sprites_thumb.append(_img[1])

    loading_end()
    display_detail_list()


# 최초의 버튼 업데이트
display_main()

window.mainloop()
