from adhoccomputing.GenericModel import GenericModel
from adhoccomputing.Generics import *
from adhoccomputing.Experimentation.Topology import Topology
import time

class A(GenericModel):
  def on_init(self, eventobj: Event):
    evt = Event(self, EventTypes.MFRT, "A to lower layer")
    self.send_down(evt)

  def on_message_from_bottom(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}\n")

class B(GenericModel):
  def on_init(self, eventobj: Event):
    evt = Event(self, EventTypes.MFRP, "B to peers")
    self.send_peer(evt)

  def on_message_from_top(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}\n")

  def on_message_from_bottom(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}\n")
    evt = Event(self, EventTypes.MFRB, "B to higher layer")
    self.send_up(evt)

  def on_message_from_peer(self, eventobj: Event):
    print(f"I am {self.componentname}, got message from peer, eventcontent={eventobj.eventcontent}\n")

class N(GenericModel):
  def on_message_from_top(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}\n")
    evt = Event(self, EventTypes.MFRT, "N to lower layer")
    self.send_down(evt)

  def on_message_from_bottom(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}\n")

  def on_message_from_peer(self, eventobj: Event):
    print(f"I am {self.componentname}, got message from peer, eventcontent={eventobj.eventcontent}\n")

class L(GenericModel):
  def on_message_from_top(self, eventobj: Event):
    print(f"I am {self.componentname}, eventcontent={eventobj.eventcontent}")
    evt = Event(self, EventTypes.MFRB, "L to higher layer")
    self.send_up(evt)

class Node(GenericModel):
  def on_init(self, eventobj: Event):
    pass

  def on_message_from_top(self, eventobj: Event):
    self.send_down(Event(self, EventTypes.MFRT, eventobj.eventcontent))

  def on_message_from_bottom(self, eventobj: Event):
    self.send_up(Event(self, EventTypes.MFRB, eventobj.eventcontent))

  def __init__(self, componentname, componentinstancenumber, context=None, configurationparameters=None, num_worker_threads=1, topology=None):
    super().__init__(componentname, componentinstancenumber, context, configurationparameters, num_worker_threads, topology)
    # SUBCOMPONENTS
    self.A = A("A", componentinstancenumber)
    self.N = N("N", componentinstancenumber)
    self.B = B("B", componentinstancenumber)
    self.L = L("L", componentinstancenumber)

    self.components.append(self.A)
    self.components.append(self.N)
    self.components.append(self.B)
    self.components.append(self.L)

  # THERE ARE THREE WAYS FOR COMPOSITION AS SHOWN BELOW
  # USE ONLY ONE OF THEM IN ORDER NOT TO GET ERRORS

    # # CONNECTIONS AMONG SUBCOMPONENTS  USING DIRECT FUNCTIONS
    # self.A.connect_me_to_component(ConnectorTypes.DOWN, self.B)
    # self.A.connect_me_to_component(ConnectorTypes.DOWN, self.N)
    # self.N.connect_me_to_component(ConnectorTypes.UP, self.A)
    # self.B.connect_me_to_component(ConnectorTypes.UP, self.A)
    # self.N.connect_me_to_component(ConnectorTypes.PEER, self.B)
    # self.B.connect_me_to_component(ConnectorTypes.PEER, self.N)
    # self.B.connect_me_to_component(ConnectorTypes.DOWN, self.L)
    # self.N.connect_me_to_component(ConnectorTypes.DOWN, self.L)
    # self.L.connect_me_to_component(ConnectorTypes.UP, self.B)
    # self.L.connect_me_to_component(ConnectorTypes.UP, self.N)
    # ## Connect the bottom component to the composite component....
    # self.L.connect_me_to_component(ConnectorTypes.DOWN, self)
    # self.connect_me_to_component(ConnectorTypes.UP, self.L)

    ## CONNECTION using U (up) D (down) P (peer) functions
    self.A.D(self.B)
    self.A.D(self.N)
    self.N.U(self.A)
    self.B.U(self.A)
    self.N.P(self.B)
    self.B.P(self.N)
    self.N.D(self.L)
    self.L.U(self.B)
    self.L.U(self.N)
    self.L.D(self)
    self.U(self.L)
    
    # ## CONNECTION USING INFIX OPERATAORS
    # self.A |D| self.B
    # self.A |D| self.N
    # self.N |U| self.A
    # self.B |U| self.A
    # self.N |P| self.B
    # self.B |P| self.N
    # self.N |D| self.L
    # self.L |U| self.B
    # self.L |U| self.N
    # self.L |D| (self)
    # self |U| self.L


def main():
  setAHCLogLevel(DEBUG)
  topo = Topology();
  topo.construct_single_node(Node, 0)
  topo.start()
  time.sleep(1)
  topo.exit()

if __name__ == "__main__":
  main()
