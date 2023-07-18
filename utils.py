from PIL import Image, ImageDraw


def transparent_img(size: tuple[int, int]) -> Image:
    """
    生成透明图
    Args:
        size:图像尺寸
    Returns:
        透明背景图-Image
    """
    return Image.new("RGBA", size, (0, 0, 0, 0))


def paste_foreground(
        background: Image,
        foreground: Image,
        position: tuple[float, float]) -> Image:
    """
    将前景图粘贴到背景图上
    Args:
        background: 前景图
        foreground: 背景图
        position: 粘贴位置（比例）
    Returns:
        backgroun-Image
    """
    # 计算前景图像在背景图像上的位置
    background_width, background_height = background.size
    foreground_width, foreground_height = foreground.size
    position = (
        int((background_width - foreground_width) * position[0]),
        int((background_height - foreground_height) * position[1])
    )

    # 粘贴前景图像到背景图像
    background.paste(foreground, position, mask=foreground)

    # 显示或保存结果
    return background


def crop_circle(image_path: str, center_ratio: tuple[float, float], radius_ratio: float) -> Image:
    """
    裁切图像，获取圆形部分
    Args:
        image_path: 图像路径
        center_ratio: 圆心（比例0~1）
        radius_ratio: 半径（比例0~1）
    Returns:
        圆形区域-Image
    """
    # 打开图像
    image = Image.open(image_path)

    # 计算圆心坐标
    center = (int(image.width * center_ratio[0]), int(image.height * center_ratio[1]))

    # 计算圆的半径
    radius = int(min(image.width, image.height) * radius_ratio)

    # 创建透明图像
    cropped_image = Image.new('RGBA', image.size, (0, 0, 0, 0))

    # 创建画笔
    draw = ImageDraw.Draw(cropped_image)

    # 绘制圆形区域
    draw.ellipse((center[0] - radius, center[1] - radius, center[0] + radius, center[1] + radius),
                 fill=(255, 255, 255, 255))

    # 裁切图像
    cropped_image.paste(image, (0, 0), mask=cropped_image)
    left = center[0] - radius
    upper = center[1] - radius
    right = center[0] + radius
    lower = center[1] + radius
    cropped_image = cropped_image.crop((left, upper, right, lower))

    return cropped_image


def paste_rotated_image(
        background: Image,
        foreground: Image,
        angle: float,
        position: tuple) -> Image:
    """
    将前景图旋转一定角度，并粘贴在背景图上
    Args:
        background: 背景图
        foreground: 前景图
        angle: 旋转角度
        position: 粘贴位置（比例）（参考点为前景图的左高中点）
    Returns:
        background-Image
    """
    # 为前景图像创建透明度通道
    foreground_with_alpha = foreground.convert("RGBA")

    # 旋转前景图像
    rotated_foreground = foreground_with_alpha.rotate(angle, expand=True)

    # 将比例形式的粘贴位置转换为具体的坐标
    paste_position = (
        int(position[0] * background.size[0]) - rotated_foreground.width // 2,
        int(position[1] * background.size[1]) - rotated_foreground.height // 2
    )

    # 将旋转后的前景图像粘贴到背景图像上
    background.paste(rotated_foreground, paste_position, rotated_foreground)

    return background
