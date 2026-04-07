import zlib
import string

# Алфавит для base62 (цифры + строчные + заглавные)
ALPHABET = string.digits + string.ascii_letters

def short_hash_str(user_id: int | str) -> str:
    # 1. Получаем числовой хэш (CRC32)
    num = zlib.crc32(str(user_id).encode()) & 0xffffffff
    
    # 2. Конвертируем число в строку base62 вручную (быстро и без лишних библиотек)
    if num == 0:
        return ALPHABET[0]
    
    result = []
    while num > 0:
        num, rem = divmod(num, 62)
        result.append(ALPHABET[rem])
    
    return ''.join(reversed(result))