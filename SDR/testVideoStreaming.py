import os
import sys
import time
sys.path.insert(0, os.getcwd())
import time
import cv2


from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.NetworkLayer.GenericNetworkLayer import GenericNetworkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.Networking.ApplicationLayer.OpenCVVideoStreamingApp import *
from adhoccomputing.Networking.ApplicationLayer.MessageSegmentation import *

appconfig = OpenCVVideoStreamingAppConfig(10)

class AdHocNode(GenericModel):

    def on_init(self, eventobj: Event):
        logger.applog(f"Initializing {self.componentname}.{self.componentinstancenumber}")
        pass

    def on_message_from_top(self, eventobj: Event):
        self.send_down(eventobj)

    def on_message_from_bottom(self, eventobj: Event):
        self.send_up(eventobj)

    def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
        super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
        # SUBCOMPONENTS
        self.appl = OpenCVVideoStreamingApp("OpenCVVideoStreamingApp", componentinstancenumber, topology=topology, configurationparameters=appconfig)
        self.seg = MessageSegmentation("MessageSegmentation", componentinstancenumber, topology=topology)

        self.components.append(self.appl)
        self.components.append(self.seg)

        ##Connect the bottom component to the composite component....
        ## CONNECTION USING INFIX OPERATAORS
        self.appl |D| self.seg
        self.seg |D| self

        self |U| self.seg
        self.seg |U| self.appl

def main():

    #NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
    setAHCLogLevel(25)
    setAHCLogLevel(LOG_LEVEL_APPLOG)
    topo = Topology()
    topo.construct_sender_receiver(AdHocNode, AdHocNode, GenericChannel)
    topo.start()
    topo.nodes[0].appl.trigger_event(Event(None, OpenCVVideoStreamingAppEventTypes.STARTSTREAMING, ""))

    cap = cv2.VideoCapture(0)
    #cap.set(3,640)
    #cap.set(4,480)

    #fourcc = cv2.VideoWriter_fourcc(*'MP4V')
    #out = cv2.VideoWriter('output.mp4', fourcc, 20.0, (640,480))

    while(True):
        frame = topo.nodes[1].appl.frame
        if frame is not None:
            #out.write(frame)
            #frameresized = cv2.resize(frame, (640,480))
            frameresized = frame
            cv2.imshow('frame', frameresized)
            c = cv2.waitKey(1)
            if c & 0xFF == ord('q'):
                break

    cap.release()
    #out.release()
    cv2.destroyAllWindows()

    topo.exit()
    time.sleep(5)

if __name__ == "__main__":
    main()
