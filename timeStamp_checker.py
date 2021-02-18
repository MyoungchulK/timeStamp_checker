import numpy as np
import os, sys
import h5py
from tqdm import tqdm

# cern root lib
import ROOT

def main(Data, Ped, Station, Run, Output):

    # import cern root and ara root lib from cvmfs
    ROOT.gSystem.Load(os.environ.get('ARA_UTIL_INSTALL_DIR')+"/lib/libAraEvent.so")

    # open a data file
    file = ROOT.TFile.Open(Data)

    # load in the event free for this file
    eventTree = file.Get("eventTree")

    # set the tree address to access our raw data type
    rawEvent = ROOT.RawAtriStationEvent()
    eventTree.SetBranchAddress("event",ROOT.AddressOf(rawEvent))

    # get the number of entries in this file
    num_events = eventTree.GetEntries()
    print('total events:', num_events)

    # open a pedestal file
    calibrator = ROOT.AraEventCalibrator.Instance()
    calibrator.setAtriPedFile(Ped, Station)

    # open general quilty cut
    #qual = ROOT.AraQualCuts.Instance()

    # save data
    if not os.path.exists(Output): #check whether there is a directory for save the file or not
        os.makedirs(Output) #if not, create the directory
    os.chdir(Output) #go to the directory

    # create output file
    h5_file_name=f'timeStamp_ARA{Station}_Run{Run}.h5'
    hf = h5py.File(h5_file_name, 'w')

    # array for timestamp
    rf_timeStamp = []
    soft_timeStamp = []
    cal_timeStamp = []

    # loop over the events
    print('event loop starts!')
    for event in tqdm(range(num_events)):

        # get the desire event
        eventTree.GetEntry(event)

        # make a useful event -> calibration process
        usefulEvent = ROOT.UsefulAtriStationEvent(rawEvent,ROOT.AraCalType.kLatestCalib)

        # create group
        g1 = hf.create_group(f'Evt{event}')

        # trigger tag check
        if rawEvent.isSoftwareTrigger() == 1:
            trig = 'Soft'
        elif rawEvent.isCalpulserEvent() == 1:
            trig = 'Cal'
        elif rawEvent.isSoftwareTrigger() == 0 and rawEvent.isCalpulserEvent() == 0:
            trig = 'RF'
        g1.attrs['Trigger'] = trig

        evt_timeStamp = []

        # extracting time and volt from every antenna
        for c in range(16):

            # get Tgraph(root format) for each antenna
            graph = usefulEvent.getGraphFromRFChan(c)

            # into numpy array
            raw_time = np.frombuffer(graph.GetX(),dtype=float,count=-1) # It is ns(nanosecond)
            raw_volt = np.frombuffer(graph.GetY(),dtype=float,count=-1) # It is mV

            #time stamp
            t_Stamp = len(raw_volt)
            evt_timeStamp.append(t_Stamp)
            if trig == 'Soft':
                soft_timeStamp.append(t_Stamp)
            elif trig == 'Cal':
                cal_timeStamp.append(t_Stamp)
            elif trig == 'RF':
                rf_timeStamp.append(t_Stamp)

            # save wf into 'Evt' group
            g1.create_dataset(f'raw_wf_Ch{c}', data=np.stack([raw_time, raw_volt],axis=-1), compression="gzip", compression_opts=9)

            graph.Delete()
            del raw_time, raw_volt#, graph

        g1.create_dataset(f'timeStamp', data=np.asarray(evt_timeStamp), compression="gzip", compression_opts=9)

        #usefulEvent.Delete()
        del g1, usefulEvent

    # create group
    g2 = hf.create_group(f'timeStamp_Trigger')
    g2.create_dataset(f'RF', data=np.asarray(rf_timeStamp), compression="gzip", compression_opts=9)
    g2.create_dataset(f'Soft', data=np.asarray(soft_timeStamp), compression="gzip", compression_opts=9)
    g2.create_dataset(f'Cal', data=np.asarray(cal_timeStamp), compression="gzip", compression_opts=9)
    del g2

    print('# of RF tStamp:',len(np.asarray(rf_timeStamp)))
    print('# of Soft tStamp:',len(np.asarray(soft_timeStamp)))
    print('# of Cal tStamp:',len(np.asarray(cal_timeStamp)))

    # close output file
    hf.close()
    del hf

    print('output is',Output+h5_file_name)
    print('Done!!')

if __name__ == "__main__":

    # since there is no click package in cobalt...
    if len (sys.argv) !=6:
        Usage = """
    Usage = python3 %s
    <Raw file ex)/data/exp/ARA/2018/filtered/L0/ARA04/1020/run5531/event5531.root>
    <Pedestal file ex)/cvmfs/ara.opensciencegrid.org/trunk/centos7/source/AraRoot/AraEvent/calib/ATRI/araAtriStation4Pedestals.txt>
    <Station ex)4>
    <Run ex)5531>
    <Output path ex)/data/user/mkim/>
        """ %(sys.argv[0])
        print(Usage)
        del Usage
        sys.exit(1)

    Data=str(sys.argv[1])
    Ped=str(sys.argv[2])
    Station=int(sys.argv[3])
    Run=int(sys.argv[4])
    Output=str(sys.argv[5])

    main(Data, Ped, Station, Run, Output)
