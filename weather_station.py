from PIL import Image
from PIL import  ImageDraw
from PIL import  ImageFont
import datetime

import weather as wlib


def transparency_to_white(image):
    if image.mode == 'RGBA':
        alpha = image.split()[3]
        bgmask = alpha.point(lambda x: 255-x)
        image = image.convert('RGB')
        image.paste((255,255,255), None, bgmask)
        return image


def main():
    # Main screen parameters
    SCREEN_HEIGHT = 480
    SCREEN_WIDTH = 800

    # Data for API
    API_KEY = '87f6be3be5756aab9f29044694dfbdad'
    LATITUDE = 50.0142814
    LONGITUDE = 19.8799902

    # Fonts definitions
    curr_temp_font = ImageFont.truetype("arialbd.ttf", 48)
    curr_temp_small_font = ImageFont.truetype("arialbd.ttf", 32)
    date_font = ImageFont.truetype("arial.ttf", 14)
    font = ImageFont.truetype("arial.ttf", 24)

    # Getting weather from API
    ow = wlib.OpenWeather(API_KEY, 'metric', 'pl', LATITUDE, LONGITUDE)
    weather = ow.get_weather()

    # Creating main image
    main_image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(main_image)

    # Date
    draw.text((10, 7), datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), font=date_font)

    # Background - black
    draw.rounded_rectangle((15, 27, 270+15, 190+27), radius=15, fill=0)
    draw.rounded_rectangle((279-98, 33, 279, 78+33), radius=9, fill=1) # white icon window

    # Current temperature
    current_temp_val = round(weather.current.temp,1)
    current_temp_fract = abs(int((current_temp_val - int(current_temp_val)) * 10))
    feel_temp_val = round(weather.current.feels_like,1)
    curr_temp_text = f'{int(current_temp_val)}'
    if current_temp_val < 0 and curr_temp_text[0] != "-": curr_temp_text = "-" + curr_temp_text
    curr_temp_fract_text = f'.{current_temp_fract}{chr(186)}C'
    curr_temp_width = draw.textlength(curr_temp_text, curr_temp_font)

    draw.text((30, 33), curr_temp_text, font=curr_temp_font, fill=1)
    draw.text((30 + curr_temp_width, 48), curr_temp_fract_text, font=curr_temp_small_font, fill=1)
    draw.text((50, 83), f'{feel_temp_val}{chr(186)}C', font=font, fill=1)

    # Add icon 
    icon_image = Image.open(weather.current.weather.get_icon_image(save=True)).resize((80,) * 2)
    icon_image = transparency_to_white(icon_image)  # use when resized and white background (resizing changes transparency to black)
    main_image.paste(icon_image, box=(190, 33))


    # Image save and show
    main_image.save("result_image.bmp")
    main_image.show(title="WeatherStation")

if __name__ == "__main__":
    main()