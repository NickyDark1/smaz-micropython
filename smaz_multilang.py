"""
smaz_multilang.py - Biblioteca de compresión SMAZ con soporte multilingüe
Adaptada para funcionar con MicroPython y optimizada para múltiples idiomas
"""

class SmazMultilang:
    """Implementación de SMAZ optimizada para múltiples idiomas"""
    
    # Tabla de decodificación genérica con soporte multilingüe
    # Esta tabla incluye:
    # 1. Caracteres individuales frecuentes en muchos idiomas
    # 2. Secuencias comunes en español, inglés y otros idiomas europeos
    # 3. Símbolos, puntuación y patrones universales
    DECODE = [
        # Espacio y caracteres individuales de alta frecuencia
        " ", "e", "a", "o", "n", "i", "s", "r", "l", "t", "d", "c", "m", "u", "p", "b", 
        "g", "v", "f", "y", "h", "j", "k", "w", "z", "x", "q",
        
        # Combinaciones de 2 letras muy frecuentes (multilingüe)
        "en", "es", "de", "la", "el", "ar", "on", "in", "or", "er", "an", "te", "ra", 
        "al", "st", "nt", "to", "re", "ll", "co", "le", "se", "os", "as", "ta", "nd", 
        "me", "lo", "ro", "po", "qu", "di", "ca", "si", "ti", "li", "do", "tr", "ma", 
        "ch", "ue", "ci", "pr", "pa", "ri", "su", "mi", "mo", "un", "ha", "no", "ya",
        
        # Secuencias frecuentes en español
        "que", "con", "los", "las", "por", "una", "para", "del", "está", "pero", "más", 
        "como", "bien", "todo", "esta", "cada", "sobre", "entre", "muy", "hay", "debe", 
        "así", "poco", "algo", "solo", "ción", "mente", "dad", "ado", "ido", "ando",
        
        # Secuencias frecuentes en inglés
        "the", "and", "ing", "of", "to", "is", "that", "for", "you", "not", "with", 
        "this", "are", "have", "be", "they", "from", "at", "one", "all", "by", "was", 
        "were", "what", "when", "how", "tion", "able", "ive", "ed", "ly", 
        
        # Secuencias útiles en otros idiomas europeos (francés, italiano, portugués, etc.)
        "et", "dans", "pour", "les", "des", "est", "che", "per", "non", "sono", "uma", 
        "das", "der", "das", "und", "ist", "den", "ein", "qui", "par", "dans", "com", 
        "ne", "au", "ça", "ce", "je", "tu", "il", "da", "na", "em", "vor", "nach", 
        "bei", "zum", 
        
        # Caracteres acentuados frecuentes
        "á", "é", "í", "ó", "ú", "ü", "ñ", "ç", "ã", "õ", "â", "ê", "î", "ô", "û", 
        "à", "è", "ì", "ò", "ù", "ä", "ë", "ï", "ö", "ü", "ß",
        
        # Patrones universales: puntuación, fechas, números
        ".", ",", ":", ";", "?", "!", "(", ")", "-", "/", "'", "\"", "\n", "\r", "\r\n",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "20", "30", "00", 
        
        # Patrones web e informáticos
        "http://", "https://", ".com", ".org", ".net", ".io", "www.", "@", "&", "%", 
        "+", "=", "#", "*", "$", "€", "£", "<", ">", "[", "]", "{", "}", "_", "|", "\\",
        
        # Secuencias genéricas útiles
        "ok", "hi", "hello", "yes", "no", "hola", "gracias", "info", "help", "error",
        "user", "name", "email", "password", "login", "file", "menu", "home", "date",
        "time", "day", "month", "year", 
        
        # Fechas y tiempos comunes
        "2024", "2025", "jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", 
        "oct", "nov", "dec", "mon", "tue", "wed", "thu", "fri", "sat", "sun",
        
        # Caracteres especiales con significado lingüístico
        "¿", "¡", "«", "»", "„", """, """, "‚", "'", "'", "‹", "›", "–", "—", "…"
    ]
    
    def __init__(self):
        """Inicializa el objeto SmazMultilang creando la tabla de búsqueda"""
        self._lookup = self._create_lookup()
    
    def _create_lookup(self):
        """Crea la tabla de búsqueda para compresión"""
        lookup = {}
        for enc_byte, text in enumerate(self.DECODE):
            # Asegurarse de que no superemos los 253 elementos (254 y 255 son especiales)
            if enc_byte >= 254:
                break
            lookup[text] = chr(enc_byte)
        return lookup
    
    def _worst_size(self, length):
        """Calcula el peor caso de tamaño de compresión"""
        if length == 0:
            return 0
        elif length == 1:
            return 2
        else:
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
    
    def compress(self, text, check_ascii=False):
        """
        Comprime un texto usando el algoritmo SMAZ multilingüe
        
        Args:
            text: Texto a comprimir
            check_ascii: Verificar si el texto es ASCII (recomendado False para texto no inglés)
            
        Returns:
            Texto comprimido
        """
        # Casos especiales
        if not text:
            return text
        
        if check_ascii:
            for ch in text:
                if ord(ch) >= 128:
                    raise ValueError('SMAZ con verificación ASCII solo procesa texto ASCII')
        
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
        Descomprime un texto comprimido con SMAZ multilingüe
        
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
_smaz_multilang_instance = None

