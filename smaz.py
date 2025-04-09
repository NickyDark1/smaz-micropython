"""
smaz.py - Biblioteca de compresión SMAZ optimizada para MicroPython
Adaptado del port Python por Max Smith
Original SMAZ por Salvatore Sanfilippo

BSD license por implementación original: https://github.com/antirez/smaz
https://github.com/CordySmith/PySmaz/tree/master
"""

class Smaz:
    """Implementación modular y optimizada de SMAZ para MicroPython"""
    
    # Tabla de decodificación con 253 entradas
    DECODE = [" ", "the", "e", "t", "a", "of", "o", "and", "i", "n", "s", "e ", "r", " th",
        " t", "in", "he", "th", "h", "he ", "to", "\r\n", "l", "s ", "d", " a", "an",
        "er", "c", " o", "d ", "on", " of", "re", "of ", "t ", ", ", "is", "u", "at",
        "   ", "n ", "or", "which", "f", "m", "as", "it", "that", "\n", "was", "en",
        "  ", " w", "es", " an", " i", "\r", "f ", "g", "p", "nd", " s", "nd ", "ed ",
        "w", "ed", "http://", "for", "te", "ing", "y ", "The", " c", "ti", "r ", "his",
        "st", " in", "ar", "nt", ",", " to", "y", "ng", " h", "with", "le", "al", "to ",
        "b", "ou", "be", "were", " b", "se", "o ", "ent", "ha", "ng ", "their", "\"",
        "hi", "from", " f", "in ", "de", "ion", "me", "v", ".", "ve", "all", "re ",
        "ri", "ro", "is ", "co", "f t", "are", "ea", ". ", "her", " m", "er ", " p",
        "es ", "by", "they", "di", "ra", "ic", "not", "s, ", "d t", "at ", "ce", "la",
        "h ", "ne", "as ", "tio", "on ", "n t", "io", "we", " a ", "om", ", a", "s o",
        "ur", "li", "ll", "ch", "had", "this", "e t", "g ", "e\r\n", " wh", "ere",
        " co", "e o", "a ", "us", " d", "ss", "\n\r\n", "\r\n\r", "=\"", " be", " e",
        "s a", "ma", "one", "t t", "or ", "but", "el", "so", "l ", "e s", "s,", "no",
        "ter", " wa", "iv", "ho", "e a", " r", "hat", "s t", "ns", "ch ", "wh", "tr",
        "ut", "/", "have", "ly ", "ta", " ha", " on", "tha", "-", " l", "ati", "en ",
        "pe", " re", "there", "ass", "si", " fo", "wa", "ec", "our", "who", "its", "z",
        "fo", "rs", ">", "ot", "un", "<", "im", "th ", "nc", "ate", "><", "ver", "ad",
        " we", "ly", "ee", " n", "id", " cl", "ac", "il", "</", "rt", " wi", "div",
        "e, ", " it", "whi", " ma", "ge", "x", "e c", "men", ".com"]
    
    def __init__(self):
        """Inicializa el objeto Smaz creando la tabla de búsqueda"""
        self._lookup = self._create_lookup()
    
    def _create_lookup(self):
        """Crea la tabla de búsqueda para compresión"""
        lookup = {}
        for enc_byte, text in enumerate(self.DECODE):
            lookup[text] = chr(enc_byte)
        return lookup
    
    def _is_ascii(self, text):
        """Verifica si el texto contiene solo caracteres ASCII"""
        try:
            for ch in text:
                if ord(ch) >= 128:
                    return False
            return True
        except:
            return False
    
    def _worst_size(self, length):
        """Calcula el peor caso de tamaño de compresión"""
        if length == 0:
            return 0
        elif length == 1:
            return 2
        else:
            # Cálculo simplificado
            full_chunks = length // 255
            remainder = length % 255
            overhead = full_chunks * 2 + (2 if remainder > 0 else 0)
            return length + overhead
    
    def _flush_verbatim(self, buffer, output):
        """Agrega caracteres verbatim al output"""
        if not buffer:
            return
            
        if len(buffer) == 1:
            # Un solo byte verbatim
            output.append(chr(254) + buffer[0])
        else:
            # Múltiples bytes verbatim
            output.append(chr(255) + chr(len(buffer) - 1))
            output.append(''.join(buffer))
        
        # Vaciar el buffer
        buffer.clear()
    
    def compress(self, text, check_ascii=True):
        """
        Comprime un texto usando el algoritmo SMAZ
        
        Args:
            text: Texto a comprimir
            check_ascii: Verificar si el texto es ASCII
            
        Returns:
            Texto comprimido
        """
        # Casos especiales
        if not text:
            return text
        
        if check_ascii and not self._is_ascii(text):
            raise ValueError('SMAZ solo procesa texto ASCII')
        
        output = []
        verbatim = []
        pos = 0
        max_len = len(text)
        
        while pos < max_len:
            # Buscar la secuencia más larga que coincida
            best_match = None
            best_len = 0
            
            # Probar secuencias de longitud decreciente (máx 7 caracteres)
            for match_len in range(min(7, max_len - pos), 0, -1):
                substring = text[pos:pos+match_len]
                if substring in self._lookup:
                    best_match = self._lookup[substring]
                    best_len = match_len
                    break
            
            if best_match:
                # Encontramos una coincidencia en la tabla
                self._flush_verbatim(verbatim, output)
                output.append(best_match)
                pos += best_len
            else:
                # Sin coincidencia, agregar a buffer verbatim
                verbatim.append(text[pos])
                pos += 1
                
                # Vaciar si alcanzamos la longitud máxima verbatim
                if len(verbatim) == 255:
                    self._flush_verbatim(verbatim, output)
        
        # Vaciar cualquier carácter verbatim restante
        self._flush_verbatim(verbatim, output)
        
        # Verificar si la compresión empeoró el tamaño
        result = ''.join(output)
        if len(result) > self._worst_size(max_len):
            # Encapsular el texto original es mejor
            return self._encapsulate(text)
        
        return result
    
    def _encapsulate(self, text):
        """Encapsula un texto en chunks de código 255"""
        if not text:
            return text
            
        output = []
        for i in range(0, len(text), 255):
            chunk = text[i:i+255]
            if len(chunk) == 1:
                output.append(chr(254) + chunk)
            else:
                output.append(chr(255) + chr(len(chunk) - 1))
                output.append(chunk)
        return ''.join(output)
    
    def decompress(self, compressed):
        """
        Descomprime un texto comprimido con SMAZ
        
        Args:
            compressed: Texto comprimido
            
        Returns:
            Texto descomprimido
        """
        if not compressed:
            return compressed
        
        output = []
        pos = 0
        max_len = len(compressed)
        
        try:
            while pos < max_len:
                ch = ord(compressed[pos])
                pos += 1
                
                if ch < 254:
                    # Entrada de la tabla de códigos
                    output.append(self.DECODE[ch])
                else:
                    next_byte = compressed[pos]
                    pos += 1
                    
                    if ch == 254:
                        # Byte verbatim
                        output.append(next_byte)
                    else:  # ch == 255
                        # Cadena verbatim
                        end_pos = pos + ord(next_byte) + 1
                        if end_pos > max_len:
                            raise ValueError('Desbordamiento de buffer')
                        output.append(compressed[pos:end_pos])
                        pos = end_pos
                        
            return ''.join(output)
        except (IndexError, ValueError) as e:
            raise ValueError('Error de descompresión: {}'.format(str(e)))


# Crea una instancia singleton para facilitar el uso
_smaz_instance = None

def get_instance():
    """Retorna una instancia compartida de Smaz (patrón singleton)"""
    global _smaz_instance
    if _smaz_instance is None:
        _smaz_instance = Smaz()
    return _smaz_instance

def compress(text, check_ascii=True):
    """Función de conveniencia para comprimir texto"""
    return get_instance().compress(text, check_ascii)

def decompress(compressed):
    """Función de conveniencia para descomprimir texto"""
    return get_instance().decompress(compressed)


