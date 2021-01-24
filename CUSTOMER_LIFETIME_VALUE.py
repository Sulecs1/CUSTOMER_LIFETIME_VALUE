#################################################################
#                   CLTV APPLICATION                            #
#################################################################
#<<<Şule AKÇAY>>>#

#CLTV = (Customer_Value / Churn_Rate) x Profit_margin
# Customer_Value = Average_Order_Value * Purchase_Frequency
# Average_Order_Value = Total_Revenue / Total_Number_of_Orders
# Purchase_Frequency =  Total_Number_of_Orders / Total_Number_of_Customers
# Churn_Rate = 1 - Repeat_Rate
# Profit_margin

#Gerekli olan eklentiler

import pandas as pd
pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', 20)
pd.set_option('display.float_format', lambda x: '%.5f' % x)
from sklearn.preprocessing import MinMaxScaler

data = pd.read_excel(r"C:\Users\Suleakcay\PycharmProjects\pythonProject3\HAFTA3\online_retail_II.xlsx",
                    sheet_name="Year 2010-2011")

df = data.copy()
df.head()
df.info()
df.columns

df = df[~df["Invoice"].str.contains("C", na=False)]
df = df[(df['Quantity'] > 0)] #Eksik değerlerden kurtulmak için
df.dropna(inplace=True)#kaldırdım
#Toplam ürün fiyatı = ürün adedi * ürün fiyatı
df["CompletePrice"] = df["Quantity"] * df["Price"]

cltv_data = df.groupby('Customer ID').agg({'Invoice': lambda x: len(x),
                                         'Quantity': lambda x: x.sum(),
                                         'CompletePrice': lambda x: x.sum()})

#complete_transaction-> işlem sayısı
#complete_unit->ürün adedi
#complete_price->Toplam satın alınan ürün fiyatı
cltv_data.columns = ['complete_transaction', 'complete_unit', 'complete_price']
cltv_data.head()

# 1.Calculate Average Order Value
cltv_data.shape[0] #total number of customers

#Revenue left per order
cltv_data['averageOrderValue'] =cltv_data['complete_price'] /cltv_data['complete_transaction']

# 2.Calculate Purchase Frequency
# Purchase_Frequency =  Total_Number_of_Orders / Total_Number_of_Customers
cltv_data['purchaseFrequency'] = cltv_data['complete_transaction'] /cltv_data.shape[0]

# 3.Calculate Repeat Rate and Churn Rate
#number of customers making multiple shoppers / number of customers
repeat_rate = cltv_data[cltv_data.complete_transaction > 1].shape[0] / cltv_data.shape[0]
churn_rate = 1 - repeat_rate

#4.Calculate Profit Margin
cltv_data['prf_margin'] = cltv_data['complete_price']*0.08 # think  made eight percent profit

#5.Calculate Customer Lifetime Value

#Customer_Value = Average_Order_Value * Purchase_Frequency
cltv_data['customerValue'] = (cltv_data['averageOrderValue'] * cltv_data["purchaseFrequency"]) / churn_rate

# CLTV = (Customer_Value / Churn_Rate) x Profit_margin
cltv_data['CLTV'] = cltv_data['customerValue'] * cltv_data['prf_margin']

cltv_data.sort_values("CLTV", ascending=False)

scaler = MinMaxScaler(feature_range=(1, 100))
scaler.fit(cltv_data[["CLTV"]])
cltv_data["SCALED_CLTV"] = scaler.transform(cltv_data[["CLTV"]])

cltv_data.sort_values("CLTV", ascending=False) #azalan değerlere göre

cltv_data[["complete_transaction", "complete_unit", "complete_price", "CLTV", "SCALED_CLTV"]].sort_values(by="SCALED_CLTV",
                                                                                               ascending=False).head()
cltv_data.sort_values("complete_price", ascending=False)
# grouped 4 segments
cltv_data["segment"] = pd.qcut(cltv_data["SCALED_CLTV"], 4, labels=["D", "C", "B", "A"])#küçükten büyüğe sırala


"cltv_data"[["segment", "complete_transaction", "complete_unit", "complete_price", "CLTV", "SCALED_CLTV"]].sort_values(
    by="SCALED_CLTV",
    ascending=False).head()

#betimsel istatistik incele
cltv_data.groupby("segment")[["complete_transaction", "complete_unit", "complete_price", "CLTV", "SCALED_CLTV"]].agg(
    {"count", "mean", "sum"})
