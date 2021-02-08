import uasyncio as asyncio
import machine
from pn532 import PN532Uart

# This example initializes the PN532 and then enters a forever loop
# waiting for rfid tags to be read.
#
# Pinout:
#      esp32 tx = 22 = pn532 rx
#      esp32 rx = 23 = pn532 tx
#
#      esp32 OUT = 21 = buzzer (or led)
#

# Enable debug printing here:
DEBUG = False


async def test():
    buzzer = machine.Pin(21, machine.Pin.OUT)
    buzzer.off()

    # NOTE: on several of the esp32-wrover dev boards, the default uart2 pins
    #       conflict with the psRam so the pn532 is plugged into two unused
    #       pins instead.
    rf = PN532Uart(2, tx=22, rx=23, debug=DEBUG)
    await rf.SAM_configuration()

    ic, ver, rev, support = await rf.get_firmware_version()
    print('Found PN532 with firmware version: {0}.{1}'.format(ver, rev))

    while True:
        try:
            uid = await asyncio.wait_for(rf.read_passive_target(), timeout=1.0)
            print("Card UUID: ", [hex(i) for i in uid])
            buzzer.on()
            await asyncio.sleep(0.2)
            buzzer.off()
        except asyncio.TimeoutError:
            # NOTE: This is important to stop the reader from reporting cards after
            #       we are no longer waiting.
            await rf.release_targets()
            print('timeout!')


loop = asyncio.get_event_loop()
loop.create_task(test())
loop.run_forever()
