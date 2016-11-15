import time
import copy
import Protocol as p


alladd = [((0b1101 << 7) | x + 1) for x in range(1, 108)]

class DictDiffer(object):
    """
    Calculate the difference between two dictionaries as:
    (1) items added
    (2) items removed
    (3) keys same in both but changed values
    (4) keys same in both and unchanged values
    """

    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.set_current, self.set_past = set(
            current_dict.keys()), set(
            past_dict.keys())
        self.intersect = self.set_current.intersection(self.set_past)

    def added(self):
        return self.set_current - self.intersect

    def removed(self):
        return self.set_past - self.intersect

    def changed(self):
        return set(o for o in self.intersect if self.past_dict[
                   o] != self.current_dict[o])

    def unchanged(self):
        return set(o for o in self.intersect if self.past_dict[
                   o] == self.current_dict[o])


def w2rAdd(w):
    return (0b1111111 & w) | (0b1101 << 7)


def r2wAdd(r):
    return (0b1111111 & r) | (0b1100 << 7)


def toMod(a):
    return (0b1111111 & a) - 1


def mod2r(m):
    return (m + 1 & 0b1111111) | (0b1101 << 7)


def mod2w(m):
    return (m + 1 & 0b1111111) | (0b1100 << 7)


def mod2chboard(m):
    return ((m - 1) % 4), int((m - 1) / 4)


def chboard2mod(c, b):
    return b * 4 + c + 1


def canID(
        masterID=0b110,
        slaveID=0b0,
        broadcastAnswer=False,
        answer=False,
        verbose=False):
    '''
    Form the can adressing as function of the:
       masterID: is the network ID of the master
       slaveID : is the slave can adress, if set to 0, it will be a broadcast
       isAnswer: is the adress used for a recieve function
       requiersAnswer : is the request expecting answer
    '''
    # Checks
    if slaveID > 0b1111111:
        raise Exception('Invalid slave address, >127')
    if masterID > 0b111:
        raise Exception('Invalid master address, >7')

    # Assign the parameters
    # Deal with broadcasting
    canid = 0b0
    if slaveID == 0b0 and not broadcastAnswer:
        canid = 0b1
    elif slaveID > 0:
        canid = slaveID + 1

    # Deal with slave address
    canid &= 0b1111111

    canid |= (masterID << 8)

    # Is it an answer or request
    if answer:
        canid |= (0b1 << 7)

    if verbose:
        print( bin(canid), hex(canid))

    return canid


