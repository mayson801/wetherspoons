import extract_msg
import glob
import re
import csv
import time
import json


def get_total_price(split):
    order_check=(len(split)-6)
    paypal=False
    products=[]

    if "Order Total" in split[order_check]:
        price = split[(len(split) - 6)]
    else:
        #this is cos paypal recipts are diffrent
        price=split[(len(split) - 7)]
        paypal=True

    num = 8
    if paypal == True: num = 9
    while not (split[(len(split) - num)]=="Qty     Description     Amount" or split[(len(split) - num)]=="Qty Description Amount "):
        if "VAT ("not in split[(len(split) - num)]:
            if "      " != split[(len(split) - num)]:
                if "£0.00" not in split[(len(split) - num)]:
                    order_iteam=re.sub(' +', ' ',split[(len(split) - num)])
                    split_order_iteam=order_iteam.split(" ")
                    split_order_iteam = list(filter(None, split_order_iteam))

                    ammount=split_order_iteam[0]
                    iteam_price=split_order_iteam[(len(split_order_iteam)-1)]
                    i = 1
                    item=""
                    while i < len(split_order_iteam):
                        if i!= (len(split_order_iteam)-1):
                            item=item+split_order_iteam[i]
                        i += 1
                    items_formated=[ammount,item,iteam_price]
                    products.append(items_formated)
        num=num+1

    price=re.findall("\d+\.\d+", price)
    return price,products
def get_location(split):
    if len(split[3])<1:
        spoons_name=split[4]
        address= split[5]+ " "+ split[7]
        postcode=split[8]
    else:
        spoons_name=split[3]
        address= split[4]+ " "+ split[6]
        postcode =split[7]
    return [spoons_name,address,postcode]
def full_data(locaion, price, address_check, total_array):
    if locaion in address_check:
        array_number=(address_check.index(locaion))
        location_price=str(price[0][0])
        total_array[array_number][3]=(float(total_array[array_number][3]))+float(location_price)
        total_array[array_number][4].append(price[1])

    else:
        address_check.append(locaion)
        total_array.append(locaion+price[0]+[[price[1]]])
def write_to_csv(array,file_name):
    with open(file_name+'.csv', 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        for data in array:
            writer.writerow(data)
def format_name_changes(array):
    for i in array:
        i[3] = round(float(i[3]), 2)
    with open('name_change.txt') as f:
        data = f.read()
        name_check = json.loads(data)
    #this is dumb and i know it'll confuse me later
    for i in array:
        for x in i[4]:
            for name_check_number in name_check:
                if x[0][1] in name_check_number["alt_text"]:
                    x[0][1] = name_check_number["name"]
    return array
def read_iteams(array):
    orders_count = 0
    csv_formatted = []

    for i in array:
        for x in i[4]:
            for y in x:
                csv_formatted.append([i[0],i[1],i[2],y[0],y[1],y[2]])

                orders_count=orders_count+1
    return csv_formatted

def group_location(array):
    location_group=[]
    for x in array:
        location=[x[0],x[1],x[2],x[3]]
        location_group.append(location)
    location_group=sorted(location_group, key=lambda x: int(x[3]),reverse=True)
    return location_group
def group_iteams(array):
    group_check=[]
    group_total=[]
    for i in array:
        if i[4] in group_check:
            array_number = (group_check.index(i[4]))
            price=i[5].replace("£", "")
            group_total[array_number][1]=round(float(price)+(float(group_total[array_number][1])),2)
        else:
            price=i[5].replace("£", "")
            group_check.append(i[4])
            group_total.append([i[4],price])
    group_total=sorted(group_total, key=lambda x: float(x[1]),reverse=True)

    return group_total
def read_from_file():
    address_check = []
    total_array = []
    for file in glob.glob("emails\*.msg"):

        msg = extract_msg.Message(file)
        msg_date = msg.date
        msg_message = msg.body

        body = ('Body: {}'.format(msg_message))
        split=body.splitlines()
        locaion=get_location(split)

        i=0
        while i < len(split):
            split[i]=split[i].replace('\t',"")
            i += 1
        res = list(filter(None, split))
        price=get_total_price(res)
        add_to_array=full_data(locaion, price, address_check, total_array)
    total_array=format_name_changes(total_array)
    return total_array

#read from file
total_array=read_from_file()

#group by iteams
iteams_grouped=group_iteams(read_iteams(total_array))
print(iteams_grouped)
#group by location
location_group=group_location(total_array)
print(location_group)

sorted(location_group, key = lambda x: int(x[3]))

#write_to_csv(group_iteams(read_iteams(total_array)),"group iteams")
#write_to_csv(total_array,"total")
#write_to_csv(read_iteams(total_array),"eachorder")