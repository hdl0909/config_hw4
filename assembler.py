import sys
import os
import json
import struct

def assemble_instruction(instruction):
    opcode_map = {
        "LOAD_CONST": 5, # В регистр загружает константу
        "LOAD_MEM": 4, # Читает из указанной ячейки памяти (C) и загружает в регистр (B)
        "STORE_MEM": 2, # Читает из указанного регистра (B) и загружает в ячейку памяти (C)
        "MOD": 0, # Читает из регистра B и памяти по адресу C, выполнение операции остатка, и запись в регистр B
    }

    parts = instruction.split()
    if len(parts) < 3:
        raise ValueError(f"Неверное количество операндов в инструкции: {instruction}")

    command = parts[0]
    if command not in opcode_map:
        raise ValueError(f"Неизвестная команда: {command}")

    A = opcode_map[command]
    try:
        B, C = map(int, parts[1:3])
    except ValueError:
        raise ValueError(f"Операнды должны быть целыми числами: {parts[1:3]}")

    if A == 5:
        if C < 0:
            C = (2 ** 15 + C)
        C = bin(C)[2:].zfill(15)

        first_part = int(C[-2:] + bin(B)[2:].zfill(3) + bin(A)[2:].zfill(3), 2)
        second_part = int(C[5:13].zfill(8), 2)
        third_part = int(C[:5].zfill(8), 2)

        byte1 = struct.pack('<B', first_part)
        byte2 = struct.pack('<B', second_part)
        byte3 = struct.pack('<B', third_part)

        return [byte1, byte2, byte3]

    elif A in [0, 2, 4]:
        C = bin(C)[2:].zfill(3)

        first_part = int(C[-2:] + bin(B)[2:].zfill(3) + bin(A)[2:].zfill(3), 2)
        second_part = int(C[0].zfill(8), 2)

        byte1 = struct.pack('<B', first_part)
        byte2 = struct.pack('<B', second_part)

        return [byte1, byte2]

def assembler(input_path, bin_path, log_path):
    with open(input_path, 'r') as source_file:
        lines = source_file.readlines()

    binary = []
    log = []

    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            assembled = assemble_instruction(line)
            if assembled:
                binary.extend(assembled)
                log.append({"instruction": line, "bytes": [byte.hex() for byte in assembled]})
        except ValueError as e:
            print(f"Ошибка в инструкции: {line} — {e}")

    with open(bin_path, 'wb') as bin_file:
        for byte in binary:
            bin_file.write(byte)

    with open(log_path, 'w') as log_file:
        json.dump(log, log_file, indent=4)

def main():
    source_path = sys.argv[1]
    bin_path = sys.argv[2]
    log_path = sys.argv[3]
    if len(sys.argv) != 4:
        print("Использование: python assembler.py <source_file> <bin_file> <log_file>")
    if not os.path.exists(source_path):
        print(f"Файл {source_path} не существует")
        exit(1)
    elif not bin_path.endswith('.bin'):
        print(f"Файл {bin_path} не бинарный")
        exit(1)
    else:
        assembler(source_path, bin_path, log_path)
        print(f"Результаты выполнения сохранены в {bin_path}")

if __name__ == "__main__":
    main()
