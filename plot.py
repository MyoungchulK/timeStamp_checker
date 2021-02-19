import os, sys 
import numpy as np 
from matplotlib import pyplot as plt 
import h5py 

def hist_1d(xlabel,ylabel,title
            ,xmin,xmax,xsc
            ,ymin,ymax,ysc
            ,bin_range_step
            ,d_path,file_name
            ,data=None,legend=None
            ,data1=None,legend1=None
            ,data2=None,legend2=None):

    #plot
    fig = plt.figure(figsize=(10, 7))
    plt.xlabel(xlabel, fontsize=25)
    plt.ylabel(ylabel, fontsize=25)
    plt.grid()
    plt.tick_params(axis='x', labelsize=20)
    plt.tick_params(axis='y', labelsize=20)
    plt.title(title, y=1.02,fontsize=25)
    plt.xscale(xsc)
    plt.yscale(ysc)
    plt.xlim(xmin,xmax)
    plt.ylim(ymin,ymax)
    
    if data is not None:
        plt.hist(data,bins=bin_range_step,histtype='step',linewidth=3,linestyle='-',color='green',alpha=0.5,label=legend)
    if data1 is not None:
        plt.hist(data1,bins=bin_range_step,histtype='step',linewidth=3,linestyle='-',color='orangered',alpha=0.5,label=legend1)
    if data2 is not None:
        plt.hist(data2,bins=bin_range_step,histtype='step',linewidth=3,linestyle='-',color='dodgerblue',alpha=0.5,label=legend2)

    #plt.legend(loc='lower center',bbox_to_anchor=(1.17,0), numpoints = 1 ,fontsize=15)
    plt.legend(loc='best',numpoints = 1 ,fontsize=15)
    
    os.chdir(d_path)
    fig.savefig(file_name,bbox_inches='tight')
    #plt.show()
    plt.close()
    del fig
    
def plot_1(xlabel,ylabel
            ,title
            ,x_data,y_data,legend
            ,d_path,file_name):

    fig = plt.figure(figsize=(10, 7))
    plt.xlabel(xlabel, fontsize=25)
    plt.ylabel(ylabel, fontsize=25)
    plt.grid()
    plt.tick_params(axis='x', labelsize=20)
    plt.tick_params(axis='y', labelsize=20)
    plt.title(title, y=1.02,fontsize=15)

    plt.plot(x_data,y_data,'-',lw=3,color='orange',alpha=0.7,label=legend)
    plt.legend(loc='best', numpoints = 1 ,fontsize=15)
    
    os.chdir(d_path)
    fig.savefig(file_name,bbox_inches='tight')
    #plt.show()
    plt.close() 
    del fig

def main(Input, Output, Station, Run):

    if not os.path.exists(Output):
        os.makedirs(Output)

    temp_file = h5py.File(Input, 'r')

    timeStamp_Trigger = temp_file['timeStamp_Trigger']
    Cal = timeStamp_Trigger['Cal'][:]
    RF = timeStamp_Trigger['RF'][:]
    Soft = timeStamp_Trigger['Soft'][:]

    hist_1d(r'TimeStamp (# of bin on the raw WF)',r'# of events x antennas',f'A{Station} Run{Run}, timeStamp distribution by each Triggers'
        ,0,4000,'linear'
        ,0.1,1e4,'log'
        ,np.arange(-5,10000,5)
        ,Output,f'A{Station}_Run{Run}_timeStamp_distribution_by_each_Triggers.png'
        ,Cal,'Calpulser'
        ,Soft,'Software'
        ,RF,'RF')

    event=101
    channel=0

    Evt101 = temp_file[f'Evt{event}']
    raw_wf_Ch0 = Evt101[f'raw_wf_Ch{channel}'][:]
    timeStamp = Evt101['timeStamp'][:]

    plot_1(r'Time [ $ns$ ]',r'Amplitude [ $mV$ ]'
            ,f'A{Station} Run{Run}, raw WF, Evt{event}, Ch{channel}'
            ,raw_wf_Ch0[:,0],raw_wf_Ch0[:,1],'# of bins (timeStamp):'+str(timeStamp[0])
            ,Output,f'A{Station}_Run{Run}_raw_WF_Evt{event}_Ch{channel}.png')
    print('Done!')

if __name__ == "__main__":

    # since there is no click package in cobalt...
    if len (sys.argv) !=5:
        Usage = """
    Usage = python3 %s
    <Input ex)/data/user/mkim/timeStamp_ARA4_Run5531.h5>
    <OutPut ex)/data/user/mkim/>
    <Station ex)4>
    <Run ex)5531>
        """ %(sys.argv[0])
        print(Usage)
        del Usage
        sys.exit(1)

    Input=str(sys.argv[1])
    Output=str(sys.argv[2])
    Station=str(sys.argv[3])
    Run=str(sys.argv[4])
    
    main(Input, Output, Station, Run)

















