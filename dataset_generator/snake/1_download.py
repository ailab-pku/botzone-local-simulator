import os
import sh
import wget

game = "Snake"
download_template = "https://extra.botzone.org.cn/matchpacks/{game}-{year}-{month}.zip"

for year in (2015, 2016, 2017, 2018, 2019, 2020):
    for month in range(1, 12 + 1):
        # future
        if year == 2020 and month > 1:
            continue
        # earliest
        if year == 2015 and month < 6:
            continue

        filename = "{game}-{year}-{month}.zip".format(game=game, year=year, month=month)
        url = download_template.format(
            game=game,
            year=year,
            month=month
        )
        print("download url:", url)
        if os.path.exists("./{filename}".format(filename=filename)):
            print("{filename} already exists".format(filename=filename))
            continue
        wget.download(url)
        print("{filename} download finish".format(filename=filename))

for year in (2015, 2016, 2017, 2018, 2019, 2020):
    for month in range(1, 12 + 1):
        filename = "{game}-{year}-{month}".format(game=game, year=year, month=month)
        if not os.path.exists(filename + ".zip"):
            continue
        print("unzip", filename)
        sh.unzip(filename + ".zip", "-d", filename)
