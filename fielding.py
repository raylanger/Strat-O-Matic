import json

#Load json of fielding chart
with open("Adv_FieldingChart.json", mode = "r", encoding = "utf-8") as read_file:
    fieldingchart = json.load(read_file)

#Convert keys of fielding chart to int if possible
fieldingchart = {int(pos): {int(rating) if rating != "E" else rating: res if rating != "E" else {int(num): errors for num, errors in res.items()} for rating, res in chart.items()} for pos, chart in fieldingchart.items()}