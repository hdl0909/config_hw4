import struct
import sys
import os
import json


def load_memory(memory, address, value, memory_range):
    if address < memory_range[0] or address > memory_range[1]:
        raise ValueError(f"Address {address} out of bounds for memory range")
    memory[address] = value



def load_register(registers, reg_num, value):
    registers[reg_num] = value


def read_memory(memory, address, memory_range):
    if address < memory_range[0] or address > memory_range[1]:
        raise ValueError(f"Address {address} out of bounds for memory range")
    return memory[address]


def read_register(registers, reg_num):
    return registers[reg_num]


def decode_instruction(bytecode, pc):
    if bytecode[pc] & 0x7 == 5:
        instruction_length = 3
    else:
        instruction_length = 2

    hex_bytecode = [f"{byte:02x}" for byte in bytecode[pc:pc + instruction_length]]

    if len(hex_bytecode) == 3:
        byte1 = int(hex_bytecode[0], 16)
        byte2 = int(hex_bytecode[1], 16)
        rest = [int(hex_bytecode[2], 16)]
    elif len(hex_bytecode) == 2:
        byte1 = int(hex_bytecode[0], 16)
        byte2 = int(hex_bytecode[1], 16)
        rest = []

    first_part = byte1
    second_part = byte2
    C = (second_part << 2) | ((first_part & 0xC0) >> 6)
    B = (first_part >> 3) & 0x7
    A = first_part & 0x7

    return (A, B, C), instruction_length


def execute_instruction(memory, registers, bytecode, pc, memory_range):
    decoded, instruction_length = decode_instruction(bytecode, pc)

    A, B, C = decoded
    log = []

    if A == 5:  # LOAD_CONST
        load_register(registers, B, C)
        log.append(f"LOAD_CONST: R{B} <- {C}")
    elif A == 4:  # LOAD_MEM
        value = read_memory(memory, C, memory_range)
        load_register(registers, B, value)
        log.append(f"LOAD_MEM: R{B} <- M{C} ({value})")
    elif A == 2:  # STORE_MEM
        value = read_register(registers, B)
        load_memory(memory, C, value, memory_range)
        log.append(f"STORE_MEM: M{C} <- R{B} ({value})")
    elif A == 0:  # MOD
        reg_value = read_register(registers, B)
        mem_value = read_memory(memory, C, memory_range)
        if mem_value == 0:
            log.append(f"Ошибка: деление на ноль при операции MOD (R{B} % M{C})")
            result = 0
        else:
            result = reg_value % mem_value
            load_register(registers, B, result)
            log.append(f"MOD: R{B} <- {reg_value} % {mem_value} = {result}")

    pc += instruction_length
    return pc, log


def run_interpreter(bin_path, result_path, memory_range):
    memory_size = 1024
    memory = [0] * memory_size
    registers = [0] * 16

    with open(bin_path, 'rb') as bin_file:
        bytecode = list(bin_file.read())

    results = []
    pc = memory_range[0]

    while pc < len(bytecode):
        pc, log = execute_instruction(memory, registers, bytecode, pc, memory_range)
        results.append(log)

        if pc > memory_range[1]:
            break

    with open(result_path, 'w') as result_file:
        json.dump(results, result_file, indent=4)


def main():
    if len(sys.argv) != 4:
        print("Использование: python interpreter.py <bin_file> <result_file> <memory_range>")
        sys.exit(1)

    bin_path = sys.argv[1]
    result_path = sys.argv[2]
    memory_range = list(map(int, sys.argv[3].split(',')))

    if not os.path.exists(bin_path):
        print(f"Файл {bin_path} не существует")
        sys.exit(1)

    run_interpreter(bin_path, result_path, memory_range)
    print(f"Результаты выполнения сохранены в {result_path}")


if __name__ == "__main__":
    main()
