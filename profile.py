#!/usr/bin/env python

kube_description= \
"""
O-RAN deployment
"""
kube_instruction= \
"""
Installation instructions: https://github.com/j0lama/O-RAN-Powder/blob/main/README.md
"""

#
# Standard geni-lib/portal libraries
#
import geni.portal as portal
import geni.rspec.pg as PG
import geni.rspec.emulab as elab
import geni.rspec.igext as IG
import geni.urn as URN



#
# PhantomNet extensions.
#
import geni.rspec.emulab.pnext as PN

#
# Globals
#
class GLOBALS(object):
    OAI_DS = "urn:publicid:IDN+emulab.net:phantomnet+ltdataset+oai-develop"
    OAI_SIM_DS = "urn:publicid:IDN+emulab.net:phantomnet+dataset+PhantomNet:oai"
    UE_IMG  = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:ANDROID444-STD")
    ADB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-PNTOOLS")
    OAI_EPC_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU16-64-OAIEPC")
    OAI_ENB_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:OAI-Real-Hardware.enb1")
    OAI_SIM_IMG = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:UBUNTU14-64-OAI")
    OAI_SRS_EPC = URN.Image(PN.PNDEFS.PNET_AM, "PhantomNet:srsEPC-OAICN")
    OAI_CONF_SCRIPT = "/usr/bin/sudo /local/repository/bin/config_oai.pl"
    MSIMG = "urn:publicid:IDN+emulab.net+image+PhantomNet:mobilestream-v1"

def connectOAI_DS(node):
    # Create remote read-write clone dataset object bound to OAI dataset
    bs = rspec.RemoteBlockstore("ds-%s" % node.name, "/opt/oai")
    bs.dataset = GLOBALS.OAI_DS
    bs.Site('Core')
    bs.rwclone = True
    # Create link from node to OAI dataset rw clone
    node_if = node.addInterface("dsif_%s" % node.name)
    bslink = rspec.Link("dslink_%s" % node.name)
    bslink.addInterface(node_if)
    bslink.addInterface(bs.interface)
    bslink.vlan_tagging = True
    bslink.best_effort = True  

#
# This geni-lib script is designed to run in the PhantomNet Portal.
#
pc = portal.Context()

#
# Profile parameters.
#
pc.defineParameter("Hardware", "Type of hardware",
                   portal.ParameterType.STRING,"d430",[("d430","d430"),("d710","d710"), ("d820", "d820"), ("pc3000", "pc3000")])


params = pc.bindParameters()
pc.verifyParameters()

rspec = PG.Request()


netmask="255.255.255.0"
oranlink = rspec.Link("oran-lan")

# RIC Machine
ric = rspec.RawPC("ric")
ric.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
ric.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/setup_ric.sh"))
ric.hardware_type = params.Hardware
ric.Site('O-RAN')
iface = ric.addInterface()
iface.addAddress(PG.IPv4Address("192.168.1.1", netmask))
oranlink.addInterface(iface)

# SMO Machine
smo = rspec.RawPC("smo")
smo.disk_image = 'urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU18-64-STD'
smo.addService(PG.Execute(shell="sh", command="/usr/bin/sudo /local/repository/scripts/setup_smo.sh"))
smo.hardware_type = params.Hardware
smo.Site('O-RAN')
iface = smo.addInterface()
iface.addAddress(PG.IPv4Address("192.168.1.2", netmask))
oranlink.addInterface(iface)


tour = IG.Tour()
tour.Description(IG.Tour.TEXT,kube_description)
tour.Instructions(IG.Tour.MARKDOWN,kube_instruction)
rspec.addTour(tour)


oranlink.link_multiplexing = True
oranlink.vlan_tagging = True
oranlink.best_effort = True



#
# Print and go!
#
pc.printRequestRSpec(rspec)
