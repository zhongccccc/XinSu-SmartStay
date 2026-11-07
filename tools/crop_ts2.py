from PIL import Image
im = Image.open(r'E:\zhikong\ts2.jpeg')
crop = im.crop((0, 60, 720, 170)).resize((1440, 220))
crop.save(r'E:\zhikong\ts2_header.png')
print(crop.size)
