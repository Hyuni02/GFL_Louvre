import io
import requests
from bs4 import BeautifulSoup
from tkinter import Tk, Frame, Button, Label, font
from PIL import Image, ImageTk
import webbrowser

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
# 전역 변수로 이미지 참조를 저장할 리스트 추가
global_images = []

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
window.title("Title Buttons")
window.geometry("768x240")
window.resizable(False, False)

# 현재 페이지 번호
current_page = 0

# 버튼을 표시할 프레임
frame = Frame(window)
frame.pack(expand=True, fill='both')


def update_buttons(page=0):
    print(f"Update Page : {page}")
    global current_page
    global global_images  # 전역 이미지 리스트 사용 선언

    current_page = page
    global_images.clear()  # 페이지가 업데이트될 때마다 이미지 리스트를 초기화

    # 프레임 내의 모든 위젯 제거
    for widget in frame.winfo_children():
        widget.destroy()

    # loading 메시지 표시
    loading_label = Label(frame, text="loading....", font=font.Font(size=29))
    loading_label.place(relx=0.5, rely=0.5, anchor="center")  # 메시지를 중앙에 배치

    window.update_idletasks()

    # 현재 페이지의 항목으로 버튼 생성, 페이지당 항목 수를 5개로 조정
    for i in range(page * 5, min((page + 1) * 5, len(titles))):
        _img = fetch_image(urls[i])
        global_images.append(_img)  # 이미지 객체를 전역 리스트에 추가하여 참조 유지
        button = Button(frame, image=_img, command=lambda _url=links[i]: open_url(_url))
        # .grid()를 사용하여 버튼을 가로로 배치, column은 i % 5로 설정하여 한 줄에 최대 5개까지만 배치
        button.grid(row=0, column=i % 5, padx=10, pady=10)  # padx와 pady는 버튼 사이의 간격 조정

    loading_label.destroy()

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
    response_img = requests.get("https:" + _url)
    print("Fetch Image from https:"+url)
    image = response_img.content
    pil_image = Image.open(io.BytesIO(image))
    return ImageTk.PhotoImage(pil_image)


def open_url(_url):
    print("Opening URL : " + _url)
    webbrowser.open('iopwiki.com/' + _url)


# 최초의 버튼 업데이트
update_buttons()

window.mainloop()
