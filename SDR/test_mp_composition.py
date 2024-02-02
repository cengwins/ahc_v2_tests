import os
import sys
import time
sys.path.insert(0, os.getcwd())
import networkx as nx
from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
import queue
from multiprocessing import Manager, freeze_support
from adhoccomputing.Distribution.AHCManager import AHCManager, AHCManagerType

CRED = '\033[91m'
CEND = '\033[0m'

class A(GenericModel):
  counter = 0 
  def send_message(self):
    self.counter += 1
    evt = Event(self, EventTypes.MFRT, "TO CHANNEL" + str(self.counter))
    self.send_down(evt)
    logger.applog(f"I am {self.componentname}-{self.componentinstancenumber}, {str(evt)}")

  def on_init(self, eventobj: Event):
    logger.applog(f"I am {self.componentname}-{self.componentinstancenumber}, will run on_init")
      
    if self.componentinstancenumber == 0:
      self.t = AHCTimer(1, self.send_message) # 1 SECOND
      self.t.start()
      logger.applog(f"I am {self.componentname}-{self.componentinstancenumber}, started message sending thread with AHCTimer")
      
        
  def on_message_from_bottom(self, eventobj: Event):
    logger.applog(f"I am {self.componentname}-{self.componentinstancenumber}, eventcontent={eventobj.eventcontent}")

class Node(GenericModel):
  def on_init(self, eventobj: Event):
    pass

  def on_message_from_top(self, eventobj: Event):
    self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))
    logger.applog(f"{self.componentname}.{self.componentinstancenumber} RECEIVED {str(eventobj)}")
    

  def on_message_from_bottom(self, eventobj: Event):
    self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))
    logger.applog(f"{self.componentname}.{self.componentinstancenumber} RECEIVED {str(eventobj)}")

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None, child_conn=None, node_queues=None, channel_queues=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology, child_conn, node_queues, channel_queues)
    # SUBCOMPONENTS

    self.A = A("A", componentinstancenumber, topology=topology)
    self.components.append(self.A)

    # CONNECTIONS AMONG SUBCOMPONENTS
    self.A.connect_me_to_component(ConnectorTypes.DOWN, self)
    self.connect_me_to_component(ConnectorTypes.UP, self.A)

def main(argv):
  setAHCLogLevel(DEBUG)
  set_start_method = "fork";
  topo = Topology()

  # numnodes = 10
  # topo.mp_construct_sdr_topology_without_channels( numnodes, Node )
  # topo.start()
  # time.sleep(1)
  # topo.exit()

  #G = nx.random_geometric_graph(4, 1)
  G =nx.Graph()
  G.add_node(0)
  G.add_node(1)
  G.add_node(2)
  G.add_edge(0,1)
  G.add_edge(1,0)
  G.add_edge(0,2)
  G.add_edge(2,0)
  G.add_edge(1,2)
  G.add_edge(2,1)
  
  ahcmanager = AHCManager(AHCManagerType.AHC_CLIENT, argv)
  try:
    ahcmanager.connect()
  except Exception as ex:
    logger.critical("Could not connect to AHCManager that helps distributing processes over different machines.")
  topo.mp_construct_sdr_topology(G, Node, GenericChannel,ahcmanager)
  logger.applog("Will start the emulation")
  topo.start()
  while(True):
    time.sleep(1)
  topo.exit()


if __name__ == "__main__":
  freeze_support()
  main(sys.argv)
