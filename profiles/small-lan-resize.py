"""Variable number of nodes in a lan. You have the option of picking from one
of several standard images we provide, or just use the default (typically a recent
version of Ubuntu). You may also optionally pick the specific hardware type for
all the nodes in the lan.

Instructions:
Wait for the experiment to start, and then log into one or more of the nodes
by clicking on them in the toplogy, and choosing the `shell` menu option.
Use `sudo` to run root commands.
"""

# Import the Portal object.
import geni.portal as portal
# Import the ProtoGENI library.
import geni.rspec.pg as pg
# Emulab specific extensions.
import geni.rspec.emulab as emulab

# Create a portal context, needed to defined parameters
pc = portal.Context()

# Create a Request object to start building the RSpec.
request = pc.makeRequestRSpec()

# Variable number of nodes.
pc.defineParameter("nodeCount", "Number of Nodes", portal.ParameterType.INTEGER, 1,
                   longDescription="If you specify more then one node, " +
                                   "we will create a lan for you.")

# Pick your OS.
imageList = [
    ('default', 'Default Image'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU22-64-STD', 'UBUNTU 22.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU20-64-STD', 'UBUNTU 20.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//UBUNTU18-64-STD', 'UBUNTU 18.04'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//CENTOS8S-64-STD', 'CENTOS 8 Stream'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD133-64-STD', 'FreeBSD 13.3'),
    ('urn:publicid:IDN+emulab.net+image+emulab-ops//FBSD141-64-STD', 'FreeBSD 14.1')]

pc.defineParameter("osImage", "Select OS image",
                   portal.ParameterType.IMAGE,
                   imageList[0], imageList,
                   longDescription="Most clusters have this set of images, " +
                                   "pick your favorite one.")

# Optional physical type for all nodes.
pc.defineParameter("phystype", "Optional physical node type",
                   portal.ParameterType.NODETYPE, "",
                   longDescription="Pick a single physical node type (pc3000,d710,etc) " +
                                   "instead of letting the resource mapper choose for you.")

# Optionally create XEN VMs instead of allocating bare metal nodes.
pc.defineParameter("useVMs", "Use XEN VMs",
                   portal.ParameterType.BOOLEAN, False,
                   longDescription="Create XEN VMs instead of allocating bare metal nodes.")

# Optionally start X11 VNC server.
pc.defineParameter("startVNC", "Start X11 VNC on your nodes",
                   portal.ParameterType.BOOLEAN, False,
                   longDescription="Start X11 VNC server on your nodes. There will be " +
                                   "a menu option in the node context menu to start a browser based VNC " +
                                   "client. Works really well, give it a try!")

# Optional link speed, normally the resource mapper will choose for you based on node availability
pc.defineParameter("linkSpeed", "Link Speed", portal.ParameterType.INTEGER, 0,
                   [(0, "Any"), (100000, "100Mb/s"), (1000000, "1Gb/s"), (10000000, "10Gb/s"), (25000000, "25Gb/s"),
                    (100000000, "100Gb/s")],
                   advanced=True,
                   longDescription="A specific link speed to use for your lan. Normally the resource " +
                                   "mapper will choose for you based on node availability and the optional physical type.")

# For very large lans you might to tell the resource mapper to override the bandwidth constraints
# and treat it a "best-effort"
pc.defineParameter("bestEffort", "Best Effort", portal.ParameterType.BOOLEAN, False,
                   advanced=True,
                   longDescription="For very large lans, you might get an error saying 'not enough bandwidth.' " +
                                   "This options tells the resource mapper to ignore bandwidth and assume you know what you " +
                                   "are doing, just give me the lan I ask for (if enough nodes are available).")

# Sometimes you want all of nodes on the same switch, Note that this option can make it impossible
# for your experiment to map.
pc.defineParameter("sameSwitch", "No Interswitch Links", portal.ParameterType.BOOLEAN, False,
                   advanced=True,
                   longDescription="Sometimes you want all the nodes connected to the same switch. " +
                                   "This option will ask the resource mapper to do that, although it might make " +
                                   "it imppossible to find a solution. Do not use this unless you are sure you need it!")

# Optional ephemeral blockstore
pc.defineParameter("tempFileSystemSize", "Temporary Filesystem Size",
                   portal.ParameterType.INTEGER, 0, advanced=True,
                   longDescription="The size in GB of a temporary file system to mount on each of your " +
                                   "nodes. Temporary means that they are deleted when your experiment is terminated. " +
                                   "The images provided by the system have small root partitions, so use this option " +
                                   "if you expect you will need more space to build your software packages or store " +
                                   "temporary files.")

# Instead of a size, ask for all available space.
pc.defineParameter("tempFileSystemMax", "Temp Filesystem Max Space",
                   portal.ParameterType.BOOLEAN, False,
                   advanced=True,
                   longDescription="Instead of specifying a size for your temporary filesystem, " +
                                   "check this box to allocate all available disk space. Leave the size above as zero.")

pc.defineParameter("tempFileSystemMount", "Temporary Filesystem Mount Point",
                   portal.ParameterType.STRING, "/mydata", advanced=True,
                   longDescription="Mount the temporary file system at this mount point; in general you " +
                                   "you do not need to change this, but we provide the option just in case your software " +
                                   "is finicky.")

pc.defineParameter("exclusiveVMs", "Force use of exclusive VMs",
                   portal.ParameterType.BOOLEAN, True,
                   advanced=True,
                   longDescription="When True and useVMs is specified, setting this will force allocation " +
                                   "of exclusive VMs. When False, VMs may be shared or exclusive depending on the policy " +
                                   "of the cluster.")

pc.defineParameter("growRoot", "Grow the root partition",
                   portal.ParameterType.BOOLEAN, True,
                   longDescription="Grow the root partition to fill the disk")

pc.defineParameter("addSwap", "Add swap space",
                   portal.ParameterType.BOOLEAN, True,
                   longDescription="Add swap space to the VMs, if there is already a swap partition, " +
                                   "it will be resized to the specified size. " +
                                   "In any case, this partition will be at the end of the device")

pc.defineParameter("swapSize", "Swap size to add or resize",
                   portal.ParameterType.INTEGER, 8,
                   longDescription="Size in GB of the swap partition to add or resize")

pc.defineParameter("swapPartition", "Swap partition to use",
                   portal.ParameterType.STRING, "", advanced=True,
                   longDescription="The partition to use for the swap space, if empty, the script will try to find " +
                                    "a suitable partition, should be given in the format /dev/sdXN or /dev/nvme0nXpN")

# Retrieve the values the user specifies during instantiation.
params = pc.bindParameters()

# Check parameter validity.
if params.nodeCount < 1:
    pc.reportError(portal.ParameterError("You must choose at least 1 node.", ["nodeCount"]))

if params.tempFileSystemSize < 0 or params.tempFileSystemSize > 200:
    pc.reportError(portal.ParameterError("Please specify a size greater then zero and " +
                                         "less then 200GB", ["tempFileSystemSize"]))

if params.phystype != "":
    tokens = params.phystype.split(",")
    if len(tokens) != 1:
        pc.reportError(portal.ParameterError("Only a single type is allowed", ["phystype"]))

if params.swapSize < 0:
    pc.reportError(portal.ParameterError("Please specify a size greater then or equal zero", ["swapSize"]))

pc.verifyParameters()

# Create link/lan.
if params.nodeCount > 1:
    if params.nodeCount == 2:
        lan = request.Link()
    else:
        lan = request.LAN()
        pass
    if params.bestEffort:
        lan.best_effort = True
    elif params.linkSpeed > 0:
        lan.bandwidth = params.linkSpeed
    if params.sameSwitch:
        lan.setNoInterSwitchLinks()
    pass

# args
add_swap = "--no-swap" if not params.addSwap else ""
swap_size = "--new-swap-size " + str(params.swapSize) if params.swapSize >= 0 else ""
swap_partition = "--swap-part " + params.swapPartition if params.swapPartition != "" else ""
move_swap = "sudo /local/move_swap.sh " + add_swap + " " + swap_size + " " + swap_partition

# Process nodes, adding to link or lan.
for i in range(params.nodeCount):
    # Create a node and add it to the request
    if params.useVMs:
        name = "vm" + str(i)
        node = request.XenVM(name)
        node.addService(pg.Execute(shell="sh",
                                   command="sudo wget -O /local/move_swap.sh https://raw.githubusercontent.com/dakaidan/cloudlab-configs/refs/heads/main/scripts/move_swap.sh"))
        node.addService(pg.Execute(shell="sh", command="chmod +x /local/move_swap.sh"))
        node.addService(
            pg.Execute(shell="sh", command=move_swap))
        if params.growRoot:
            node.addService(pg.Execute(shell="sh",
                                       command="sudo wget -O /local/grow_root.sh https://raw.githubusercontent.com/dakaidan/cloudlab-configs/refs/heads/main/scripts/grow_root.sh"))
            node.addService(pg.Execute(shell="sh", command="chmod +x /local/grow_root.sh"))
            node.addService(pg.Execute(shell="sh", command="sudo /local/grow_root.sh"))
        if params.exclusiveVMs:
            node.exclusive = True
            pass
    else:
        name = "node" + str(i)
        node = request.RawPC(name)
        node.addService(pg.Execute(shell="sh",
                                   command="sudo wget -O /local/move_swap.sh https://raw.githubusercontent.com/dakaidan/cloudlab-configs/main/scripts/move_swap.sh"))
        node.addService(pg.Execute(shell="sh", command="sudo chmod +x /local/move_swap.sh"))
        node.addService(
            pg.Execute(shell="sh", command=move_swap))
        if params.growRoot:
            node.addService(pg.Execute(shell="sh",
                                       command="sudo wget -O /local/grow_root.sh https://raw.githubusercontent.com/dakaidan/cloudlab-configs/refs/heads/main/scripts/grow_root.sh"))
            node.addService(pg.Execute(shell="sh", command="sudo chmod +x /local/grow_root.sh"))
            node.addService(pg.Execute(shell="sh", command="sudo /local/grow_root.sh"))
        pass
    if params.osImage and params.osImage != "default":
        node.disk_image = params.osImage
        pass
    # Add to lan
    if params.nodeCount > 1:
        iface = node.addInterface("eth1")
        lan.addInterface(iface)
        pass
    # Optional hardware type.
    if params.phystype != "":
        node.hardware_type = params.phystype
        pass
    # Optional Blockstore
    if params.tempFileSystemSize > 0 or params.tempFileSystemMax:
        bs = node.Blockstore(name + "-bs", params.tempFileSystemMount)
        if params.tempFileSystemMax:
            bs.size = "0GB"
        else:
            bs.size = str(params.tempFileSystemSize) + "GB"
            pass
        bs.placement = "any"
        pass
    #
    # Install and start X11 VNC. Calling this informs the Portal that you want a VNC
    # option in the node context menu to create a browser VNC client.
    #
    # If you prefer to start the VNC server yourself (on port 5901) then add nostart=True.
    #
    if params.startVNC:
        node.startVNC()
        pass
    pass


# Print the RSpec to the enclosing page.
pc.printRequestRSpec(request)