#!/usr/bin/python
# MIT License
# Copyright (c) 2018 Jetsonhacks
# Copyright (c) 2019 ninn55
import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
from collections import deque

# Check admin right.
if os.getuid()!=0:
    sys.exit("Please use sudo.")

gpuLoadFile="/sys/devices/gpu.0/load"
# On the Jetson TX1 this is a symbolic link to:
# gpuLoadFile="/sys/devices/platform/host1x/57000000.gpu/load"
# On the Jetson TX2, this is a symbolic link to:
# gpuLoadFile="/sys/devices/platform/host1x/17000000.gp10b/load"
cpuLoadDirs=["/sys/devices/system/cpu/cpu0/cpufreq",
			"/sys/devices/system/cpu/cpu1/cpufreq",
			"/sys/devices/system/cpu/cpu2/cpufreq",
			"/sys/devices/system/cpu/cpu3/cpufreq",
			"/sys/devices/system/cpu/cpu4/cpufreq",
			"/sys/devices/system/cpu/cpu5/cpufreq"]
cpuMaxFile="/cpuinfo_max_freq"
cpuLoadFile="/cpuinfo_cur_freq"
# CPU load file only tested on TX2

fig = plt.figure(figsize=(9,6))
#plt.subplots_adjust(top=0.85, bottom=0.30)
fig.set_facecolor('#F2F1F0')
fig.canvas.set_window_title('GPU/CPU Activity Monitor')

# Subplot for the GPU activity
#gpuAx = plt.subplot2grid((2,1), (0,0))
gs = gridspec.GridSpec(2, 1)
gs.update(hspace = 0.38)
gpuAx = plt.subplot(gs[0, 0])
#cpuAx = plt.subplot2grid((2,1), (1,0))
cpuAx = plt.subplot(gs[1, 0])

# For the comparison
gpuLine, = gpuAx.plot([],[])
cpuLine, = cpuAx.plot([],[])

# The line points in x,y list form
gpuy_list = deque([0]*240)
gpux_list = deque(np.linspace(60,0,num=240))
cpuy_list = deque([0]*240)
cpux_list = deque(np.linspace(60,0,num=240))

gpu_fill_lines=0
cpu_fill_lines=0

def initGraph():
    global gpuAx
    global gpuLine
    global gpu_fill_lines

    global cpuAx
    global cpuLine
    global cpu_fill_lines

    gpuAx.set_xlim(60, 0)
    gpuAx.set_ylim(-5, 105)
    gpuAx.set_title('GPU History')
    gpuAx.set_ylabel('GPU Usage (%)')
    gpuAx.set_xlabel('Seconds');
    gpuAx.grid(color='gray', linestyle='dotted', linewidth=1)
    
    cpuAx.set_xlim(60, 0)
    cpuAx.set_ylim(-5, 105)
    cpuAx.set_title('CPU History')
    cpuAx.set_ylabel('CPU Usage (%)')
    cpuAx.set_xlabel('Seconds');
    cpuAx.grid(color='gray', linestyle='dotted', linewidth=1)

    gpuLine.set_data([],[])
    gpu_fill_lines=gpuAx.fill_between(gpuLine.get_xdata(),50,0)
    cpuLine.set_data([],[])
    cpu_fill_lines=cpuAx.fill_between(cpuLine.get_xdata(),50,0)

    return gpuLine, cpuLine, gpu_fill_lines, cpu_fill_lines

def updateGraph(frame):
    global gpu_fill_lines
    global gpuy_list
    global gpux_list
    global gpuLine
    global gpuAx

    global cpu_fill_lines
    global cpuy_list
    global cpux_list
    global cpuLine
    global cpuAx
 
    # Now draw the GPU usage
    gpuy_list.popleft()
    with open(gpuLoadFile, 'r') as gpuFile:
      fileData = gpuFile.read()
    # The GPU load is stored as a percentage * 10, e.g 256 = 25.6%
    gpuy_list.append(int(fileData)/10)
    gpuLine.set_data(gpux_list,gpuy_list)
    gpu_fill_lines.remove()
    gpu_fill_lines=gpuAx.fill_between(gpux_list,0,gpuy_list, facecolor='cyan', alpha=0.50)
    
    # Now draw the CPU usage
    # CPU usage is the average of curentFrequency/maxFrequency on every core
    cpuy_list.popleft()
    cpuUag=0
    for cpuDir in cpuLoadDirs:
        with open(cpuDir+cpuLoadFile, 'r') as cpuFile:
            cpuFeq = cpuFile.read()
        with open(cpuDir+cpuMaxFile, 'r') as cpuFile:
            cpuMax = cpuFile.read()
        cpuUag+=(int(cpuFeq)/int(cpuMax))/len(cpuLoadDirs)
    cpuy_list.append(cpuUag*100)
    cpuLine.set_data(cpux_list,cpuy_list)
    cpu_fill_lines.remove()
    cpu_fill_lines=cpuAx.fill_between(cpux_list,0,cpuy_list, facecolor='red', alpha=0.50)

    return gpuLine, cpuLine, gpu_fill_lines, cpu_fill_lines


# Keep a reference to the FuncAnimation, so it does not get garbage collected
animation = FuncAnimation(fig, updateGraph, frames=200,
                    init_func=initGraph,  interval=250, blit=True)


plt.show()


