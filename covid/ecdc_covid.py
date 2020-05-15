# -*- coding: utf-8 -*-
"""
Created on Sat Mar 21 18:01:01 2020

@author: Dennis
"""

import pandas as pd
import numpy as np
import numpy.polynomial.polynomial as poly
from matplotlib import style
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates
import requests
import io

requesttimeout = 10

def download_file(url,fileloc,to=requesttimeout,redirect=True):
	try:
		r = requests.get(url, allow_redirects=redirect, timeout=to)
		with open(fileloc, 'wb') as f:
			f.write(r.content)
		del r
		return 1
	except:
		return 0


#most striaght forward but verbose way of reading csv from a website
url = "https://covid.ourworldindata.org/data/ecdc/full_data.csv"
csv = requests.get(url,timeout=requesttimeout).content
data = pd.read_csv(io.StringIO(csv.decode('utf-8')))

#striaght using read_csv to download and read url
data2=pd.read_csv(url)


#another example using my own lib
filename = "full_data.csv"
download_file(url,filename)
#read it once it's downloaded but that might cause breaks
"""
csv_read_params={
	"filepath_or_buffer": "full_data.csv"
	}

data = pd.read_csv(**csv_read_params)
"""

############ Done Downloading ############

#convert date colun to datetime format
data['date']=pd.to_datetime(data['date'])

#data['date']=data['date'] + pd.Timedelta(days = 365*240) #test timestamp limitations

dictdata = {}

for location in data.location.unique():
	smalldf = data.loc[data['location'] == location]
	#print(smalldf)
	smalldf = smalldf.drop('location', 1)
	#print(smalldf.set_index('date').to_dict())
	smalldict = smalldf.set_index('date').to_dict()
	dictdata[location]= smalldict
	

#example of plotting directly from dataframe
dffig, dfaxfig = plt.subplots(1,figsize=(32, 20), dpi=300, facecolor='w', edgecolor='k', num=2)
data.loc[data['location'] == 'World'].plot(kind='line',x='date',y='total_cases',ax=dfaxfig) #use ax to locate axis to plot on
dffig.show()
#plt.close(fig=dffig) #close plot after user to reduce memory usage

#plt.figure(1, figsize=(32, 16), dpi=800, facecolor='w', edgecolor='k')

plt.figure(1, figsize=(32, 40), dpi=300, facecolor='w', edgecolor='k')
fig,(ax1,ax2) = plt.subplots(2,num=1) #using num=1 to locate exact figure object; create 2 subplots with axis ax1 and ax2

#simply creating a figure object as fig2, with an axis called axfig2
fig2, axfig2 = plt.subplots(1,figsize=(32, 20), dpi=300, facecolor='w', edgecolor='k')


biglocs = ['World','United States','United Kingdom','Italy']

for location in biglocs: 
	cases = sorted(dictdata[location]['total_cases'].items())
	x, y = zip(*cases)
	xdate = x
	
	x = mdates.date2num(x)
	
	##using subplot notation -- dirty
	#plt.subplot(211)
	#plt.yscale('linear')
	#plt.plot(x,y)
	#plt.subplot(212)
	#plt.yscale('log')
	#plt.plot(x,y)
	
	#plotting linear graph, label is used for legend
	
	coefs = poly.polyfit(x,y,3)
	ffit = poly.polyval(x,coefs)
	
	ax1.plot(x,y,label = location)
	ax1.plot(x,ffit,label = location + " Fitted")
	ax1.set_title('linear')
	
	#plotting semilog graph, label is used for legend
	ax2.semilogy(x,y,label = location)
	ax2.set_title('semilogy')
	
	#polyfit on a log scale
	#p = np.polyfit(x, np.log(y), 1) #using old lib note that outputs are BACKWARDS
	p = poly.polyfit(x, np.log(y), 1)#using new lib 
	
	axfig2.semilogy(x,y,label = location)
	#inorder to plot polyfit on a log scale, we need to de log it and then plot using semilogy 
	#axfig2.semilogy(x,np.exp(p[0]* x + p[1]), label = location + " Fitted") #using old lib
	axfig2.semilogy(x,np.exp(poly.polyval(x,p)), label = location + " Fitted")
	axfig2.set_title('figure2-semilogy-polyfit')


#set date format to be used to format x axis
plotdatefmt = mdates.DateFormatter('%Y-%m-%d')

stepsize = 1
for ax in fig.axes: #loop through axes and call show legend and vertical x labels
	ax.legend()
	start, end = ax.get_xlim()
	ax.xaxis.set_ticks(np.arange(start,end,stepsize))
	ax.tick_params(labelrotation=90)
	ax.xaxis.set_major_formatter(plotdatefmt)
	ax.grid(True, which = 'both', axis = 'y')

fig.show()
fig.savefig('plot2.svg')


#show legend
axfig2.legend()
#get x axis limits and set x ticks to show
start, end = axfig2.get_xlim()
stepsize = 1
axfig2.xaxis.set_ticks(np.arange(start,end,stepsize))
#rotate x labels 
axfig2.tick_params(labelrotation=90)
#set date format
plotdatefmt = mdates.DateFormatter('%Y-%m-%d')
axfig2.xaxis.set_major_formatter(plotdatefmt)
#add grid to y axis for semilog
axfig2.grid(True, which = 'both', axis = 'y')
#show figure
fig2.show()
#save figure
fig2.savefig('plotfig2.svg')

#plt.close(fig='all') #closes all figures

