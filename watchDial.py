import math
from PIL import Image, ImageDraw, ImageFont

import utils


class WatchDial:
    def __init__(self):
        """
        初始化表盘背景类
        """
        self.background = {}
        self.ticks = {}
        self.nums = {}

    def set_background_style(self, color: tuple):
        """
        设置纯色背景圆盘
        Args:
            color:颜色元组
        """
        self.background.clear()
        self.background['color'] = color

    def set_background_img(self, img_path, center: tuple, radius: float):
        """
        设置图像背景圆盘
        Args:
            img_path: 图像路径
            center: 圆心（左上角为原点，按比例截取）
            radius:半径比例
        """
        self.background.clear()

        assert radius <= 0.5, "半径超出范围(0~0.5)"
        assert center[0] < 1 and center[1] < 1, "圆心超出范围（0~1）"

        self.background['img'] = img_path
        self.background['center'] = center
        self.background['radius'] = radius

    def add_ticks_style(self, angles: list, length: float, width: float, color: tuple):
        """
        添加矢量的刻度
        Args:
            angles:触发角度列表 (0~360)
            length:长度比例
            width: 宽度比例
            color: 颜色
        """
        for angle in angles:
            assert 0 <= angle <= 360
            self.ticks[angle] = {
                'length': length,
                'width': width,
                'color': color
            }

    def add_num_style(self, angles: list, font: str, size: float, color: tuple, distance: float, value):
        """
        添加矢量的数字
        Args:
            angles:触发角度列表 (0~360)
            font:字体文件路径
            size:字体大小（比例）
            color: 颜色
            distance:距离圆盘边缘的比例
            value:整形值或函数（以角度为参数）
        """
        for angle in angles:
            assert 0 <= angle <= 360
            self.nums[angle] = {
                'font': font,
                'size': size,
                'color': color,
                'distance': distance,
                'value': value
            }

    def add_ticks_img(self, angles: list, scale: float, img_path: str):
        """
        添加刻度图像
        Args:
            angles: 触发角度列表 (0~360)
            scale: 缩放比例
            img_path: 图像路径
        """
        for angle in angles:
            assert 0 <= angle <= 360
            self.ticks[angle] = {
                'img': img_path,
                'scale': scale
            }

    def add_num_img(self, angles: list, scale: float, distance: float, img_path: str):
        """
        添加数字图像
        Args:
            angles: 触发角度列表 (0~360)
            scale: 缩放比例
            distance:距离表盘边缘的比例
            img_path: 图像路径
        """
        for angle in angles:
            assert 0 <= angle <= 360
            self.nums[angle] = {
                'img': img_path,
                'scale': scale,
                'distance': distance
            }

    def draw(self, size: int, output: str or None = 'watchDial.png') -> Image:
        """
        绘制表盘背景
        Args:
            size: 图像大小(size,size)
            output: 输出路径。若为None则只预览不保存
        Returns:
            PIL.Image
        """
        # 计算图像尺寸和圆心坐标
        radius = size / 2
        center = (radius, radius)

        # 绘制圆盘图层
        disk_layer = utils.transparent_img(size=(size, size))

        if 'color' in self.background.keys():
            # 绘制纯色背景圆盘
            draw = ImageDraw.Draw(disk_layer)

            color = self.background['color']
            draw.ellipse([(center[0] - radius, center[1] - radius), (center[0] + radius, center[1] + radius)],
                         fill=color)
        else:
            # 裁切圆形图像背景圆盘
            bk_img_path, bk_center, bk_radius = self.background['img'], self.background['center'], self.background[
                'radius']
            background_img = utils.crop_circle(image_path=bk_img_path, center_ratio=bk_center, radius_ratio=bk_radius)
            background_img = background_img.resize((size, size))
            disk_layer = utils.paste_foreground(background=disk_layer, foreground=background_img,
                                                position=(0.5, 0.5))

        # 绘制刻度和数字
        tick_layer = utils.transparent_img(size=(size, size))
        num_layer = utils.transparent_img(size=(size, size))

        tick_draw = ImageDraw.Draw(tick_layer)
        num_draw = ImageDraw.Draw(num_layer)

        for angle in range(-90, 270):
            rel_angle = angle + 90
            if rel_angle in self.ticks.keys():
                # 绘制刻度
                tick_params = self.ticks[rel_angle]
                if 'color' in tick_params:
                    # 绘制矢量刻度
                    length, width, color = tick_params['length'], tick_params['width'], tick_params['color']
                    start = (
                        center[0] + int(radius * (1 - length) * math.cos(math.radians(angle))),
                        center[1] + int(radius * (1 - length) * math.sin(math.radians(angle)))
                    )
                    end = (
                        center[0] + int(radius * math.cos(math.radians(angle))),
                        center[1] + int(radius * math.sin(math.radians(angle)))
                    )
                    tick_draw.line([start, end], fill=color, width=int(radius * width))
                else:
                    # 绘制图像刻度
                    tick_img_path, tick_scale = tick_params['img'], tick_params['scale']
                    # 打开刻度图像
                    tick_img = Image.open(tick_img_path)
                    # 缩放
                    scale_times = size * tick_scale / tick_img.size[1]
                    tick_img = tick_img.resize(
                        (int(tick_img.size[0] * scale_times), int(tick_img.size[1] * scale_times)))
                    # 绘制图
                    paste_pos = (
                        center[0] / size + 0.5 * math.cos(math.radians(angle)),
                        center[1] / size + 0.5 * math.sin(math.radians(angle))
                    )
                    tick_layer = utils.paste_rotated_image(background=tick_layer, foreground=tick_img,
                                                           position=paste_pos, angle=angle)
            if rel_angle in self.nums.keys():
                # 绘制数字
                num_params = self.nums[rel_angle]
                if 'color' in num_params:
                    # 绘制矢量数字
                    font_path, font_size, color, distance, value = num_params['font'], num_params['size'], num_params[
                        'color'], num_params['distance'], num_params['value']
                    # 计算值
                    if isinstance(value, (str, int, float)):
                        value = str(value)
                    else:
                        value = value(angle)
                    # 初始化字体
                    font_unit = ImageFont.truetype(font_path, 1)
                    # 计算相对大小并缩放
                    text_length = num_draw.textlength(text=value, font=font_unit)
                    abs_font_pixels = font_size * size
                    abs_font_size = int(abs_font_pixels / text_length)
                    font = ImageFont.truetype(font_path, abs_font_size)

                    text_box = num_draw.textbbox((0, 0,), text=value, font=font)
                    text_width = text_box[2] - text_box[0]
                    text_height = text_box[3] - text_box[1]

                    text_position = (
                        center[0] + int(radius * (1 - distance) * math.cos(math.radians(angle))) - text_width // 2,
                        center[1] + int(radius * (1 - distance) * math.sin(math.radians(angle))) - text_height // 1.5)
                    num_draw.text(text_position, value, font=font, fill=color)
                else:
                    # 绘制图像数字
                    num_img_path, num_scale, distance = num_params['img'], num_params['scale'], num_params['distance']
                    # 打开数字图像
                    num_img = Image.open(num_img_path)
                    # 缩放
                    num_img = num_img.resize((size * num_scale, size * num_scale))
                    # 绘制
                    paste_pos = (
                        int(center[0] / size + math.cos(math.radians(angle)) - distance),
                        int(center[1] / size + math.sin(math.radians(angle)) - distance)
                    )
                    num_layer = utils.paste_foreground(background=num_layer, foreground=num_img,
                                                       position=paste_pos)

        # 合并图层
        image = utils.paste_foreground(background=disk_layer, foreground=tick_layer, position=(0.5, 0.5))
        image = utils.paste_foreground(background=image, foreground=num_layer, position=(0.5, 0.5))

        # 保存或显示图像
        if output:
            image.save(output)
        else:
            image.show()


if __name__ == "__main__":
    wd = WatchDial()
    wd.set_background_style((0, 0, 0))
    # wd.set_background_img(img_path=r"C:\Users\loachex\Downloads\rs\bkg.png", center=(0.5, 0.5), radius=0.5)
    # wd.add_ticks_style(angles=[0, 90, 180, 270], length=0.03, width=0.01, color=(0, 255, 0))
    wd.add_ticks_img(angles=[0, 90, 180, 270], scale=0.02, img_path=r"C:\Users\loachex\Downloads\rs\tick.png")
    wd.add_num_style(angles=[0, 90, 180, 270], font=r"C:\Users\loachex\Downloads\rs\font.ttf", size=0.03,
                     color=(255, 255, 255),
                     distance=0.05, value=0)
    wd.draw(1000, None)
