# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#         ported for Micropython ESP8266 by Cefn Hoile
#         modified by STECRZ for only
#         (e.g. pin validation and MCP23007 removed to reduce code)
# Documentation: see original code


_IODIR = 0x00
_GPIO = 0x12
_GPPU = 0x0C

_GPIO_BYTES = 2  # 16 pins


class MCP23017:
    def __init__(self, i2c, address=0x20, def_inp=True, def_val=0):
        # def_inp: True = by default all directions are inputs, False = - " - outputs
        # def_val (if not def_inp): 1 = by default pullups are enabled and outputs set to HIGH, 0 = outputs are LOW
        self.address = address
        self._i2c = i2c

        # Buffer register values so they can be changed without reading.
        self._iodir = bytearray([def_inp * 0xFF] * _GPIO_BYTES)  # default: all directions are outputs?
        self._gppu = bytearray([def_val * 0xFF] * _GPIO_BYTES)   # default: all pullups enabled?
        self._gpio = bytearray([def_val * 0xFF] * _GPIO_BYTES)   # default: all outputs high?

        # write current direction and pullup buffer state:
        self.write_iodir()
        self.write_gppu()

    def decl_output(self, pin):  # declare pin <pin> as an output
        self._iodir[int(pin / 8)] &= ~(1 << (int(pin % 8)))
        self.write_iodir()

    def decl_input(self, pin):  # declare pin <pin> as an input
        self._iodir[int(pin / 8)] |= 1 << (int(pin % 8))
        self.write_iodir()

    def output(self, pin, value):  # turns output <pin> on/off depending on <value>
        self.output_pins({pin: value})

    def output_pins(self, pins):  # like output, but multiple pins
        for pin, value in iter(pins.items()):
            if value:
                self._gpio[int(pin / 8)] |= 1 << (int(pin % 8))
            else:
                self._gpio[int(pin / 8)] &= ~(1 << (int(pin % 8)))
        self.write_gpio()

    def input(self, pin, read=True):  # read the specified pin and return True if the pin is HIGH
        return self.input_pins([pin], read)[0]

    def input_pins(self, pins, read=True):  # like input, but multiple pins
        if read:
            self.read_gpio()  # get GPIO state
        # return True if pin's bit is set
        return [(self._gpio[int(pin / 8)] & 1 << (int(pin % 8))) > 0 for pin in pins]

    def pullup(self, pin, enabled):  # turn on/off pullup resistor for <pin>
        if enabled:
            self._gppu[int(pin / 8)] |= 1 << (int(pin % 8))
        else:
            self._gppu[int(pin / 8)] &= ~(1 << (int(pin % 8)))
        self.write_gppu()

    def _write_list(self, register, data):
        return self._i2c.writeto_mem(self.address, register, data)

    def _read_list(self, register, length):
        return self._i2c.readfrom_mem(self.address, register, length)

    def read_gpio(self):
        self._gpio[:] = self._read_list(_GPIO, _GPIO_BYTES)

    def write_gpio(self, gpio=None):  # write value <gpio> to the GPIO register (no value = current buffered)
        if gpio is not None:
            self._gpio = gpio
        self._write_list(_GPIO, self._gpio)

    def write_iodir(self, iodir=None):  # write value <iodir> to IODIR register (no value = current buffered value)
        if iodir is not None:
            self._iodir = iodir
        self._write_list(_IODIR, self._iodir)

    def write_gppu(self, gppu=None):  # write value <gppu> to the GPPU register (no value = current buffered)
        if gppu is not None:
            self._gppu = gppu
        self._write_list(_GPPU, self._gppu)
