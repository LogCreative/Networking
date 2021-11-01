# 2. Write an RYU controller that switches paths (h1-s1-s3-s2-h2 or h1-s1-s4-s2-h2) between h1 and h2 every 5 seconds. 

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls
from ryu.lib import packet
from ryu.lib.packet import ether_types, ethernet
from ryu.lib.packet import in_proto as inet
from ryu.ofproto import ofproto_v1_3

pathport = 1

class PeriodicSwtich(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *_args, **_kwargs):
        super(PeriodicSwtich, self).__init__(*_args, **_kwargs)
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        out_port = 1
        
        match = parser.OFPMatch(in_port=1, eth_type=ether_types.ETH_TYPE_IP,ipv4_src='10.0.0.1', ipv4_dst='10.0.0.2',ip_proto=inet.IPPROTO_UDP, udp_dst=5555)
        actions = [parser.OFPActionOutput(out_port)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """
        Default adding flow.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    def add_flow_timeout(self, datapath, priority, match, actions, buffer_id=None):
        """
        Add a flow that timeout in 5 sec.
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst, hard_timeout=5, flags=ofproto.OFPFF_SEND_FLOW_REM)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst, hard_timeout=5, flags=ofproto.OFPFF_SEND_FLOW_REM)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        global pathport

        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Since the switches are added in order,
        # The id is appended in order as well.
        print('CONFIG switch id: '+ str(datapath.id))

        if datapath.id == 1 or datapath.id == 2:
            # forward flow h1 -> s1(s2)
            # input from port 3, output to the selected port.
            match = parser.OFPMatch(in_port=3)
            actions = [parser.OFPActionOutput(pathport)] #
            self.add_flow_timeout(datapath, 2, match, actions)

            # return flow s1(s2) -> h1
            # 2 possible flows: from port 1, from port 2.
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 2, match, actions)
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(3)]
            self.add_flow(datapath, 2, match, actions)
        # elif datapath.id == 3:
        elif datapath.id == 3 or datapath.id == 4:
            # s3 
            match = parser.OFPMatch(in_port=1)
            actions = [parser.OFPActionOutput(2)]
            self.add_flow(datapath, 2, match, actions)
        # elif datapath.id == 4:
            # s4
            match = parser.OFPMatch(in_port=2)
            actions = [parser.OFPActionOutput(1)]
            self.add_flow(datapath, 2, match, actions)

    @set_ev_cls(ofp_event.EventOFPFlowRemoved, MAIN_DISPATCHER)
    def flow_removed_handler(self, ev):
        global pathport
        
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        if msg.reason == ofproto.OFPRR_HARD_TIMEOUT:
            if datapath.id == 1:
                pathport = 2 if pathport==1 else 1  
                # change on pathport could only be invoked once.
                print('Swtich to port: ' + str(pathport))
            print('OFPFlowRemoved received: ' + str(datapath.id))
            match = parser.OFPMatch(in_port=3)
            actions = [parser.OFPActionOutput(pathport)]
            self.add_flow_timeout(datapath, 2, match, actions)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        if ev.msg.msg_len < ev.msg.total_len:
            self.logger.debug("packet truncated: only %s of %s bytes",
                              ev.msg.msg_len, ev.msg.total_len)
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
        dst = eth.dst
        src = eth.src

        actions = [parser.OFPActionOutput(pathport)]        

        # install a flow to avoid packet_in next time
        # if out_port != ofproto.OFPP_FLOOD:
        match = parser.OFPMatch(in_port=in_port, eth_dst=dst, eth_src=src)
        # verify if we have a valid buffer_id, if yes avoid to send both
        # flow_mod & packet_out
        if msg.buffer_id != ofproto.OFP_NO_BUFFER:
            self.add_flow_timeout(datapath, 1, match, actions, msg.buffer_id)
            return
        else:
            self.add_flow_timeout(datapath, 1, match, actions)
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)