def command(
        bus,
        slaveIDs,
        cmdtype,
        canmsg=[],
        waitanswer=True,
        broadcast=False,
        broadcastAnswer=False,
        masterID=0b110,
        verbose=False):
    # type: (object, object, object, object, object, object, object, object, object) -> object

    sendIDs, recieveIDs = [], []
    if broadcast:
        sendIDs.append(
            canID(
                masterID=masterID,
                slaveID=0b0,
                broadcastAnswer=broadcastAnswer,
                verbose=verbose))
    else:
        for slaveID in slaveIDs:
            sendIDs.append(
                canID(
                    masterID=masterID,
                    slaveID=slaveID,
                    broadcastAnswer=broadcastAnswer,
                    verbose=verbose))
    if broadcastAnswer and broadcast:
        recieveIDs.append([canID(masterID=masterID,
                                 slaveID=slaveID,
                                 answer=True,
                                 verbose=verbose) for slaveID in slaveIDs])
    if not broadcast:
        for slaveID in slaveIDs:
            recieveIDs.append(
                canID(
                    masterID=masterID,
                    slaveID=slaveID,
                    broadcastAnswer=broadcastAnswer,
                    answer=True,
                    verbose=verbose))

    msgID = None
    if cmdtype == 'Abort':
        msgID = 0x00
    elif cmdtype == 'SetCANAddress':
        msgID = 0x01
    elif cmdtype == 'SetDACLevel':
        msgID = 0x02
    elif cmdtype == 'SetLED':
        msgID = 0x03
    elif cmdtype == 'GetLEDandDAC':
        msgID = 0x04
    elif cmdtype == 'GetVersion':
        msgID = 0x1E
    else:
        raise Exception('Invalid command type' + cmdtype)

    r = []
    for sendID in sendIDs:
        # if msgID==0x02: print 'In command...', sendIDs,msgID,canmsg
        s = None
        if 1==0 : #isinstance(bus, 'CANBus'):
            if len(canmsg) == 0:
                s = bus.send(0, sendID, msgID, verbose=4 if verbose else 0)
            elif len(canmsg) == 1:
                s = bus.send(
                    0,
                    sendID,
                    msgID,
                    canmsg[0],
                    verbose=4 if verbose else 0)
            elif len(canmsg) == 2:
                s = bus.send(
                    0,
                    sendID,
                    msgID,
                    canmsg[0],
                    canmsg[1],
                    verbose=4 if verbose else 0)
            elif len(canmsg) == 3:
                s = bus.send(
                    0,
                    sendID,
                    msgID,
                    canmsg[0],
                    canmsg[1],
                    canmsg[2],
                    verbose=4 if verbose else 0)
            elif len(canmsg) == 4:
                s = bus.send(
                    0,
                    sendID,
                    msgID,
                    canmsg[0],
                    canmsg[1],
                    canmsg[2],
                    canmsg[3],
                    verbose=4 if verbose else 0)
            else:
                print ('Too much commands!!!!!!')
                raise Exception('Too much commands')
        else:
            if len(canmsg) == 0:
                s = bus.query_request(
                    1, sendID, msgID, verbose=4 if verbose else 0)
            elif len(canmsg) == 1:
                s = bus.query_request(
                    1, sendID, msgID, canmsg[0], verbose=4 if verbose else 0)
            elif len(canmsg) == 2:
                s = bus.query_request(1, sendID, msgID, canmsg[0], canmsg[
                                      1], verbose=4 if verbose else 0)
            elif len(canmsg) == 3:
                s = bus.query_request(1, sendID, msgID, canmsg[0], canmsg[
                                      1], canmsg[2], verbose=4 if verbose else 0)
            elif len(canmsg) == 4:
                s = bus.query_request(1, sendID, msgID, canmsg[0], canmsg[1], canmsg[
                                      2], canmsg[3], verbose=4 if verbose else 0)
            else:
                print ('Too much commands!!!!!!')
                raise Exception('Too much commands')
        if s != 0:
            raise Exception('Could not send', sendID, msgID, msg)
    if waitanswer:
        # print '================= Answer expected'
        for recieveID in recieveIDs:
            resp = None
            if 1==0:#isinstance(bus, 'CANBus'):
                resp = bus.receive(
                    0,
                    recieveID,
                    verbose=4 if verbose else 0,
                    only_data=True)
            else:
                # print recieveID
                resp = bus.receive_answer(
                    1, recieveID, verbose=4 if verbose else 0)
            r.append(resp)
            if verbose:
                print (r[-1])
    return r


def setAddress(bus, origAdd, modnum):
    bus.bus.send(0, origAdd, 0x01, 0x00, 0x07)
    bus.bus.send(0, origAdd, 0x01, 0x01, modnum)
    time.sleep(1)
    r = bus.bus.receive(0, alladd, verbose=False, only_data=True)
    if len(r.keys()) == 0:
        print ('Failed to change the address')
        r = bus.bus.receive(0, [w2rAdd(origAdd)],
                            verbose=False, only_data=True)
        if len(r.keys()) == 0:
            'Or not??? investigate manually'


def setBoardAddresses(bus, boardnum):
    # first get the adresses
    bus.bus.send(0, 0x600, 0x1E)
    time.sleep(1.)
    theadd = bus.bus.receive(0, alladd, only_data=True)
    theadd = sorted(theadd.keys())
    print ('Original adresses:', theadd)
    # Then set new addresses
    for add in theadd:
        setAddress(bus, r2wAdd(add), boardnum * 4 + 1)
    time.sleep(2)
    bus.bus.send(0, 0x600, 0x1E)
    time.sleep(2)
    theadd = bus.bus.receive(0, alladd, only_data=True)
    theadd = theadd.keys()
    print ('New adresses:', theadd)
    print ('Module:',)
    for a in theadd:
        print (toMod(a),)
    print ('')


def updateStatus(bus, statusdict):
    # Get the LED status
    statusdict.update(checkLEDStatus(bus))
    # Get the LED level
    statusdict.update(checkLEDLevel(bus))


def checkModules(bus):
    # Send a broadcast to get the version and see who is responding
    print ('Get the modules list...')
    res = command(
        bus,
        range(
            1,
            45),
        'GetVersion',
        broadcast=True,
        broadcastAnswer=True,
        verbose=False,
        waitanswer=True)
    modules = sorted(res[0].keys())
    modList = []
    for k in res[0].keys():
        modList.append(toMod(k))
    return {'ModuleList': modList}


