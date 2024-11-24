import unittest
import os
import struct
import json
from assembler import assemble_instruction, assembler
from interpreter import run_interpreter


class TestAssembler(unittest.TestCase):

    def test_assemble_instruction_load_const(self):
        instruction = "LOAD_CONST 0 765"
        expected_bytes = [b'\x45', b'\xBF', b'\x00']
        result = assemble_instruction(instruction)
        self.assertEqual([byte.hex() for byte in result], [byte.hex() for byte in expected_bytes])

    def test_assemble_instruction_load_mem(self):
        instruction = "LOAD_MEM 2 3"
        expected_bytes = [b'\xD4', b'\x00']
        result = assemble_instruction(instruction)
        self.assertEqual([byte.hex() for byte in result], [byte.hex() for byte in expected_bytes])

    def test_assemble_instruction_invalid_command(self):
        instruction = "INVALID_CMD 1 2"
        with self.assertRaises(ValueError):
            assemble_instruction(instruction)

    def test_assemble_instruction_invalid_operands(self):
        instruction = "LOAD_CONST 1 non_integer"
        with self.assertRaises(ValueError):
            assemble_instruction(instruction)

    def test_assembler(self):
        input_path = 'source.asm'
        bin_path = 'file.bin'
        log_path = 'log.json'

        # Prepare sample input file
        with open(input_path, 'w') as f:
            f.write("LOAD_CONST 1 100\n")
            f.write("STORE_MEM 2 3\n")

        assembler(input_path, bin_path, log_path)

        self.assertTrue(os.path.exists(bin_path))

        # Проверяем содержимое лог файла
        with open(log_path, 'r') as log_file:
            log_data = log_file.read()
            self.assertIn("LOAD_CONST 1 100", log_data)
            self.assertIn("STORE_MEM 2 3", log_data)


class TestInterpreter(unittest.TestCase):

    def test_load_const(self):
        bin_data = [b'\x45', b'\xBF', b'\x00']
        bin_path = 'file.bin'
        with open(bin_path, 'wb') as f:
            f.write(b''.join(bin_data))

        result_path = 'result_log.json'
        memory_range = [0, 1023]

        run_interpreter(bin_path, result_path, memory_range)

        self.assertTrue(os.path.exists(result_path))

        with open(result_path, 'r') as result_file:
            results = json.load(result_file)
            self.assertIn("LOAD_CONST: R0 <- 765", str(results))

    def test_memory_operations(self):
        bin_data = [b'\x45', b'\xBF', b'\x00',
                    b'\xB8', b'\x01']
        bin_path = 'file.bin'
        with open(bin_path, 'wb') as f:
            f.write(b''.join(bin_data))

        result_path = 'result_log.json'
        memory_range = [0, 1023]

        run_interpreter(bin_path, result_path, memory_range)

        with open(result_path, 'r') as result_file:
            results = json.load(result_file)
            self.assertIn("LOAD_CONST: R0 <- 765", str(results))
            self.assertIn('Ошибка: деление на ноль при операции MOD (R7 % M6)', str(results))


if __name__ == '__main__':
    unittest.main()

