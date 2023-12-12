from PIL import Image
from PIL import  ImageDraw
from PIL import  ImageFont
import datetime
import io
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
import os

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
    FONTS_DIR = "./fonts"
    curr_temp_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Bold.ttf"), 48)
    curr_temp_small_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Bold.ttf"), 32)
    date_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Regular.ttf"), 14)
    font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Regular.ttf"), 24)
    add_info_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Regular.ttf"), 16)
    daily_info_days_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Bold.ttf"), 24)
    daily_info_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Regular.ttf"), 24)
    daily_info_small_font = ImageFont.truetype(os.path.join(FONTS_DIR, "Arimo-Regular.ttf"), 14)

    # Getting weather from API
    ow = wlib.OpenWeather(API_KEY, 'metric', 'pl', LATITUDE, LONGITUDE)
    weather = ow.get_weather()

    # Creating main image
    main_image = Image.new('1', (SCREEN_WIDTH, SCREEN_HEIGHT), 255)  # 255: clear the frame
    draw = ImageDraw.Draw(main_image)


    ### CURRENT DATE ###
    draw.text((10, 7), datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S"), font=date_font)


    ### CURRENT WEATHER MAIN INFO ###

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


    ### ADDITIONAL CURRENT INFO ###

    ADD_INFO_Y_POS = 125
    ADD_INFO_Y_SPACE = 30
    ADD_INFO_X_POS = 35
    ADD_INFO_X_SPACE = 150

    # Precipitations values
    rain = weather.current.rain
    rain = rain.get('1h', 0) if rain is not None else 0
    snow = weather.current.snow
    snow = snow.get('1h', 0) if snow is not None else 0

    info_element = [
        [
            {'icon': "./images/precip.png", 'value': rain + snow, 'unit': " mm/h"},
            {'icon': "./images/cloud.png", 'value': weather.current.clouds, 'unit': " %"},
            {'icon': "./images/pressure.png", 'value': weather.current.pressure, 'unit': " hPa"},
        ],
        [
            {'icon': "./images/wind.png", 'value': weather.current.wind_speed, 'unit': " m/s"},
            {'icon': "./images/humidity.png", 'value': weather.current.humidity, 'unit': " %"},
        ]
    ]
    for col_no, column in enumerate(info_element):
        for row_no, element in enumerate(column):
            # Icon
            try:
                icon_image = Image.open(element['icon'])
                main_image.paste(icon_image, box=(ADD_INFO_X_POS + ADD_INFO_X_SPACE * col_no, ADD_INFO_Y_POS + ADD_INFO_Y_SPACE * row_no))
            except FileNotFoundError as exc:
                print(exc)

            # Value, unit
            val = round(element['value'], 1)
            draw.text((ADD_INFO_X_POS + 25 + ADD_INFO_X_SPACE * col_no, ADD_INFO_Y_POS + ADD_INFO_Y_SPACE * row_no), 
                      str(val) + element['unit'], font=add_info_font, fill=1)
            

    ### DAILY FORECAST ###

    WEEKDAY_NAMES = ["Pon", "Wt", "Śr", "Czw", "Pt", "Sob", "Nie"]
    Y_START_POS = 260
    Y_SPACE = 30

    # Icons
    icon_image = Image.open('./images/temp_day.png')
    icon_image = transparency_to_white(icon_image)  
    main_image.paste(icon_image, box=(80, 230))

    icon_image = Image.open('./images/temp_night.png')
    icon_image = transparency_to_white(icon_image)  
    main_image.paste(icon_image, box=(135, 230))

    icon_image = Image.open('./images/rain.png')
    icon_image = transparency_to_white(icon_image)  
    main_image.paste(icon_image, box=(250, 230))

    # Days
    for index, day_wthr in enumerate(weather.daily[:7]):

        # Day name
        weekday = 'Dziś' if index == 0 else WEEKDAY_NAMES[day_wthr.dt_dt.weekday()]
        draw.text((15, Y_START_POS + index * Y_SPACE), f'{weekday}', font=daily_info_days_font)

        # Day temperature
        temp_day = int(round(day_wthr.temp.get('day', '-'), 0))
        text_1 = str(temp_day)
        x_pos_1 = 95 - draw.textlength(text_1, daily_info_font) / 2
        draw.text((x_pos_1, Y_START_POS + index * Y_SPACE), text_1, font=daily_info_font)

        # Night temperature
        temp_night = int(round(day_wthr.temp.get('night', '-'), 0))
        text_2 = str(temp_night)
        x_pos_2 = 150 - draw.textlength(text_2, daily_info_font) / 2
        draw.text((x_pos_2, Y_START_POS + index * Y_SPACE), text_2, font=daily_info_font)

        # Icon
        icon_image = Image.open(day_wthr.weather.get_icon_image(save=True)).resize((35,) * 2)
        icon_image = transparency_to_white(icon_image)  # use when resized and white background (resizing changes transparency to black)
        main_image.paste(icon_image, box=(195, -5 + Y_START_POS + index * Y_SPACE))

        # Rain / snow
        rain = day_wthr.rain or 0
        snow = day_wthr.snow or 0
        precip = round(rain + snow, 1) or ''
        text_3 = str(precip)
        x_pos_3 = 265 - draw.textlength(text_3, daily_info_small_font) / 2
        draw.text((x_pos_3, 5 + Y_START_POS + index * Y_SPACE), text_3, font=daily_info_small_font)


    ### GRAPH - HOURLY FORECAST ###

    FORECAST_HOURS_COUNT = 16
    FIG_WIDTH_INCHES = 4.98
    FIG_HEIGHT_INCHES = 2.38
    fig_width = FIG_WIDTH_INCHES * 100  # pixels
    fig_height = FIG_HEIGHT_INCHES * 100  # pixels

    # Data from API
    dates = [hour_item.dt_dt for hour_item in weather.hourly][:FORECAST_HOURS_COUNT]
    temperatures = [hour_item.temp for hour_item in weather.hourly][:FORECAST_HOURS_COUNT]

    precips = []
    for hour_item in weather.hourly[:FORECAST_HOURS_COUNT]:
        rain = hour_item.rain.get("1h", 0) if hour_item.rain else 0
        snow = hour_item.snow.get("1h", 0) if hour_item.snow else 0
        precips.append(rain + snow)

    # Create figures
    fig, ax = plt.subplots(figsize=[FIG_WIDTH_INCHES, FIG_HEIGHT_INCHES])

    ax.grid(axis="y")  # removes vertical lines

    # Remove outlines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)

    # X axis
    ax.xaxis.set_major_locator(mdates.HourLocator(interval = 1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H'))

    # Creates plot
    temp_points, = ax.plot(dates[:FORECAST_HOURS_COUNT], temperatures, color="black", marker="o")

    # Y axis
    ax.set_ylabel(f'{chr(176)}C', rotation=0, loc="top")
    ax.yaxis.set_label_coords(-0.08, 0.98)
    
    # Move axis up in Z layer up - temperatures above precipitations
    ax.set_zorder(1)
    ax.patch.set_visible(False)

    # Setting y max/min label value always bigger/smaller than min/max temperature value
    y_ticks = ax.get_yticks()
    tick_diff = y_ticks[1] - y_ticks[0]
    if y_ticks[-1] < max(temperatures): y_ticks.append(y_ticks[-1] + tick_diff)
    if y_ticks[0] > min(temperatures): y_ticks.insert(0, y_ticks[-1] - tick_diff)
    ax.set_yticks(y_ticks)

    ax.set_ylim(bottom=y_ticks[0] - 0.1, top=y_ticks[-1] + 0.1)  # set y-axis limits always bigger/smaller than label value

    plt.rcParams['axes.autolimit_mode'] = 'round_numbers'


    # Precipitation Y-axis
    ax2 = ax.twinx()

    # Remove outlines
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['left'].set_visible(False)

    ax2.set_ylabel(f'mm/h', rotation=0, loc="top")
    ax2.yaxis.set_label_coords(1.11, 1.05)

    # Creates plot
    ax2.bar(dates, precips, width=0.017, color='lightgrey')

    # Setting y max/min label value always bigger/smaller than min/max precipitation value
    max_lim = max(precips) * 2 or 1
    ax2.set_ylim(bottom=0, top=max_lim)  # precipitation plot only on the half of the plot
    ticks = ax2.get_yticks()
    if max(precips) == 0:
        ticks = ticks[0:1]
    else:
        ticks = [tick for index, tick in enumerate(ticks) if not (index > 0 and ticks[index-1] > max(precips))]
    ax2.set_yticks(ticks)


    # Add sunrise / sunset icons
    ICON_SIZE = 30
    center_offs = ICON_SIZE / 2
    sunrise_icon = Image.open('./images/sunrise.png').resize((ICON_SIZE,) * 2)
    sunset_icon = Image.open('./images/sunset.png').resize((ICON_SIZE,) * 2)

    # Get the x and y data and transform it into pixel coordinates
    x, y = temp_points.get_data()
    x = [mdates.date2num(date) for date in x]  # x values as nums instead of datetime
    
    # Gets sunrise time
    sunrise_time = weather.current.sunrise_dt
    if sunrise_time < weather.hourly[0].dt_dt:
        sunrise_time = weather.daily[1].sunrise_dt

    # Gets sunset time
    sunset_time = weather.current.sunset_dt
    if sunset_time < weather.hourly[0].dt_dt:
        sunset_time = weather.daily[1].sunset_dt

    # Calculate pixel positions
    x_sunrise_pix_pos, y_sunrise_pix_pos = ax.transData.transform((mdates.date2num(sunrise_time), ax.get_yticks()[-1]))
    x_sunset_pix_pos, _ = ax.transData.transform((mdates.date2num(sunset_time), 0))
    y_pix_pos = y_sunrise_pix_pos - 5

    # Insert icons
    fig.figimage(sunrise_icon, xo=x_sunrise_pix_pos - center_offs, yo=y_pix_pos)
    fig.figimage(sunset_icon, xo=x_sunset_pix_pos - center_offs, yo=y_pix_pos)

    # Add sunrise time
    if dates[0] < sunrise_time < dates[-1]:
        sunrise_time_str = sunrise_time.strftime('%H:%M')
        if sunrise_time < dates[-3]:
            sunrise_time_pos = (x_sunrise_pix_pos + center_offs, y_pix_pos + 5)
        else:
            sunrise_time_pos = (x_sunrise_pix_pos - 60, y_pix_pos + 5)  # text on the left
        ax.text(*(ax.transData.inverted().transform(sunrise_time_pos)),  f'({sunrise_time_str})',
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax.transData,
            color='black', fontsize=9)

    # Add sunset time
    if dates[0] < sunset_time < dates[-1]:
        sunset_time_str = sunset_time.strftime('%H:%M')
        if sunset_time < dates[-3]:
            sunset_time_pos = (x_sunset_pix_pos + center_offs, y_pix_pos + 5)
        else:
            sunset_time_pos = (x_sunset_pix_pos - 60, y_pix_pos + 5)  # text on the left
        ax.text(*(ax.transData.inverted().transform(sunset_time_pos)),  f'({sunset_time_str})',
            verticalalignment='bottom', horizontalalignment='left',
            transform=ax.transData,
            color='black', fontsize=9)


    # Save to in-memory bufor
    img_buf = io.BytesIO()
    fig.savefig(img_buf, format='png', dpi=fig.dpi)

    plot_image = Image.open(img_buf)  # Open plot as image from memory
    main_image.paste(plot_image, box=(301, 1))  # plot paste to main_image


    # Image save and show
    main_image.save("result_image.bmp")
    main_image.show(title="WeatherStation")

if __name__ == "__main__":
    main()