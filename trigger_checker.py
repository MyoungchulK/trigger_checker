import numpy as np
import os, sys
import h5py
from tqdm import tqdm

# cern root lib
import ROOT

#def main(Data, Ped, Station, Run, Output):
def main(Data, Station, Run, Output):

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

    # create a geomtool
    geomTool = ROOT.AraGeomTool.Instance()
   
    # trigger channel info 
    trig_ch = np.full((16), np.nan)
    for c in range(16):
       trig_ch[c] = geomTool.getStationInfo(Station).getAntennaInfo(c).getTrigChan()
    print('trigger channel:',trig_ch)

    """
    # open a pedestal file
    calibrator = ROOT.AraEventCalibrator.Instance()
    calibrator.setAtriPedFile(Ped, Station)

    # open general quilty cut
    qual = ROOT.AraQualCuts.Instance()
    """

    # save data
    if not os.path.exists(Output): #check whether there is a directory for save the file or not
        os.makedirs(Output) #if not, create the directory
    os.chdir(Output) #go to the directory

    # create output file
    h5_file_name=f'Trig_ARA{Station}_Run{Run}.h5'
    hf = h5py.File(h5_file_name, 'w')

    g0 = hf.create_group(f'ChanInfo')
    g0.create_dataset('getTrigChan', data=trig_ch, compression="gzip", compression_opts=9)    
    del g0

    # loop over the events
    print('event loop starts!')
    for event in tqdm(range(num_events)):

        # get the desire event
        eventTree.GetEntry(event)

        """
        # make a useful event -> calibration process
        usefulEvent = ROOT.UsefulAtriStationEvent(rawEvent,ROOT.AraCalType.kLatestCalib)
        """

        # selecting only calpulser event
        if rawEvent.isCalpulserEvent() == 1:

            # trigger info
            num_high_trig = rawEvent.numTriggerChansHigh() # number of high trigger channel
            high_trig_ch = []

            # create group
            g1 = hf.create_group(f'Evt{event}')

            # extracting time and volt from every antenna
            for c in range(16):

                # high triggered ch
                if rawEvent.isTriggerChanHigh(int(trig_ch[c])) == True:
                    high_trig_ch.append(int(trig_ch[c]))
                else:
                    pass   

                """
                # get Tgraph(root format) for each antenna
                graph = usefulEvent.getGraphFromRFChan(c)

                # into numpy array
                raw_time = np.frombuffer(graph.GetX(),dtype=float,count=-1) # It is ns(nanosecond)
                raw_volt = np.frombuffer(graph.GetY(),dtype=float,count=-1) # It is mV

                # save wf into 'Evt' group
                g1.create_dataset(f'raw_wf_Ch{c}', data=np.stack([raw_time, raw_volt],axis=-1), compression="gzip", compression_opts=9)
                """

            #print(f'Evt{event} is Calpulser triggered event.')
            #print('# of high trigger channel:',num_high_trig)
            #print('high triggered channel:', high_trig_ch)
       
            # save trigger info
            g1.create_dataset('numTriggerChansHigh', data=np.array([num_high_trig]), compression="gzip", compression_opts=9)
            g1.create_dataset('isTriggerChanHigh', data=np.asarray(high_trig_ch).astype(int), compression="gzip", compression_opts=9)
 
            del g1

        #del usefulEvent

    # close output file
    hf.close()
    del hf

    print('output is',Output+h5_file_name)
    print('Done!!')

if __name__ == "__main__":

    # since there is no click package in cobalt...
    if len (sys.argv) !=5:
        Usage = """
    Usage = python3 %s
    <Raw file ex)/data/exp/ARA/2018/filtered/L0/ARA04/1020/run5531/event5531.root>
    <Station ex)4>
    <Run ex)5531>
    <Output path ex)/data/user/mkim/>
        """ %(sys.argv[0])
        print(Usage)
        del Usage
        sys.exit(1)

    Data=str(sys.argv[1])
    Station=int(sys.argv[2])
    Run=int(sys.argv[3])
    Output=str(sys.argv[4])

    main(Data, Station, Run, Output)
    """
    if len (sys.argv) !=6:
    <Pedestal file ex)/cvmfs/ara.opensciencegrid.org/trunk/centos7/source/AraRoot/AraEvent/calib/ATRI/araAtriStation4Pedestals.txt>
    Ped=str(sys.argv[2])

    main(Data, Ped, Station, Run, Output)
    """
