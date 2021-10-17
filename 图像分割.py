# 图像灰度的处理 图像的分割

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import cv2 as cv
import pyautogui as pg
import time
from PIL import Image
import matplotlib.cm as cm
import scipy.signal as signal     # 导入sicpy的signal模块


image = cv.imread('up.png')  # 读取当前图像


def cut_image(image, realx, realy, baoguangx, baoguangy):  # 自动将图像切割成为符合DMD分辨率的图像
    # realx,realy真实图像的大小
    # 首先需要获取当前图像的大小
    shape = image.shape
    shapey = shape[0]  # 现在是三通道的图像
    shapex = shape[1]  # 上面两个分别是图像的宽高

    # 需要保证768像素满足真正的曝光距离
    lengthy_perpixel = baoguangy / 768  # 确保每个像素的y长度
    lengthx_perpixel = baoguangx / 1024  # 确保每个像素的x长度

    # 得到这个之后就需要将图像转变为适合的大小
    pixely = int(realy / lengthy_perpixel)
    pixelx = int(realx / lengthx_perpixel)

    image = cv.resize(image, (pixelx, pixely))  # 将图像转变为合适的大小

    image = cv.cvtColor(image, cv.COLOR_BGR2GRAY)  # 转变为二值图像

    # 现在需要观察是否需要padding
    # 如果需要补充的话，先补充y在对x进行补充
    numbery = pixely // 768
    numberx = pixelx // 1024

    padding_imagey = int((numbery+1) * 768 - pixely)  # 这是需要补充的图像的y大小
    padding_imagex = int((numberx+1) * 1024 - pixelx)  # 这是需要补充的图像的x大小

    falsey = 0
    falsex = 0
    if padding_imagey >= 768:  # 不进行填充
        falsey = 1
    if padding_imagex >= 1024:  # 不进行填充
        falsex = 1

    if falsey == 0:
        padding_imagey = np.zeros((padding_imagey, image.shape[1]))

        image = np.vstack((image, padding_imagey))  # 进行拼接

    if falsex == 0 and False:
        padding_imagex = np.zeros((image.shape[0], padding_imagex))
        image = np.hstack(image, padding_imagex)

    # padding_image = np.zeros((153, 1024))
    # image = np.vstack((image, padding_image))

    # image1 = image[:768, :]
    # image2 = image[768:1536, :]
    # image3 = image[1536:, :]
    image1 = image[:768, :]
    image2 = image[768:1536, :]
    image3 = image[1536:, :]

    image1, bin_image1 = cv.threshold(
        image1, thresh=125, maxval=255, type=cv.THRESH_BINARY)  # 然后将图像做二值化处理
    image1, bin_image2 = cv.threshold(
        image2, thresh=125, maxval=255, type=cv.THRESH_BINARY)  # 然后将图像做二值化处理
    image1, bin_image3 = cv.threshold(
        image3, thresh=125, maxval=255, type=cv.THRESH_BINARY)  # 然后将图像做二值化处理
    # 根据DMD微镜的准确分辨率将其进行分割，那么现在我们按照DMD镜的分辨率以及误差的大小进行分割，如果不足那么进行补零
    return (bin_image1, bin_image2, bin_image3)


image = cut_image(image, 1, 30.810, 1, 11)
image1 = image[0]
image2 = image[1]
image3 = image[2]
cv.imwrite('image1.jpg', image1)
cv.imwrite('image2.jpg', image2)
cv.imwrite('image3.jpg', image3)


def imconv(image_array, suanzi):

    image = image_array.copy()  # 原图像矩阵的深拷贝

    dim1, dim2 = image.shape

    # 对每个元素与算子进行乘积再求和(忽略最外圈边框像素)
    for i in range(1, dim1 - 1):
        for j in range(1, dim2 - 1):
            image[i, j] = (image_array[(i - 1):(i + 2),
                           (j - 1):(j + 2)] * suanzi).sum()

    # 由于卷积后灰度值不一定在0-255之间，统一化成0-255
    image = image * (255.0 / image.max())

    # 返回结果矩阵
    return image


# x方向的Prewitt算子
suanzi_x = np.array([[-1, 0, 1],
                    [-1, 0, 1],
                    [-1, 0, 1]])

# y方向的Prewitt算子
suanzi_y = np.array([[-1, -1, -1],
                     [0, 0, 0],
                     [1, 1, 1]])

# 打开图像并转化成灰度图像
image = Image.open("pika.jpg").convert("L")

# 转化成图像矩阵
image_array = np.array(image)

# 得到x方向矩阵
image_x = imconv(image_array, suanzi_x)

# 得到y方向矩阵
image_y = imconv(image_array, suanzi_y)

# 得到梯度矩阵
image_xy = np.sqrt(image_x**2+image_y**2)
# 梯度矩阵统一到0-255
image_xy = (255.0/image_xy.max())*image_xy

# 绘出图像
plt.subplot(2, 2, 1)
plt.imshow(image_array, cmap=cm.gray)
plt.axis("off")
plt.subplot(2, 2, 2)
plt.imshow(image_x, cmap=cm.gray)
plt.axis("off")
plt.subplot(2, 2, 3)
plt.imshow(image_y, cmap=cm.gray)
plt.axis("off")
plt.subplot(2, 2, 4)
plt.imshow(image_xy, cmap=cm.gray)
plt.axis("off")
plt.show()


# Laplace算子
suanzi1 = np.array([[0, 1, 0],
                    [1, -4, 1],
                    [0, 1, 0]])

# Laplace扩展算子
suanzi2 = np.array([[1, 1, 1],
                    [1, -8, 1],
                    [1, 1, 1]])

# 打开图像并转化成灰度图像
image = Image.open("pika.jpg").convert("L")
image_array = np.array(image)

# 利用signal的convolve计算卷积
image_suanzi1 = signal.convolve2d(image_array, suanzi1, mode="same")
image_suanzi2 = signal.convolve2d(image_array, suanzi2, mode="same")

# 将卷积结果转化成0~255
image_suanzi1 = (image_suanzi1/float(image_suanzi1.max()))*255
image_suanzi2 = (image_suanzi2/float(image_suanzi2.max()))*255

# 为了使看清边缘检测结果，将大于灰度平均值的灰度变成255(白色)
image_suanzi1[image_suanzi1 > image_suanzi1.mean()] = 255
image_suanzi2[image_suanzi2 > image_suanzi2.mean()] = 255

# 显示图像
plt.subplot(2, 1, 1)
plt.imshow(image_array, cmap=cm.gray)
plt.axis("off")
plt.subplot(2, 2, 3)
plt.imshow(image_suanzi1, cmap=cm.gray)
plt.axis("off")
plt.subplot(2, 2, 4)
plt.imshow(image_suanzi2, cmap=cm.gray)
plt.axis("off")
plt.show()


src = Image.open('d:/ex.jpg')
r, g, b = src.split()

plt.figure("lena")
ar = np.array(r).flatten()
plt.hist(ar, bins=256, normed=1, facecolor='r', edgecolor='r', hold=1)
ag = np.array(g).flatten()
plt.hist(ag, bins=256, normed=1, facecolor='g', edgecolor='g', hold=1)
ab = np.array(b).flatten()
plt.hist(ab, bins=256, normed=1, facecolor='b', edgecolor='b')
plt.show()
