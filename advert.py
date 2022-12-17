ad = list()

    wookbook = openpyxl.load_workbook("base.xlsx")

    worksheet = wookbook.active

    for i in range(0, worksheet.max_row):
        for col in worksheet.iter_cols(1, worksheet.max_column):
            ad.append(str(col[i].value))

    ad.remove('None')
    ad.remove('None')
    ad.remove('None')

    for n in ad:
        await bot.send_message(message.from_user.id, n)
