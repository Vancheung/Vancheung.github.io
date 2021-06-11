""" 快速切图 """
from PIL import Image  # 批量对一批图片更改大小

path = '/Users/admin/Documents/zxf/vancheung.github.io/assets/img/favicons/'  # 图片所在目录
img_list = ['favicon.ico']  # 图片名称列表
size_list = {
    'android-chrome-512x512.png': (512, 512),
    'android-chrome-192x192.png': (192, 192),
    'apple-touch-icon.png': (180, 180),
    'mstile-150x150.png': (150, 150),
    'favicon-32x32.png': (32, 32),
    'favicon-16x16.png': (16, 16)
}

for imgs in img_list:
    img = Image.open(path + imgs)  # 读取图片
    for name in size_list:
        pic = img.resize(size_list[name])  # 重置大小 （长，宽）
        pic.save(path + name)  # 保存（默认路径为原图片位置+原图片名[也就是相当于覆盖]）
