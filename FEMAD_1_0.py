import shutil
import os

import sys

import smtplib


import numpy as np
import matplotlib.pyplot as plt

import mpl_toolkits.axisartist as AA
from mpl_toolkits.axes_grid1 import host_subplot

import time
#from datetime import date
from datetime import datetime, timedelta


# Import the email modules we'll need
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


import urllib
from urllib.request import urlopen
#####################################################################################################
#####################################################################################################
##
##    GLOBAL VARIABLES
##
#####################################################################################################
#####################################################################################################

Time_A = []
TimeStps_A = []
Itter_A = []
#
TimeStp = 0
d3plot=0
FlStr=0
FlTime=0
Endtime=0
NowTime=0
TotTime=0
nitt = 1
Simulation=''
PFrek = 0
Noopr = 0
#
TimeFlag=0
#
#####################################################################################################
#####################################################################################################
##
##    FUNCTIONS
##
#####################################################################################################
#####################################################################################################

##   Plot function, PROGRESS
##################################################################################
def PlotFunk(BaseName):
    global Time_A, TimeStps_A, Itter_A, TimeStp
    ####
    fig, ax1 = plt.subplots()
    
    # Stepsize
    Line_1, = ax1.plot(Time_A, TimeStps_A, 'b-', linewidth=2.5, label='Stepsize, $\Delta t$')
    ax1.set_xlabel('Time, $t$', fontsize=16)
    ax1.set_title(BaseName, fontsize=18)
    
    # Make the y-axis label and tick labels match the line color.
    ax1.set_ylabel('Stepsize, $\Delta t$', color='b', fontsize=16)
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
    
    ax2 = ax1.twinx()
    
    # Iterations
    Line_2, = ax2.plot(Time_A, Itter_A, 'r-', linewidth=1.5, label='Iterations')
    ax2.set_ylabel('No of iterations', color='r', fontsize=16)
    
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
        
    plt.legend(handles=[Line_1, Line_2])

    Exten = ".png"
    Figname = "%s%s%s" %(BaseName, TimeStp, Exten)
    print('Saving plot: ',Figname)
    plt.savefig(Figname)
    plt.clf()
    return Figname
##################################################################################
##   Send mail
##################################################################################
def SendProgress(Figname, SimName):
    global d3plot, Proc, FlTime, TimeStp, Endtime
    PrembMail1 = " Progress of analysis:  %s \n -----------------------------------------------------\n" %(SimName)
    Slask1 = " Simulated time:  %f \n" %FlTime
    Proc = round(100*FlTime/Endtime)
    Slask2 = " Procentage of total time:  %i\n" %int(Proc)
    Slask3 = " Number of d3plots generated:  %i\n" %d3plot
    Slask4 = " Total CPU time:  %s" %TotTime
    #TotTime
    Exten = ".txt"
    Xfile = "%s%s%s" %(SimName, TimeStp, Exten)
    #XFile='C:\\Users\\niklas.safstrom\\PROJECTS\\SLASK_Python\\ProgressMail.txt'
    fm = open(Xfile, 'w') 
    fm.write(PrembMail1)
    fm.write(Slask1)
    fm.write(Slask2)
    fm.write(Slask3)
    fm.write(Slask4)
    fm.close()
    ###
    fp = open(Figname, 'rb')
    img = MIMEImage(fp.read())
    fp.close()
    ####
    msg = MIMEMultipart()
    with open(Xfile, 'r') as fm:
        msgText = MIMEText(fm.read())
    fm.closed
    ###
    msg.attach(msgText)
    msg.attach(img)
    me = 'niklas.safstrom@shl-group.com'
    you = 'niklas.safstrom@shl-group.com'
    msg['Subject'] = 'Simulation report'
    msg['From'] = me
    msg['To'] = you
    #msg.attach(img)
    s = smtplib.SMTP('192.168.0.30')
    s.sendmail(me, you, msg.as_string())
    s.quit()
    return
##################################################################################
##   Termination mail
##################################################################################
def SendTermination(SimName, ErMail, NtMail):
    global TimeStp
    if NtMail == 1:
        PrembMail1 = " Normal termination of analysis:  %s \n -----------------------------------------------------\n" %(SimName)
    elif ErMail == 1:
        PrembMail1 = " Error termination of analysis:  %s \n -----------------------------------------------------\n" %(SimName)
    #
    Exten = ".txt"
    Xfile = "%s%s%s" %(SimName, TimeStp, Exten)
    #XFile='C:\\Users\\niklas.safstrom\\PROJECTS\\SLASK_Python\\ProgressMail.txt'
    fm = open(Xfile, 'w') 
    fm.write(PrembMail1)
    fm.close()
    ###
    ####
    msg = MIMEMultipart()
    with open(Xfile, 'r') as fm:
        msgText = MIMEText(fm.read())
    fm.closed
    ###
    msg.attach(msgText)
    me = 'niklas.safstrom@shl-group.com'
    you = 'niklas.safstrom@shl-group.com'
    msg['Subject'] = 'Simulation report'
    msg['From'] = me
    msg['To'] = you
    #msg.attach(img)
    s = smtplib.SMTP('192.168.0.30')
    s.sendmail(me, you, msg.as_string())
    s.quit()
    return
