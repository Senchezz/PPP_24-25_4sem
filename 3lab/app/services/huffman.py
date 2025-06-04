import heapq
from collections import Counter
from typing import Dict, Tuple

class Node:
    def __init__(self, char=None, freq=0):
        self.char = char       # символ (если листовой узел)
        self.freq = freq       # частота символа или сумма частот для внутренних узлов
        self.left = None       # левый потомок (Node)
        self.right = None      # правый потомок (Node)

    def __lt__(self, other):
        return self.freq < other.freq  # сравнение по частоте для использования в heapq


def build_huffman_tree(text: str) -> Node:
    freq = Counter(text)   # подсчёт частоты каждого символа
    heap = [Node(char=c, freq=f) for c, f in freq.items()]  # создаём узлы для каждого символа
    heapq.heapify(heap)    # формируем кучу по частоте

    while len(heap) > 1:
        a = heapq.heappop(heap)  # извлекаем два узла с минимальной частотой
        b = heapq.heappop(heap)
        merged = Node(freq=a.freq + b.freq)  # создаём новый внутренний узел
        merged.left = a
        merged.right = b
        heapq.heappush(heap, merged)  # возвращаем в кучу объединённый узел
    
    return heap[0]  # корень дерева

def build_codes(root: Node) -> Dict[str, str]:
    codes = {}
    def dfs(node, path=""):
        if node.char is not None:  # если лист — запоминаем код для символа
            codes[node.char] = path
        else:
            dfs(node.left, path + "0")   # идём влево — добавляем '0'
            dfs(node.right, path + "1")  # идём вправо — добавляем '1'
    dfs(root)
    return codes

def huffman_encode(text: str) -> Tuple[bytes, Dict[str, str], int]:
    tree = build_huffman_tree(text)
    codes = build_codes(tree)
    encoded_bits = ''.join(codes[c] for c in text)  # кодируем текст в битовую строку

    padding = 8 - len(encoded_bits) % 8  # сколько нужно нулей добавить для кратности 8 битам
    encoded_bits += '0' * padding         # добавляем нули (паддинг)

    byte_array = bytearray()
    for i in range(0, len(encoded_bits), 8):
        byte = encoded_bits[i:i+8]
        byte_array.append(int(byte, 2))  # преобразуем каждые 8 бит в байт и добавляем в массив

    return bytes(byte_array), codes, padding

def huffman_decode(encoded: bytes, codes: Dict[str, str], padding: int) -> str:
    inverse_codes = {v: k for k, v in codes.items()}  # инвертируем словарь для поиска символа по коду
    bits = ''.join(f'{byte:08b}' for byte in encoded)  # преобразуем байты обратно в битовую строку
    bits = bits[:-padding] if padding > 0 else bits    # убираем добавленные в конце нули

    current = ""
    decoded = []
    for bit in bits:
        current += bit
        if current in inverse_codes:      # если текущий путь совпал с кодом символа
            decoded.append(inverse_codes[current])  # добавляем символ в результат
            current = ""                   # сбрасываем буфер

    return ''.join(decoded)