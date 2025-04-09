
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
