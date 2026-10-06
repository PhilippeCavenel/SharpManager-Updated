#!/usr/bin/env python3
"""Build with Arduino AVR core 1.8.6 and avr-gcc 7.3.0 Arduino7.
Usage: python BuildProMiniFirmware.py CORE_DIRECTORY COMPILER_DIRECTORY
Builds sketch only, for ATmega328P / 5 V / 16 MHz. Does not replace bootloader.
"""
import pathlib, subprocess, sys, tempfile

root = pathlib.Path(__file__).resolve().parent
core_root, compiler_root = map(pathlib.Path, sys.argv[1:3])
core = core_root / 'cores/arduino'
variant = core_root / 'variants/eightanaloginputs'
sketch = root / 'Arduino'
def tool(name):
    return str(compiler_root / 'bin' / ('avr-' + name))
def run(args):
    subprocess.run(args, check=True)
flags = ['-Os', '-flto', '-ffunction-sections', '-fdata-sections', '-mmcu=atmega328p',
         '-DF_CPU=16000000L', '-DARDUINO=10819', '-DARDUINO_AVR_PRO', '-DARDUINO_ARCH_AVR',
         '-I'+str(core), '-I'+str(variant), '-I'+str(sketch)]
cxx = ['-std=gnu++11', '-fpermissive', '-fno-exceptions', '-fno-threadsafe-statics', '-Wno-error=narrowing']
with tempfile.TemporaryDirectory(prefix='sharp-firmware-') as folder:
    build = pathlib.Path(folder)
    source = build / 'Sketch.cpp'
    source.write_text('#include <Arduino.h>\n' + '\n'.join(
        (sketch / name).read_text() for name in ['Arduino.ino', 'Manager.ino', 'Sharp.ino', 'Tape.ino']))
    objects = []
    for file in sorted(core.iterdir()):
        if file.suffix not in ['.cpp', '.c', '.S']:
            continue
        obj = build / (file.name + '.o')
        extra = cxx if file.suffix == '.cpp' else ['-std=gnu11'] if file.suffix == '.c' else ['-x', 'assembler-with-cpp']
        run([tool('g++' if file.suffix == '.cpp' else 'gcc'), *flags, *extra, '-c', str(file), '-o', str(obj)])
        objects.append(str(obj))
    archive = build / 'core.a'
    run([tool('gcc-ar'), 'rcs', str(archive), *objects])
    obj = build / 'Sketch.o'
    run([tool('g++'), *flags, *cxx, '-c', str(source), '-o', str(obj)])
    elf = build / 'ProMiniSync2s.elf'
    run([tool('g++'), '-Os', '-flto', '-fuse-linker-plugin', '-Wl,--gc-sections', '-mmcu=atmega328p',
         '-o', str(elf), str(obj), str(archive), '-lm'])
    output = root / 'Desktop/SharpManager.Common/Firmware/ProMiniSync2s.hex'
    run([tool('objcopy'), '-O', 'ihex', '-R', '.eeprom', str(elf), str(output)])
    run([tool('size'), str(elf)])
    print('Firmware:', output)
