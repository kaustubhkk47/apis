import settings
import ast
import Image
import os
BASE_DIR = settings.STATIC_ROOT
from catalog.models.product import Product
allImageSizes = [100.0, 200.0, 300.0, 400.0, 600.00, 700.0]
allSizePaths = []
for imageSize in allImageSizes:
    allSizePaths.append("{:.0f}x{:.0f}/".format(imageSize,imageSize))
def create_new_images(minPID,maxPID):
    
    for pid in range(minPID,maxPID+1):
        try:    
            product = Product.objects.get(id=pid)
            image_path = product.image_path
            image_name = product.image_name
            image_numbers = ast.literal_eval(product.image_numbers)

            for image_number in image_numbers:
                originalFilePath = "{}{}{}-{}.jpg".format(BASE_DIR,image_path,image_name,image_number)
                if os.path.exists(originalFilePath):
                    for i in range(0,len(allSizePaths)):
                        sizePath = allSizePaths[i]
                        directory = "{}{}{}".format(BASE_DIR,image_path,sizePath)
                        if not os.path.exists(directory):
                            os.makedirs(directory)
                        filePath = "{}{}{}{}-{}.jpg".format(BASE_DIR,image_path,sizePath,image_name,image_number)
                        if not os.path.exists(filePath):
                            img = Image.open(originalFilePath)
                            imgnew = resize_image(img, allImageSizes[i])
                            imgnew.save(filePath,format="JPEG",quality=100)
            if pid%100 == 0:
                print "{} done".format(pid)
        except Exception as e:
            pass

def resize_image(img, x):
    size = img.size
    width = size[0]
    height = size[1]
    if width > height and width > x:
        img = img.resize((int(x), int(x*float(height)/float(width))),Image.ANTIALIAS)
    if height >= width and height > x:
        img = img.resize((int(x*float(width)/float(height)), int(x)),Image.ANTIALIAS)
    return img