def checkLEDStatus(bus, module=None, verbose=False):
    print ('Get AC and DC Status...')
    res = None
    if not module:
        res = command(
            bus,
            range(
                1,
                45),
            'GetLEDandDAC',
            [0x00],
            broadcast=True,
            broadcastAnswer=True,
            verbose=False,
            waitanswer=True)
    else:
        res = command(bus, [module], 'GetLEDandDAC', [0x00], waitanswer=True)
    res = res[0]
    # check the response is the expected code:
    for k in res.keys():
        goodcode = False
        for result in res[k]:
            if result[0] == 0x04:
                goodcode = True
        if not goodcode:
            raise Exception('Answer code not aligned with request...')
    modules = sorted(res.keys())
    resdict = {}
    # Get the information per modules
    for k in res.keys():
        # Get the DC LED status
        resdict['M_' +
                str(toMod(k)) +
                '_DCDC_Status'] = 'OFF' if res[k][0][4] == 0 else 'ON'
        resdict['M_' + str(toMod(k)) + '_ACLED_Status'] = []
        acstat = res[k][0][1] << 16 | res[k][0][2] << 8 | res[k][0][3]
        # Get the AC LED status
        for x in range(24):
            if ((1 << x) & acstat) >> x == 1:
                resdict['M_' + str(toMod(k)) + '_ACLED_Status'].append('ON')
            else:
                resdict['M_' + str(toMod(k)) + '_ACLED_Status'].append('OFF')
    if verbose:
        print ('=================== LED STATUS =======================')
        for k in res.keys():
            print ('| Module: ', toMod(k), 'DCDC convertor', resdict['M_' + str(toMod(k)) + '_DCDC_Status'], '| AC LED (0-23)', resdict['M_' + str(toMod(k)) + '_ACLED_Status'])
        print ('')
    return resdict


def checkLEDLevel(bus, module=None, verbose=False):
    print ('Get the AC led level...')
    res = None
    if not module:
        res = command(
            bus,
            range(
                1,
                45),
            'GetLEDandDAC',
            [0x01],
            broadcast=True,
            broadcastAnswer=True,
            verbose=False,
            waitanswer=True)
    else:
        res = command(bus, [module], 'GetLEDandDAC', [0x01], waitanswer=True)
    res = res[0]
    # check the response is the expected code:
    for k in res.keys():
        goodcode = False
        for result in res[k]:
            if result[0] == 0x04:
                goodcode = True
        if not goodcode:
            raise Exception('Answer code not aligned with request...')
    print ('Get AC and DC levels')
    modules = sorted(res.keys())
    resdict = {}
    # Get the information per modules
    for k in res.keys():
        # Get the DC LED status
        channels = [(res[k][0][1] << 8) | res[k][0][2],
                    (res[k][0][3] << 8) | res[k][0][4],
                    (res[k][0][5] << 8) | res[k][0][6],
                    (res[k][1][1] << 8) | res[k][1][2],
                    (res[k][1][3] << 8) | res[k][1][4],
                    (res[k][1][5] << 8) | res[k][1][6],
                    (res[k][2][1] << 8) | res[k][2][2],
                    (res[k][2][3] << 8) | res[k][2][4],
                    (res[k][2][5] << 8) | res[k][2][6]]
        for i, ch in enumerate(channels):
            resdict['M_' + str(toMod(k)) + '_ACLED_Ch_' + str(i)] = ch
    if verbose:
        print ('=================== LED STATUS =======================')
        for k in res.keys():
            print ('|-----> Module:', str(toMod(k)),)
            for ch in range(8):
                print ('| Ch:', ch, '-', resdict['M_' + str(toMod(k)) + '_ACLED_Ch_' + str(ch)],)
            print ('')
    return resdict


