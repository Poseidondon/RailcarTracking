import csv
# TODO: add sources manager

urls = [['https://www.youtube.com/watch?v=okpIxrWSACo'],
        ['https://www.youtube.com/watch?v=Q9_jZVECcjY'],
        ['https://www.youtube.com/watch?v=cJzYyUpf2mg'],
        ['https://www.youtube.com/watch?v=2VLzhHPl6wU'],
        ['https://www.youtube.com/watch?v=_JC19RunEmg'],
        ['https://www.youtube.com/watch?v=7FVYjsoUFmQ'],
        ['https://www.youtube.com/watch?v=EsH_uVnwqh0'],
        ['https://www.youtube.com/watch?v=Gm0r1JqpDT8'],
        ['https://www.youtube.com/watch?v=1jiIRpVJRzk'],
        ['https://www.youtube.com/watch?v=0N2huDO2x10']]

# writing to csv file
with open('webcams.csv', 'w', newline="") as csvfile:
    # creating a csv writer object
    csvwriter = csv.writer(csvfile)

    # writing the fields
    csvwriter.writerow(['url'])

    # writing the data rows
    csvwriter.writerows(urls)