def get_instance():
    """Retorna una instancia compartida de SmazMultilang (patrón singleton)"""
    global _smaz_multilang_instance
    if _smaz_multilang_instance is None:
        _smaz_multilang_instance = SmazMultilang()
    return _smaz_multilang_instance

def compress(text, check_ascii=False):
    """Función de conveniencia para comprimir texto"""
    return get_instance().compress(text, check_ascii)

def decompress(compressed):
    """Función de conveniencia para descomprimir texto"""
    return get_instance().decompress(compressed)


# Función para pruebas
def test():
    """Ejecuta pruebas de compresión en cadenas de ejemplo en varios idiomas"""
    smaz = get_instance()
    test_strings = [
        # Inglés
        "This is a small string",
        "Hello World!",
        
        # Español
        "Hola Mundo!",
        "Esto es una pequeña cadena de prueba",
        "El rápido zorro marrón salta sobre el perro perezoso",
        
        # Francés
        "Bonjour le monde!",
        "C'est une petite chaîne de test",
        
        # Alemán
        "Hallo Welt!",
        "Dies ist ein kleiner Teststring",
        
        # Italiano
        "Ciao mondo!",
        "Questa è una piccola stringa di prova",
        
        # Portugués
        "Olá mundo!",
        "Esta é uma pequena cadeia de teste",
        
        # Multilingüe
        "Hello/Hola/Bonjour/Ciao/Hallo/Olá - 2024",
        "http://www.example.com",
        '''A veces, una palabra escrita a tiempo vale más que mil pensamientos no dichos. 
        Hoy es un buen día para comenzar algo nuevo.''',
    ]
    
    for s in test_strings:
        try:
            compressed = smaz.compress(s, check_ascii=False)
            decompressed = smaz.decompress(compressed)
            
            print("Original ({0} bytes): {1}".format(len(s), s))
            
            # Usar representación hexadecimal para mostrar caracteres no imprimibles
            hex_repr = "".join("\\x{:02x}".format(ord(c)) for c in compressed)
            print("Comprimido ({0} bytes): {1}".format(len(compressed), hex_repr))
            
            print("Descomprimido: {0}".format(decompressed))
            ratio = len(compressed)/len(s) * 100
            print("Ratio de compresión: {0:.2f}%".format(ratio))
            
            # Verificar si la descompresión tuvo éxito
            if decompressed != s:
                print("ERROR: ¡La descompresión no coincide con el original!")
            
            print()
        except Exception as e:
            print("Error con cadena '{0}': {1}".format(s, str(e)))


# Solo ejecutar las pruebas si se ejecuta este archivo directamente
if __name__ == "__main__":
    test()