def setDACLevel(
        bus,
        level,
        module=None,
        channel=None,
        verbose=False,
        waitanswer=True):
    '''
    Change the DAC led level

    bus: the CAN bus (type Protocole)
    level : the required level
    module :  None will broadcast to all module (AC and DC)
              a module value will send to this module only (0 and 2 are for AC, 1 and 3 for DC)
    channel : None will set the same level to all channel (AC and DC)
              a channel will set the level to this channel (note that for DC only channel 0x0 is available)
    '''
    if verbose:
        print ('Set the DAC led level...')
    res = None
    tmp_cmd = 0x8
    # print level
    level &= 0x3FF
    level_LSB = level & 0xFF
    level_MSB = (level & 0x300) >> 8
    # print level_LSB,level_MSB
    # print level,(level_MSB << 8) | level_LSB

    if channel is not None:
        tmp_cmd = channel
    if not module:
        # Set a single value everywhere
        if tmp_cmd == 8:
            # First broadcast on channel 0 such that the module for DC gets set
            res = command(bus, range(1, 45), 'SetDACLevel', [
                          0x0, level_MSB, level_LSB], broadcast=True, verbose=verbose)
            #res = command( bus, range(1,45) , 'SetDACLevel', [0x0,level], broadcast=True, verbose= verbose)
            # Then broadcast on channel 8 such that all the module for AC gets
            # set
            res = command(
                bus, range(
                    1, 45), 'SetDACLevel', [
                    tmp_cmd, level_MSB, level_LSB], broadcast=True, verbose=verbose)
            #res = command( bus, range(1,45) , 'SetDACLevel', [tmp_cmd,level], broadcast=True, verbose= verbose)
        else:
            res = command(
                bus, range(
                    1, 45), 'SetDACLevel', [
                    tmp_cmd, level_MSB, level_LSB], broadcast=True, verbose=verbose)
            #res = command( bus, range(1,45) , 'SetDACLevel', [tmp_cmd,level], broadcast=True, verbose= verbose)
    else:
        # print 'module',module,'channel',tmp_cmd,'level',(level_MSB << 8) |
        # level_LSB,level_MSB,level_LSB
        res = command(
            bus, [module], 'SetDACLevel', [
                tmp_cmd, level_MSB, level_LSB], verbose=verbose, waitanswer=waitanswer)
        #res = command( bus, [module] , 'SetDACLevel', [tmp_cmd,level], verbose= verbose)
        # print "resout: ",res
    if module and waitanswer:
        if res[0][mod2r(module)][0][0] != 2:
            raise Exception('Answer not of the same command type')
        if res[0][mod2r(module)][0][1] != 0:
            raise Exception(
                'Error in setting the DAC level', res[0][
                    mod2r(module)][1])


def setLED(
        bus,
        module=None,
        led=None,
        globalCmd=None,
        verbose=False,
        waitanswer=True):
    if verbose:
        print ('Set the LED ON/OFF...')
        print ('Set the LED ON/OFF...')
    res = None
    led_LSB = led & 0xFF
    led_MSB = (led & 0xFF00) >> 8
    led_HSB = (led & 0xFF0000) >> 16
    if not module:
        # Then broadcast on channel 8 such that all the module for AC gets set
        if globalCmd is None:
            res = command(
                bus, range(
                    1, 45), 'SetLED', [
                    led_HSB, led_MSB, led_LSB, False], broadcast=True)
        else:
            res = command(
                bus, range(
                    1, 45), 'SetLED', [
                    led_HSB, led_MSB, led_LSB, globalCmd], broadcast=True)
    else:
        # print
        # module,bin(led_HSB),bin(led_MSB),bin(led_LSB),globalCmd,bin(led)
        if globalCmd is None:
            res = command(
                bus, [module], 'SetLED', [
                    led_HSB, led_MSB, led_LSB, False], waitanswer=waitanswer)
        else:
            res = command(
                bus, [module], 'SetLED', [
                    led_HSB, led_MSB, led_LSB, globalCmd], waitanswer=waitanswer)

    if module and waitanswer:
        if len(res[0][mod2r(module)]) == 1:
            if res[0][mod2r(module)][0][0] != 3:
                raise Exception('Answer not of the same command type')
            if res[0][mod2r(module)][0][1] != 0 and globalCmd is None:
                raise Exception(
                    'Error in setting the LED', res[0][
                        mod2r(module)])
        else:
            if res[0][mod2r(module)][0] != 3:
                raise Exception('Answer not of the same command type')
            if res[0][mod2r(module)][1] != 0 and globalCmd is None:
                raise Exception(
                    'Error in setting the LED', res[0][
                        mod2r(module)])


def flushAnswer(bus, verbose=False):
    resp = bus.receive_answer(1, alladd, verbose=4 if verbose else 0)


def resetAll(bus, status_dict, cmd_dict):
    updateStatus(bus, status_dict)
    for k in cmd_dict.keys():
        if k.count('ACLED_Ch') > 0.5:
            cmd_dict[k] = 0
        elif k.count('DCDC') > 0.5:
            cmd_dict[k] = 'OFF'
        elif k.count('ACLED_Status') > 0.5:
            cmd_dict[k] = ['OFF'] * 24
    diffK = DictDiffer(status_dict, cmd_dict)
    applyDict(bus, status_dict, cmd_dict)


def initialise_can(cts):
    # First open the device

    cts.bus = p.BusProtocol(lib='USB-to-CANV2 compact')
    cts.canstatus = 0
    try:
        cts.bus.open_all()
        cts.canstatus = 1
    except SystemExit as e:
        if e.code == 137:
            cts.connected = False
            return
        else:
            raise
    cts.bus.start_all()
    cts.canstatus = 2
    # Make sure at least one command has been send (for some reason the
    # first does not always reply)
    res = command(
        cts.bus,
        [1],
        'GetVersion',
        broadcast=True,
        broadcastAnswer=True,
        verbose=False)
    return

