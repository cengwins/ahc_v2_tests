import networkx as nx
import time

from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import * #Event, setAHCLogLevel, ConnectorTypes, EventTypes, logger, AHCTimer, DEBUG
from adhoccomputing.Experimentation.Topology import Topology
from adhoccomputing.Networking.LinkLayer.GenericLinkLayer import GenericLinkLayer
from adhoccomputing.Networking.LogicalChannels.GenericChannel import GenericChannel
from adhoccomputing.DistributedAlgorithms.Broadcasting.Broadcasting import ControlledFlooding,BroadcastingEventTypes
import logging

class ApplicationLayer(GenericModel): 
  def on_message_from_bottom(self, eventobj: Event):
    logger.applog(f"{self.componentname}-{self.componentinstancenumber} RECEIVED {str(eventobj)}")

class AdHocNode(GenericModel):
  def on_message_from_top(self, eventobj: Event):
    eventobj.event = EventTypes.MFRT
    self.send_down(eventobj)

  def on_message_from_bottom(self, eventobj: Event):
    eventobj.event = EventTypes.MFRB
    self.send_up(eventobj)

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
    # SUBCOMPONENTS
    self.appl = ApplicationLayer("ApplicationLayer", componentinstancenumber, topology=topology)
    self.broadcastservice = ControlledFlooding("ControlledFlooding", componentinstancenumber, topology=topology)
    self.linklayer = GenericLinkLayer("GenericLinkLayer", componentinstancenumber, topology=topology)

    self.components.append(self.appl)
    self.components.append(self.broadcastservice)
    self.components.append(self.linklayer)

    
    # CONNECTIONS AMONG SUBCOMPONENTS
    self.appl.connect_me_to_component(ConnectorTypes.DOWN, self.broadcastservice)
    self.broadcastservice.connect_me_to_component(ConnectorTypes.UP, self.appl)

    self.broadcastservice.connect_me_to_component(ConnectorTypes.DOWN, self.linklayer)
    self.linklayer.connect_me_to_component(ConnectorTypes.UP, self.broadcastservice)

    # Connect the bottom component to the composite component....
    self.linklayer.connect_me_to_component(ConnectorTypes.DOWN, self)
    self.connect_me_to_component(ConnectorTypes.UP, self.linklayer)

topo = Topology()

def send_broadcast_message_event():
  topo.nodes[0].broadcastservice.trigger_event(Event(None, BroadcastingEventTypes.BROADCAST, "BROADCAST MESSAGE"))

def main():
  #NOTSET, DEBUG, INFO, WARNING, ERROR, CRITICAL
  setAHCLogLevel(DEBUG)
  #A random geometric graph, undirected and without self-loops
  G = nx.random_geometric_graph(9, 1)
  
  
  # G =nx.Graph()
  # G.add_node(0)
  # G.add_node(1)
  # G.add_node(2)
  # G.add_edge(0,1)
  # G.add_edge(1,0)
  # G.add_edge(0,2)
  # G.add_edge(2,0)
  # G.add_edge(1,2)
  # G.add_edge(2,1)

  
  topo.construct_from_graph(G, AdHocNode, GenericChannel)
  print(str(topo))
  topo.start()
  t = AHCTimer(1, send_broadcast_message_event)
  t.start()

  time.sleep(5)
  t.cancel()
  topo.exit()

if __name__ == "__main__":
  main()
