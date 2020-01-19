import sys
import os
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.colors import n_colors

def createGraph(keyword,totalHistory,newHistory,checkNum):

    x = np.arange(1,checkNum[0][0]+1) 
    width = 0.35  

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, totalHistory, width, label='Total', color=(0.2, 0.5, 0.6, 1))
    rects2 = ax.bar(x + width/2, newHistory, width, label='New', color=(0.1, 0.9, 0.3, 1))

    ax.set_ylabel('Users')
    ax.set_xlabel('Checks')
    ax.set_title('keyword')
    ax.set_xticks(x)
    ax.set_yticks(np.arange(totalHistory[-1] +2))
    ax.legend()


    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                       xy=(rect.get_x() + rect.get_width() / 2, height),
                       xytext=(0, 3),  # 3 points vertical offset
                       textcoords="offset points",
                       ha='center', va='bottom')


    autolabel(rects1)
    autolabel(rects2)
    
    fig.tight_layout()

  

    filePath = "/home/code/Desktop/twitterscraper/images/graphs/{key}.png".format(key=(keyword + '_graph'))

    if (os.path.isfile(filePath)):
        os.remove(filePath)

    plt.savefig((filePath), bbox_inches='tight')

    print(keyword+' graph created')
    

def createTable(keyword,username,bio,location,followers,following,isNew):
    new=[]

    for i in isNew:
        if i[0]:
            new.append(1)
        else:
            new.append(0)

    colors = n_colors('rgb(255, 255, 255)', 'rgb(80, 220, 100)', 2, colortype='rgb')
    
    fig = go.Figure(data=[go.Table(
    columnorder = [1,2,3,4,5,6],
    columnwidth = [20,30,20,20,20,20],
      header=dict(
        values=['<b>username</b>','<b>bio</b>','<b>location</b>','<b>followers</b>','<b>following</b>','<b>is new</b>'],
        line_color='black', fill_color='white',
        align='center',font=dict(color='black', size=12)
      ),
      cells=dict(
        values=[username,bio,location,followers,following,isNew],
        line_color=['black'],
        fill_color=[np.array(colors)[new]],
        align='center', font=dict(color='black', size=11)
        ))
    ])
        

    filePath = "/home/code/Desktop/twitterscraper/images/tables/{key}.png".format(key=(keyword + '_table'))

    if (os.path.isfile(filePath)):
        os.remove(filePath)
    
    fig.write_image(filePath,width=800, height=len(username)*120)

    print(keyword+' table created')        

    


        # fig = go.Figure(data=[go.Table(header=dict(values=['username','bio','location','followers','following','is new']),
        #              cells=dict(values=[username,bio,location,followers,following,isNew]))
        #                  ])
    

# createTable(['exgoog'],['username','username2'],['bio','bio2'],['location','location2'],['followers','followers2'],['following','following2'],[True,False])