##################################################################################
##   Read d3hsp/data
##################################################################################
def ReadD3Buf():
    #
    global d3plot, TimeStp, Time_A, TimeStps_A, Itter_A, D3Buf, StartTime, TotTime, FlTime, NowTime
    #
    Time_A = []
    TimeStps_A = []
    Itter_A = []
    TimeStp = 0
    WD3Buf=D3Buf
    d3plot = 0
    try:
        
        while True:
            linestartD3 = WD3Buf.find('Equilibrium iterations summary step')
            if linestartD3 == -1:
                print('hoho')
                NowTime = datetime.now()
                TotTime = NowTime - StartTime
                return
            else: 
                #print('hoho2')
                TimeStp = TimeStp + 1
                lineendD3 = WD3Buf.find('BEGIN',linestartD3)
                #
                if lineendD3 != -1:
                    D3Line = WD3Buf[linestartD3:lineendD3]
                else:
                    D3Line = WD3Buf[linestartD3:]
                #### d3Plot Count
                #####################################
                check1=D3Line.find('write d3plot file')
                if check1 != -1:
                    d3plot = d3plot + 1
                #### Plot Time
                #####################################
                StrTime=D3Line[45:60]
                StrTime = StrTime.replace(' ','')
                FlTime=float(StrTime)
                Time_A.append(FlTime)
                if TimeStp == 1:
                    TimeStps_A.append(FlTime)
                else:
                    x2=Time_A[TimeStp-1]
                    x1=Time_A[TimeStp - 2]
                    Stepsize=x2-x1
                    TimeStps_A.append(Stepsize)
                ## Iterations to Conv
                #####################################
                linestart2 = D3Line.find('Number of iterations to converge')
                lineend2 = D3Line.find('Number of stiffness reformations',linestart2)
                Line2= D3Line[linestart2:lineend2]
                ItCon=Line2[47:59]
                ItCon = ItCon.replace(' ','')
                FlItCon=int(ItCon)
                Itter_A.append(FlItCon)
                ####################################
                WD3Buf = WD3Buf[lineendD3:]
                ####################################
    except:
        print('Error when reading d3hsp data. Leaving')
        return
    return
#####################################################################################################
#####################################################################################################
##
##    START    MAIN Function
##
#####################################################################################################
#####################################################################################################

######################################################
##   Input, Open Run file
######################################################
# Sinulation name
SimulName = input('Name of analysis (implicit): ')

# Inputfile
InpFile = input("Input file (E.g. Run.key): ")
if os.path.exists(InpFile):
    try:
        with open(InpFile, 'r') as RunF:
            RunBuf = RunF.read()
        RunF.closed
        StControl = RunBuf.find("*CONTROL_TERMINATION")
        RunBuf = RunBuf[StControl+1:]
        EnControl = RunBuf.find("*")
        RunBuf = '*' + RunBuf[:EnControl]
        print('\n' + RunBuf)
        TFind = RunBuf.find("\n ")
        TTime = RunBuf[TFind:TFind+12]
        FlTTime = float(TTime.replace(' ',''))
        print("\n" + "Total simulation time: ",FlTTime)
    except:
        print('Exception in handling! Leaving...')
else:
    sys.exit('Could not find file ({0}). Leaving...'.format(InpFile))
    
# Number of progress reports, Noopr
while True:
    try:
        Noopr = int(input("\n Number of progress resports ( > 0 ): "))
        print('\n')
        break
    except ValueError:
        print("Oops!  That was no valid number.  Try again...")

# Compute PFrek
PFrek=float(FlTTime/Noopr)
Endtime=FlTTime
print("Simulation time span between reports: ", PFrek)

######################################################
##   Reading and sending
######################################################
fname = 'd3hsp'
if os.path.exists(fname):
    print('Converting ' + fname + '...')
else:
    print('Could not find file ({0}). Leaving...'.format(fname))
    sys.exit()
#
StartTime = datetime.now()
nitt = 1
#read original file to memory buffer
print('Starting \n')
try:
    next_info = ""
    while(1):
        info = os.stat(fname)
        #print(info)
        if(info.st_mtime != next_info):
            #print (info.st_mtime)
            with open(fname, 'r') as f:
                D3Buf = f.read()
            f.closed
            ###f = open(fname, 'r')
            ###D3Buf = f.read()
            ###f.close()
            #
            ErMail=0
            NtMail=0
            ChckNT = D3Buf.find('N o r m a l    t e r m i n a t i o n')
            ChckET = D3Buf.find('E r r o r   t e r m i n a t i o n')
            if ChckNT != -1:
                NtMail=1
                SendTermination(SimulName, ErMail, NtMail)
                sys.exit()
            if ChckET != -1:
                ErMail=1
                SendTermination(SimulName, ErMail, NtMail)
                sys.exit()
            #
            ReadD3Buf()
            #print('Hoho3 ',FlTime)
            #
            if FlTime >= nitt*PFrek:
                SendPlot = PlotFunk(SimulName)
                SendProgress(SendPlot, SimulName)
                print('Sending: ', SendPlot)
                nitt = nitt + 1
                
            next_info = info.st_mtime
            #prev_buf = buf[len(buf)-1:].replace("\n","")

except:
    print('Leaving...')
    sys.exit()

#sys.exit()
#####################################################################################################
#####################################################################################################
#####################################################################################################
#####################################################################################################
