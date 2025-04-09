# SMAZ for MicroPython

An optimized implementation of the SMAZ compression algorithm adapted for MicroPython.

## Description

SMAZ is a simple compression algorithm specifically designed for compressing short text strings. This implementation has been optimized to work efficiently in MicroPython environments, where resources are limited.

The library is adapted from the Python port by Max Smith and based on the original SMAZ implementation by Salvatore Sanfilippo.

## Features

- Optimized for resource-constrained devices running MicroPython
- Highly efficient for compressing short ASCII texts
- Modular and easy-to-use implementation
- Automatic verification to avoid expansion when compression is not advantageous
- Singleton pattern for efficient memory usage

## Installation

Simply copy the `smaz.py` file into your project or into your MicroPython device's library directory.

```python
# If you're using tools like ampy, you can upload the file like this:
$ ampy --port /dev/ttyUSB0 put smaz.py
```

## Usage

```python
from smaz import get_instance as sz

SZ= sz()
# Compress a string
original_text = "Hello World!"
compressed_text = sz.compress(original_text)

# Decompress
decompressed_text = sz.decompress(compressed_text)

# You can also create your own instance
compressor = sz.Smaz()
result = compressor.compress("This is another text")
```

### Complete Example

```python
from smaz import get_instance as sz

SZ= sz()
# Basic usage example
text = "This is a text string that we will compress with SMAZ"
compressed = sz.compress(text)
decompressed = sz.decompress(compressed)

print("Original ({} bytes): {}".format(len(text), text))
print("Compressed ({} bytes)".format(len(compressed)))
print("Compression ratio: {:.2f}%".format(len(compressed)/len(text) * 100))
print("Decompressed: {}".format(decompressed))
```

## Test

The library includes a test function that you can run to verify its operation:

```python
# main_test.py
from smaz import get_instance as sz

SZ= sz()
test_strings = [
        "This is a small string",
        "foobar",
        "the end",
        "Hello World!",
        "http://micropython.org",
        '''A veces, una palabra escrita a tiempo vale mas que mil pensamientos no dichos. Hoy es un buen dia para comenzar algo nuevo, aunque sea con solo una linea.'''
    ]
    
for s in test_strings:
    try:
        compressed = SZ.compress(s)
        decompressed = SZ.decompress(compressed)
            
        print("Original ({0} bytes): {1}".format(len(s), s))
            
        # Usar representación hexadecimal para mostrar caracteres no imprimibles
        hex_repr = "".join("\\x{:02x}".format(ord(c)) for c in compressed)
        print("Comprimido ({0} bytes): {1}".format(len(compressed), hex_repr))
            
        print("Descomprimido: {0}".format(decompressed))
        print("Ratio de compresión: {0:.2f}%".format(len(compressed)/len(s)))
        print()
            
        # Verificar si la descompresión tuvo éxito
        if decompressed != s:
            print("ERROR: ¡La descompresión no coincide con el original!")
    except Exception as e:
        print("Error con cadena '{0}': {1}".format(s, str(e)))

''' output:
Original (22 bytes): This is a small string
Comprimido (11 bytes): \xfe\x54\x4c\x38\xac\x3e\xad\x98\x3e\xc3\x46
Descomprimido: This is a small string
Ratio de compresión: 0.50

Original (6 bytes): foobar
Comprimido (4 bytes): \xdc\x06\x5a\x4f
Descomprimido: foobar
Ratio de compresión: 0.67

Original (7 bytes): the end
Comprimido (3 bytes): \x01\xab\x3d
Descomprimido: the end
Ratio de compresión: 0.43

Original (12 bytes): Hello World!
Comprimido (12 bytes): \xfe\x48\xb2\x16\x60\xfe\x57\x2a\x16\x18\xfe\x21
Descomprimido: Hello World!
Ratio de compresión: 1.00

Original (22 bytes): http://micropython.org
Comprimido (11 bytes): \x43\x2d\x83\x73\x3c\x53\x11\x1f\x6e\x2a\x3b
Descomprimido: http://micropython.org
Ratio de compresión: 0.50

Original (154 bytes): A veces, una palabra escrita a tiempo vale mas que mil pensamientos no dichos. Hoy es un buen dia para comenzar algo nuevo, aunque sea con solo una linea.
Comprimido (95 bytes): \xfe\x41\x00\x6f\x88\x85\xe0\xa3\x3c\x58\x04\x5a\x82\xab\x0a\x1c\x72\xc8\x92\x4a\x02\x2d\x3c\x60\x6d\x58\x0b\xad\x17\xfe\x71\x26\x0b\x2d\xf0\x7d\x33\x0a\x04\x2d\x08\x61\x06\x17\xb7\xa5\x83\xbb\x0a\x79\xfe\x48\x06\x47\x7e\xe0\x5e\x26\xcf\x81\xa3\x3c\x4f\xa3\x75\xfc\xdb\x4f\x19\x16\x3b\x60\x09\x26\x02\x6d\x06\x94\xe0\xfe\x71\x26\xb5\x78\xa1\x29\xb3\x16\x60\xe0\xa3\x97\x8b\x04\x6e
Descomprimido: A veces, una palabra escrita a tiempo vale mas que mil pensamientos no dichos. Hoy es un buen dia para comenzar algo nuevo, aunque sea con solo una linea.
Ratio de compresión: 0.62
'''
```

## Colab create table decode:
```
https://colab.research.google.com/drive/1x_80R0508hd8V_3Xgqni58dqopvPk0Wg#scrollTo=I4y1c3nXk-zm
```
This will run compression and decompression tests on several example strings, showing statistics about performance.

## Limitations

- SMAZ is optimized for ASCII text. By default, it verifies that the text is ASCII before compressing.
- To process non-ASCII text, you can pass `check_ascii=False` to the `compress()` method, but results may not be optimal.
- The algorithm works best with English text, as its encoding table is optimized for this language.

## Technical Implementation

This implementation includes:

- A decoding table with 253 entries for the most common text sequences
- Automatic generation of the lookup table for compression
- Optimized handling of verbatim characters (which have no entry in the table)
- Worst-case calculation to avoid unwanted expansion

## License

BSD License, in accordance with the original implementation.

Original SMAZ implementation: [https://github.com/antirez/smaz](https://github.com/antirez/smaz)
