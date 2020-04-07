import os
import sh
import wget

game = "Gomoku"
download_template = "https://extra.botzone.org.cn/matchpacks/{game}-{year}-{month}.zip"

for year in (2018, 2019, 2020):
    for month in range(1, 12 + 1):
        # future
        if year == 2020 and month > 1:
            continue
        # earliest
        if year == 2018 and month < 4:
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

for file in os.listdir("./"):
    if ".zip" not in file:
        continue
    print("unzip file:", file)
    sh.unzip(file, "-d", file.split(".")[0])

