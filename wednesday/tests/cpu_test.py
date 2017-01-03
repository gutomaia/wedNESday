from unittest import TestCase
from unittest import skip

from wednesday.cpu6502 import *

REGISTERS = {
    'A': 'accumulator',
    'X': 'x_index',
    'Y': 'y_index',
    'SP': 'stack_pointer',
}

FLAGS = {
    'C': 'carry_flag',
    'Z': 'zero_flag',
    'I': 'interrupt_disable_flag',
    'D': 'decimal_mode_flag',
    'B': 'break_flag',
    'O': 'overflow_flag',
    'N': 'sign_flag',
}

class CPUTest(TestCase):

    def setUp(self):
        class Options():

            def __init__(self):
                self.rom = None
                self.ram = None
                self.bus = None
                self.pc = 0xFFFA

        self.memory = BasicMemory()
        self.options = Options()
        self.cpu = CPU(self.options, self.memory)

        self.executor = self.cpu.run()

    def tearDown(self):
        pass

    def cpu_pc(self, counter):
        self.cpu.program_counter = counter

    def memory_set(self, pos, val):
        self.memory._mem[pos] = val

    def memory_fetch(self, pos):
        return self.memory._mem[pos]

    def execute(self):
        cycle, _ = self.executor.next()
        return cycle, _

    def cpu_set_register(self, register, value):
        name = REGISTERS[register]
        setattr(self.cpu, name, value)

    def cpu_register(self, register):
        name = REGISTERS[register]
        return getattr(self.cpu, name)

    def cpu_flag(self, flag):
        name = FLAGS[flag]
        return not not getattr(self.cpu, name)

    def test_lda_imediate(self):
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa9)
        self.memory_set(0x0101, 0xff)
        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)

    def test_lda_zeropage(self):
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa5)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0xff)
        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_lda_zero_page_x(self):
        self.cpu_set_register('X', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb5)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_lda_absolute(self):
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xad)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_lda_absolute_x(self):
        self.cpu_set_register('X', 1)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xbd)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0xff)

        cycles, _ = self.execute()

        self.assertEquals(cycles, 4)
        self.assertEquals(self.cpu_register('A'), 0xff)

    @skip('TODO')
    def test_lda_absolute_x_2(self):
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xbd)
        self.memory_set(0x0101, 0xff)
        self.memory_set(0x0102, 0x02)
        self.memory_set(0x0300, 0xff)

        cycles, _ = self.execute()

        self.assertEquals(cycles, 5)

    def test_lda_absolute_y(self):

        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb9)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0xff)

        cycles, _ = self.execute()

        self.assertEquals(cycles, 4)

        self.assertEquals(self.cpu_register('A'), 0xff)

        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb9)
        self.memory_set(0x0101, 0xff)
        self.memory_set(0x0102, 0x02)
        self.memory_set(0x0300, 0xff)

        cycles, _ = self.execute()

        # TODO: self.assertEquals(cycles, 5)


    def test_lda_indirect_x(self):

        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa1)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)
        self.memory_set(0x0087, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_lda_indirect_y(self):

        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb1)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)
        self.memory_set(0x0087, 0xff)

        cycles, _ = self.execute()

        #TODO: self.assertEquals(cycle, 5)

        self.assertEquals(self.cpu_register('A'), 0xff)

        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb1)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0xff)
        self.memory_set(0x0085, 0x02)
        self.memory_set(0x0300, 0xff)

        cycles, _ = self.execute()

        #TODO: self.assertEquals(cycle, 6)


    def test_lda_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa9)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_lda_z_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa9)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_lda_n_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa9)
        self.memory_set(0x0101, 0x81)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_lda_n_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa9)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // LDX

    def test_ldx_immediate(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa2)
        self.memory_set(0x0101, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('X'), 0xff)

    def test_ldx_zero_page(self):
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa6)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0xff)

        self.execute()
        self.assertEquals(self.cpu_register('X'), 0xff)


    def test_ldx_zeropage_y(self):
        self.cpu_set_register('Y', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb6)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0xff)

        self.execute()
        self.assertEquals(self.cpu_register('X'), 0xff)


    def test_ldx_absolute(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xae)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('X'), 0xff)


    def test_ldx_absolute_y(self):

        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xbe)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('X'), 0xff)


    def test_ldx_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa2)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_ldx_z_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa2)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_ldx_n_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa2)
        self.memory_set(0x0101, 0x81)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_ldx_n_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa2)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // LDY

    def test_ldy_immediate(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa0)
        self.memory_set(0x0101, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)


    def test_ldy_zeropage(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa4)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)


    def test_ldy_zeropage_x(self):

        self.cpu_set_register('X', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xb4)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)


    def test_ldy_absolute(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xac)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)


    def test_ldy_absolute_x(self):

        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xbc)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0xff)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)


    def test_ldy_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa0)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_ldy_z_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa0)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_ldy_n_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa0)
        self.memory_set(0x0101, 0x81)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_ldy_n_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa0)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // STA

    def test_sta_zeropage(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x85)
        self.memory_set(0x0101, 0x84)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)


    def test_sta_zeropage_x(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x95)
        self.memory_set(0x0101, 0x84)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0085), 0xff)


    def test_sta_absolute(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x8d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)


    def test_sta_absolute_x(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x9d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0085), 0xff)


    def test_sta_absolute_y(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x99)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0085), 0xff)


    def test_sta_indirect_x(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x81)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0087), 0xff)


    def test_sta_indirect_y(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x91)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0087), 0xff)


    # // STX

    def test_stx_zeropage(self):

        self.cpu_set_register('X', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x86)
        self.memory_set(0x0101, 0x84)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)



    def test_stx_zeropage_y(self):

        self.cpu_set_register('X', 0xff)
        self.cpu_set_register('Y', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x96)
        self.memory_set(0x0101, 0x84)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0085), 0xff)


    def test_stx_absolute(self):

        self.cpu_set_register('X', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x8e)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)


    # // STY

    def test_sty_zeropage(self):

        self.cpu_set_register('Y', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x84)
        self.memory_set(0x0101, 0x84)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)


    def test_sty_zeropage_y(self):

        self.cpu_set_register('Y', 0xff)
        self.cpu_set_register('X', 0x01)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x94)
        self.memory_set(0x0101, 0x84)

        self.execute()


        self.assertEquals(self.memory_fetch(0x0085), 0xff)


    def test_sty_absolute(self):

        self.cpu_set_register('Y', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x8c)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)

        self.execute()

        self.assertEquals(self.memory_fetch(0x0084), 0xff)


    # // TAX

    def test_tax(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xaa)

        self.execute()

        self.assertEquals(self.cpu_register('X'), 0xff)


    def test_tax_z_flag_set(self):

        self.cpu_set_register('A', 0x00)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xaa)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))

    def test_tax_z_flag_unset(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xaa)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))

    def test_tax_n_flag_set(self):
        self.cpu_set_register('A', 0x81)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xaa)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_tax_n_flag_unset(self):
        self.cpu_set_register('A', 0x01)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xaa)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // TAY

    def test_tay(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xa8)

        self.execute()

        self.assertEquals(self.cpu_register('Y'), 0xff)

    # // TXA

    def test_txa(self):

        self.cpu_set_register('X', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x8a)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    # // TYA

    def test_tya(self):

        self.cpu_set_register('Y', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x98)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)

    # // TSX

    def test_tsx(self):
        self.cpu_set_register('SP', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xba)

        self.execute()

        self.assertEquals(self.cpu_register('X'), 0xff)


    # // TXS

    def test_txs(self):
        self.cpu_set_register('X', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x9a)

        self.execute()

        self.assertEquals(self.cpu_register('SP'), 0xff)


    # // PHA

    @skip('TODO')
    def test_pha(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x48)

        self.execute()

    #     if cpu.pull() != 0xff {
    #         t.Error("Memory is not 0xff")
    #     }


    # // PHP
    @skip('TODO')
    def test_php(self):
        self.cpu_set_register('P', 0xff)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x08)

        self.execute()

        #     if cpu.pull() != 0xff {
        #         t.Error("Memory is not 0xff")
        #     }


    # // PLA

    @skip('TODO')
    def test_pla(self):

        self.cpu_pc(0x0100)
        #TODO: cpu.push(0xff)

        self.memory_set(0x0100, 0x68)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)



    def test_pla_z_flag_set(self):

        # TODO: cpu.push(0x00)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x68)

        self.execute()

        # self.assertTrue(self.cpu_flag('Z'))


    def test_pla_z_flag_unset(self):

        # TODO: cpu.push(0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x68)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


# def test_Pla_n_flag_set(self):

#     cpu.push(0x81)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x68)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Pla_n_flag_unset(self):

#     cpu.push(0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x68)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // PLP

# def test_Plp(self):

#     self.cpu_pc(0x0100)
#     cpu.push(0xff)

#     self.memory_set(0x0100, 0x28)

#     self.execute()

#     if cpu.Registers.P != 0xef {
#         t.Error("Status is not 0xef")
#     }


    # // AND

    def test_and_immediate(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x29)
        self.memory_set(0x0101, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_zeropage(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x25)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_zeropage_x(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 0x01)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x35)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_absolute(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x2d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_absolute_x(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x3d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_absolute_y(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x39)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_indirect_x(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x21)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_indirect_y(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x31)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x0f)


    def test_and_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x29)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_and_z_flag_unset(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x29)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_and_n_flag_set(self):
        self.cpu_set_register('A', 0x81)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x29)
        self.memory_set(0x0101, 0x81)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_and_n_flag_unset(self):
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x29)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // EOR

    def test_eor_immediate(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x49)
        self.memory_set(0x0101, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_zeropage(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x45)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_zeropage_x(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 0x01)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x55)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_absolute(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x4d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_absolute_x(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x5d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_absolute_y(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x59)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_indirect_x(self):
        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x41)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_indirect_y(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x51)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xf0)


    def test_eor_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x49)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_eor_z_flag_unset(self):
        self.cpu_set_register('A', 0x00)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x49)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_eor_n_flag_set(self):
        self.cpu_set_register('A', 0x00)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x49)
        self.memory_set(0x0101, 0x81)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_eor_n_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x49)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // ORA

    def test_ora_immediate(self):
        self.cpu_set_register('A', 0xf0)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x09)
        self.memory_set(0x0101, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)



    def test_ora_zeropage(self):

        self.cpu_set_register('A', 0xf0)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x05)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_zeropage_x(self):
        self.cpu_set_register('A', 0xf0)
        self.cpu_set_register('X', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x15)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_absolute(self):
        self.cpu_set_register('A', 0xf0)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x0d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_absolute_x(self):

        self.cpu_set_register('A', 0xf0)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x1d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)



    def test_ora_absolute_y(self):

        self.cpu_set_register('A', 0xf0)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x19)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_indirect_x(self):

        self.cpu_set_register('A', 0xf0)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x01)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_indirect_y(self):

        self.cpu_set_register('A', 0xf0)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x11)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)
        self.memory_set(0x0087, 0x0f)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0xff)


    def test_ora_z_flag_set(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x09)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('Z'))


    def test_ora_z_flag_unset(self):

        self.cpu_set_register('A', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x09)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertFalse(self.cpu_flag('Z'))


    def test_ora_n_flag_set(self):
        self.cpu_set_register('A', 0x81)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x09)
        self.memory_set(0x0101, 0x00)

        self.execute()

        self.assertTrue(self.cpu_flag('N'))


    def test_ora_n_flag_unset(self):

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x09)
        self.memory_set(0x0101, 0x01)

        self.execute()

        self.assertFalse(self.cpu_flag('N'))


    # // BIT

    def test_bit_zeropage(self):

        self.cpu_set_register('A', 0xff)
        self.cpu_pc(0x0100)
        self.memory_set(0x0100, 0x24)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x7f)

        self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_BitAbsolute(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2c)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x7f)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_Bit_n_flag_set(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Bit_n_flag_unset(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x7f)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_Bit_v_flag_set(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&V == 0 {
#         t.Error("V flag is not set")
#     }


# def test_Bit_v_flag_unset(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x3f)

#     self.execute()

#     if cpu.Registers.P&V != 0 {
#         t.Error("V flag is set")
#     }


# def test_Bit_z_flag_set(self):

#     cpu.Registers.A = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Bit_z_flag_unset(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x24)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x3f)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# // ADC

# def test_AdcImmediate(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.A != 0x03 {
#         t.Error("Register A is not 0x03")
#     }

#     cpu.Registers.P |= D
#     cpu.Registers.A = 0x29 // BCD
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x11) // BCD

#     self.execute()

#     if cpu.Registers.A != 0x40 { // BCD
#         t.Error("Register A is not 0x40")
#     }

#     cpu.Registers.P |= D
#     cpu.Registers.A = 0x29 | uint8(N) // BCD
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x29) // BCD

#     self.execute()

#     if cpu.Registers.A != 0x38 { // BCD
#         t.Error("Register A is not 0x38")
#     }

#     cpu.Registers.P |= D
#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x58 // BCD
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x46) // BCD

#     self.execute()

#     if cpu.Registers.A != 0x05 { // BCD
#         t.Errorf("Register A is not 0x05")
#     }


    def test_adc_zeropage(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x65)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)



    def test_adc_zeropage_x(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_set_register('X', 0x01)

        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x75)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)


    def test_adc_absolute(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x6d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0084, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)

    def test_adc_absolute_x(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x7d)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)

    def test_adc_absolute_y(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x79)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0102, 0x00)
        self.memory_set(0x0085, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)

    def test_adc_indirect_x(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_set_register('X', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x61)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0085, 0x87)
        self.memory_set(0x0086, 0x00)
        self.memory_set(0x0087, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)


    def test_adc_indirect_y(self):
        self.cpu_set_register('A', 0x01)
        self.cpu_set_register('Y', 1)
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0x71)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x86)
        self.memory_set(0x0085, 0x00)
        self.memory_set(0x0087, 0x02)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x03)


# def test_AdcC_flag_set(self):

#     self.cpu_set_register('A', 0xff // -1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }

#     cpu.Registers.P |= C
#     self.cpu_set_register('A', 0xff // -1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x00) // +0

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_AdcC_flag_unset(self):

#     cpu.Registers.A = 0x00 // +0
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }

#     cpu.Registers.P &^= C
#     self.cpu_set_register('A', 0xff // -1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x00) // +0

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_adc_z_flag_set(self):

#     cpu.Registers.A = 0x00 // +0
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x00) // +0

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_adc_z_flag_unset(self):

#     cpu.Registers.A = 0x00 // +0
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0xff) // -1

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }

#     cpu.Registers.A = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_adc_v_flag_set(self):

#     cpu.Registers.A = 0x7f // +127
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&V == 0 {
#         t.Error("V flag is not set")
#     }


# def test_adc_v_flag_unset(self):

#     self.cpu_set_register('A', 0x01) // +1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&V != 0 {
#         t.Error("V flag is set")
#     }


# def test_adc_n_flag_set(self):

#     self.cpu_set_register('A', 0x01) // +1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_adc_n_flag_unset(self):

#     self.cpu_set_register('A', 0x01) // +1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x69)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // SBC

# def test_sbc_immediate(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }

#     cpu.Registers.P |= D
#     cpu.Registers.A = 0x29 // BCD
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x11) // BCD

#     self.execute()

#     if cpu.Registers.A != 0x18 { // BCD
#         t.Error("Register A is not 0x18")
#     }

    @skip('TODO')
    def test_SbcZeroPage(self):
        cpu.Registers.P |= C
        cpu.Registers.A = 0x02
        self.cpu_pc(0x0100)

        self.memory_set(0x0100, 0xe5)
        self.memory_set(0x0101, 0x84)
        self.memory_set(0x0084, 0x01)

        self.execute()

        self.assertEquals(self.cpu_register('A'), 0x01)


# def test_SbcZeroPageX(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf5)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcAbsolute(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xed)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcAbsoluteX(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xfd)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcAbsoluteY(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_set_register('Y', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf9)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcIndirectX(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe1)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x87)
#     self.memory_set(0x0086, 0x00)
#     self.memory_set(0x0087, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcIndirectY(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x02
#     self.cpu_set_register('Y', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf1)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x86)
#     self.memory_set(0x0085, 0x00)
#     self.memory_set(0x0087, 0x01)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_SbcC_flag_set(self):

#     cpu.Registers.A = 0xc4 // -60
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x3c) // +60

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_SbcC_flag_unset(self):

#     cpu.Registers.A = 0x02 // +2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x04) // +4

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_Sbc_z_flag_set(self):

#     cpu.Registers.A = 0x02 // +2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Sbc_z_flag_unset(self):

#     cpu.Registers.A = 0x02 // +2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Sbc_v_flag_set(self):

#     cpu.Registers.A = 0x80 // -128
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&V == 0 {
#         t.Error("V flag is not set")
#     }


# def test_Sbc_v_flag_unset(self):

#     self.cpu_set_register('A', 0x01) // +1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&V != 0 {
#         t.Error("V flag is set")
#     }


# def test_Sbc_n_flag_set(self):

#     cpu.Registers.A = 0xfd // -3
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Sbc_n_flag_unset(self):

#     cpu.Registers.A = 0x02 // +2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe9)
#     self.memory_set(0x0101, 0x01) // +1

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // CMP

# def test_CmpImmediate(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpZeroPage(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc5)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpZeroPageX(self):

#     self.cpu_set_register('A', 0xff)
#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd5)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpAbsolute(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xcd)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpAbsoluteX(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xdd)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpAbsoluteY(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_set_register('Y', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd9)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpIndirectX(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc1)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x87)
#     self.memory_set(0x0086, 0x00)
#     self.memory_set(0x0087, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CmpIndirectY(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_set_register('Y', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd1)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x86)
#     self.memory_set(0x0085, 0x00)
#     self.memory_set(0x0087, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cmp_n_flag_set(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Cmp_n_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_Cmp_z_flag_set(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }

#     cpu.Registers.A = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cmp_z_flag_unset(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }

#     cpu.Registers.A = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0xff) // -1

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_CmpC_flag_set(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }

#     cpu.Registers.A = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0xfd) // -3

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_CmpC_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }

#     cpu.Registers.A = 0xfd // -3
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc9)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# // CPX

# def test_CpxImmediate(self):

#     self.cpu_set_register('X', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CpxZeroPage(self):

#     self.cpu_set_register('X', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe4)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CpxAbsolute(self):

#     self.cpu_set_register('X', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xec)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cpx_n_flag_set(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Cpx_n_flag_unset(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_Cpx_z_flag_set(self):

#     cpu.Registers.X = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cpx_z_flag_unset(self):

#     cpu.Registers.X = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_CpxC_flag_set(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_CpxC_flag_unset(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# // CPY

# def test_CpyImmediate(self):

#     self.cpu_set_register('Y', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CpyZeroPage(self):

#     self.cpu_set_register('Y', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc4)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_CpyAbsolute(self):

#     self.cpu_set_register('Y', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xcc)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0xff)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cpy_n_flag_set(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Cpy_n_flag_unset(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# def test_Cpy_z_flag_set(self):

#     cpu.Registers.Y = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Cpy_z_flag_unset(self):

#     cpu.Registers.Y = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_CpyC_flag_set(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x01)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_CpyC_flag_unset(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc0)
#     self.memory_set(0x0101, 0x02)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# // INC

# def test_IncZeroPage(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xfe)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0xff {
#         t.Error("Memory is not 0xff")
#     }


# def test_IncZeroPageX(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0xfe)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0xff {
#         t.Error("Memory is not 0xff")
#     }


# def test_IncAbsolute(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xee)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0xfe)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0xff {
#         t.Error("Memory is not 0xff")
#     }


# def test_IncAbsoluteX(self):

#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xfe)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0xfe)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0xff {
#         t.Error("Memory is not 0xff")
#     }


# def test_Inc_z_flag_set(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xff) // -1

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Inc_z_flag_unset(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x00)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Inc_n_flag_set(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Inc_n_flag_unset(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x00)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // INX

# def test_Inx(self):

#     cpu.Registers.X = 0xfe
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe8)

#     self.execute()

#     self.assertEquals(self.cpu_register('X'), 0xff)


# def test_Inx_z_flag_set(self):

#     self.cpu_set_register('X', 0xff) // -1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe8)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Inx_z_flag_unset(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe8)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Inx_n_flag_set(self):

#     cpu.Registers.X = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe8)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Inx_n_flag_unset(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xe8)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // INY

# def test_Iny(self):

#     cpu.Registers.Y = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc8)

#     self.execute()

#     if cpu.Registers.Y != 0xff {
#         t.Error("Register X is not 0xff")
#     }


# def test_Iny_z_flag_set(self):

#     self.cpu_set_register('Y', 0xff) // -1
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc8)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Iny_z_flag_unset(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc8)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Iny_n_flag_set(self):

#     cpu.Registers.Y = 0xfe // -2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc8)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Iny_n_flag_unset(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc8)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // DEC

# def test_DecZeroPage(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_DecZeroPageX(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_DecAbsolute(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xce)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_DecAbsoluteX(self):

#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xde)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_Dec_z_flag_set(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x01)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Dec_z_flag_unset(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Dec_n_flag_set(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x00)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Dec_n_flag_unset(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xc6)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x01)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // DEX

# def test_Dex(self):

#     cpu.Registers.X = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xca)

#     self.execute()

#     if cpu.Registers.X != 0x01 {
#         t.Error("Register X is not 0x01")
#     }


# def test_Dex_z_flag_set(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xca)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Dex_z_flag_unset(self):

#     cpu.Registers.X = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xca)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Dex_n_flag_set(self):

#     cpu.Registers.X = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xca)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Dex_n_flag_unset(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xca)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // DEY

# def test_Dey(self):

#     cpu.Registers.Y = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x88)

#     self.execute()

#     if cpu.Registers.Y != 0x01 {
#         t.Error("Register X is not 0x01")
#     }


# def test_Dey_z_flag_set(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x88)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Dey_z_flag_unset(self):

#     cpu.Registers.Y = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x88)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Dey_n_flag_set(self):

#     cpu.Registers.Y = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x88)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Dey_n_flag_unset(self):

#     self.cpu_set_register('Y', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x88)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // ASL

# def test_AslAccumulator(self):

#     cpu.Registers.A = 0x2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.A != 0x04 {
#         t.Error("Register A is not 0x04")
#     }


# def test_AslZeroPage(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x06)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x04 {
#         t.Error("Memory is not 0x04")
#     }


# def test_AslZeroPageX(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x16)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x04 {
#         t.Error("Memory is not 0x04")
#     }


# def test_AslAbsolute(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x04 {
#         t.Error("Memory is not 0x04")
#     }


# def test_AslAbsoluteX(self):

#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x1e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x04 {
#         t.Error("Memory is not 0x04")
#     }


# def test_AslC_flag_set(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_AslC_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_Asl_z_flag_set(self):

#     cpu.Registers.A = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Asl_z_flag_unset(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Asl_n_flag_set(self):

#     cpu.Registers.A = 0xfe
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Asl_n_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x0a)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // LSR

# def test_LsrAccumulator(self):

#     cpu.Registers.A = 0x2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.A != 0x01 {
#         t.Error("Register A is not 0x01")
#     }


# def test_LsrZeroPage(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x46)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_LsrZeroPageX(self):

#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x56)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_LsrAbsolute(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_LsrAbsoluteX(self):

#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x5e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }


# def test_LsrC_flag_set(self):

#     self.cpu_set_register('A', 0xff)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_LsrC_flag_unset(self):

#     cpu.Registers.A = 0x10
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_Lsr_z_flag_set(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Lsr_z_flag_unset(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# // def test_Lsr_n_flag_set(self): }
# // not tested, N bit always set to 0

# def test_Lsr_n_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4a)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // ROL

# def test_RolAccumulator(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x2
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.A != 0x05 {
#         t.Error("Register A is not 0x05")
#     }


# def test_RolZeroPage(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x26)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x05 {
#         t.Error("Memory is not 0x05")
#     }


# def test_RolZeroPageX(self):

#     cpu.Registers.P |= C
#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x36)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x05 {
#         t.Error("Memory is not 0x05")
#     }


# def test_RolAbsolute(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x05 {
#         t.Error("Memory is not 0x05")
#     }


# def test_RolAbsoluteX(self):

#     cpu.Registers.P |= C
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x3e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x02)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x05 {
#         t.Error("Memory is not 0x05")
#     }


# def test_RolC_flag_set(self):

#     cpu.Registers.A = 0x80
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_RolC_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_Rol_z_flag_set(self):

#     cpu.Registers.A = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Rol_z_flag_unset(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Rol_n_flag_set(self):

#     cpu.Registers.A = 0xfe
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Rol_n_flag_unset(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x2a)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // ROR

# def test_RorAccumulator(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0x08
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.A != 0x84 {
#         t.Error("Register A is not 0x84")
#     }


# def test_RorZeroPage(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x66)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0084, 0x08)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x84 {
#         t.Error("Memory is not 0x84")
#     }


# def test_RorZeroPageX(self):

#     cpu.Registers.P |= C
#     cpu.Registers.X = 0x01
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x76)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0085, 0x08)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x84 {
#         t.Error("Memory is not 0x84")
#     }


# def test_RorAbsolute(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x08)

#     self.execute()

#     if cpu.Memory.Fetch(0x0084) != 0x84 {
#         t.Error("Memory is not 0x84")
#     }


# def test_RorAbsoluteX(self):

#     cpu.Registers.P |= C
#     self.cpu_set_register('X', 1)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x7e)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0085, 0x08)

#     self.execute()

#     if cpu.Memory.Fetch(0x0085) != 0x84 {
#         t.Error("Memory is not 0x84")
#     }


# def test_RorC_flag_set(self):

#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# def test_RorC_flag_unset(self):

#     cpu.Registers.A = 0x10
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# def test_Ror_z_flag_set(self):

#     cpu.Registers.A = 0x00
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&Z == 0 {
#         t.Error("Z flag is not set")
#     }


# def test_Ror_z_flag_unset(self):

#     cpu.Registers.A = 0x02
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&Z != 0 {
#         t.Error("Z flag is set")
#     }


# def test_Ror_n_flag_set(self):

#     cpu.Registers.P |= C
#     cpu.Registers.A = 0xfe
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&N == 0 {
#         t.Error("N flag is not set")
#     }


# def test_Ror_n_flag_unset(self):

#     cpu.Registers.P &^= C
#     self.cpu_set_register('A', 0x01)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6a)

#     self.execute()

#     if cpu.Registers.P&N != 0 {
#         t.Error("N flag is set")
#     }


# // JMP

# def test_JmpAbsolute(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x4c)
#     self.memory_set(0x0101, 0xff)
#     self.memory_set(0x0102, 0x01)

#     self.execute()

#     if cpu.Registers.PC != 0x01ff {
#         t.Error("Register PC is not 0x01ff")
#     }


# def test_JmpIndirect(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x6c)
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x01)
#     self.memory_set(0x0184, 0xff)
#     self.memory_set(0x0185, 0xff)

#     self.execute()

#     if cpu.Registers.PC != 0xffff {
#         t.Error("Register PC is not 0xffff")
#     }


# // JSR

# def test_Jsr(self):

#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x20)
#     self.memory_set(0x0101, 0xff)
#     self.memory_set(0x0102, 0x01)

#     self.execute()

#     if cpu.Registers.PC != 0x01ff {
#         t.Error("Register PC is not 0x01ff")
#     }

#     if cpu.Memory.Fetch(0x01fd) != 0x01 {
#         t.Error("Memory is not 0x01")
#     }

#     if cpu.Memory.Fetch(0x01fc) != 0x02 {
#         t.Error("Memory is not 0x02")
#     }



#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x20) // JSR
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0084, 0x60) // RTS

#     self.execute()
#     self.execute()

#     if cpu.Registers.PC != 0x0103 {
#         t.Error("Register PC is not 0x0103")
#     }

#     if cpu.Registers.SP != 0xfd {
#         t.Error("Register SP is not 0xfd")
#     }



#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x20) // JSR $0084
#     self.memory_set(0x0101, 0x84)
#     self.memory_set(0x0102, 0x00)
#     self.memory_set(0x0103, 0xa9) // LDA #$ff
#     self.memory_set(0x0104, 0xff)
#     self.memory_set(0x0105, 0x02) // illegal opcode
#     self.memory_set(0x0084, 0x60) // RTS

#     cpu.Run()

#     if cpu.Registers.A != 0xff {
#         t.Error("Register A is not 0xff")
#     }



# // RTS

# def test_Rts(self):

#     self.cpu_pc(0x0100)
#     cpu.push16(0x0102)

#     self.memory_set(0x0100, 0x60)

#     self.execute()

#     if cpu.Registers.PC != 0x0103 {
#         t.Error("Register PC is not 0x0103")
#     }


# // BCC

# def test_Bcc(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x90)

#     cycles, _ = self.execute()

#     if cycles != 2 {
#         t.Error("Cycles is not 2")
#     }

#     if cpu.Registers.PC != 0x0102 {
#         t.Error("Register PC is not 0x0102")
#     }

#     cpu.Registers.P &^= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x90)
#     self.memory_set(0x0101, 0x02) // +2

#     cycles, _ = self.execute()

#     if cycles != 3 {
#         t.Error("Cycles is not 3")
#     }

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P &^= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x90)
#     self.memory_set(0x0101, 0xfd) // -3

#     cycles, _ = self.execute()

#     if cycles != 4 {
#         t.Error("Cycles is not 4")
#     }

#     if cpu.Registers.PC != 0x00ff {
#         t.Error("Register PC is not 0x00ff")
#     }


# // BCS

# def test_Bcs(self):

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xb0)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xb0)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BEQ

# def test_Beq(self):

#     cpu.Registers.P |= Z
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf0)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P |= Z
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf0)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BMI

# def test_Bmi(self):

#     cpu.Registers.P |= N
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x30)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P |= N
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x30)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BNE

# def test_Bne(self):

#     cpu.Registers.P &^= Z
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd0)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P &^= Z
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd0)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BPL

# def test_Bpl(self):

#     cpu.Registers.P &^= N
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x10)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P &^= N
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x10)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BVC

# def test_Bvc(self):

#     cpu.Registers.P &^= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x50)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P &^= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x50)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // BVS

# def test_Bvs(self):

#     cpu.Registers.P |= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x70)
#     self.memory_set(0x0101, 0x02) // +2

#     self.execute()

#     if cpu.Registers.PC != 0x0104 {
#         t.Error("Register PC is not 0x0104")
#     }

#     cpu.Registers.P |= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x70)
#     self.memory_set(0x0101, 0xfe) // -2

#     self.execute()

#     if cpu.Registers.PC != 0x0100 {
#         t.Error("Register PC is not 0x0100")
#     }


# // CLC

# def test_Clc(self):

#     cpu.Registers.P &^= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x18)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x18)

#     self.execute()

#     if cpu.Registers.P&C != 0 {
#         t.Error("C flag is set")
#     }


# // CLD

# def test_Cld(self):

#     cpu.Registers.P &^= D
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd8)

#     self.execute()

#     if cpu.Registers.P&D != 0 {
#         t.Error("D flag is set")
#     }

#     cpu.Registers.P |= D
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xd8)

#     self.execute()

#     if cpu.Registers.P&D != 0 {
#         t.Error("D flag is set")
#     }


# // CLI

# def test_Cli(self):

#     cpu.Registers.P &^= I
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x58)

#     self.execute()

#     if cpu.Registers.P&I != 0 {
#         t.Error("I flag is set")
#     }

#     cpu.Registers.P |= I
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x58)

#     self.execute()

#     if cpu.Registers.P&I != 0 {
#         t.Error("I flag is set")
#     }


# // CLV

# def test_Clv(self):

#     cpu.Registers.P &^= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xb8)

#     self.execute()

#     if cpu.Registers.P&V != 0 {
#         t.Error("V flag is set")
#     }

#     cpu.Registers.P |= V
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xb8)

#     self.execute()

#     if cpu.Registers.P&V != 0 {
#         t.Error("V flag is set")
#     }


# // SEC

# def test_Sec(self):

#     cpu.Registers.P &^= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x38)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }

#     cpu.Registers.P |= C
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x38)

#     self.execute()

#     if cpu.Registers.P&C == 0 {
#         t.Error("C flag is not set")
#     }


# // SED

# def test_Sed(self):

#     cpu.Registers.P &^= D
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf8)

#     self.execute()

#     if cpu.Registers.P&D == 0 {
#         t.Error("D flag is not set")
#     }

#     cpu.Registers.P |= D
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0xf8)

#     self.execute()

#     if cpu.Registers.P&D == 0 {
#         t.Error("D flag is not set")
#     }


# // SEI

# def test_Sei(self):

#     cpu.Registers.P &^= I
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x78)

#     self.execute()

#     if cpu.Registers.P&I == 0 {
#         t.Error("I flag is not set")
#     }

#     cpu.Registers.P |= I
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x78)

#     self.execute()

#     if cpu.Registers.P&I == 0 {
#         t.Error("I flag is not set")
#     }


# // BRK

# def test_Brk(self):

#     cpu.Registers.P = 0xff & (^B)
#     self.cpu_pc(0x0100)

#     self.memory_set(0x0100, 0x00)
#     self.memory_set(0xfffe, 0xff)
#     self.memory_set(0xffff, 0x01)

#     self.execute()

#     if cpu.pull() != 0xff {
#         t.Error("Memory is not 0xff")
#     }

#     if cpu.pull16() != 0x0102 {
#         t.Error("Memory is not 0x0102")
#     }

#     if cpu.Registers.PC != 0x01ff {
#         t.Error("Register PC is not 0x01ff")
#     }


# // RTI

# def test_Rti(self):

#     self.cpu_pc(0x0100)
#     cpu.push16(0x0102)
#     cpu.push(0x03)

#     self.memory_set(0x0100, 0x40)

#     self.execute()

#     if cpu.Registers.P != 0x23 {
#         t.Error("Register P is not 0x23")
#     }

#     if cpu.Registers.PC != 0x0102 {
#         t.Error("Register PC is not 0x0102")
#     }


# // Rom

# def test_Rom(self):

#     cpu.DisableDecimalMode()

#     cpu.Registers.P = 0x24
#     cpu.Registers.SP = 0xfd
#     cpu.Registers.PC = 0xc000

#     cpu.Memory.(*BasicMemory).load("test-roms/nestest/nestest.nes")

#     self.memory_set(0x4004, 0xff)
#     self.memory_set(0x4005, 0xff)
#     self.memory_set(0x4006, 0xff)
#     self.memory_set(0x4007, 0xff)
#     self.memory_set(0x4015, 0xff)

#     err := cpu.Run()

#     if err != nil {
#         switch err.(type) {
#         case BrkOpCodeError:
#         default:
#             t.Error("Error during Run\n")
#         }
#     }

#     if cpu.Memory.Fetch(0x0002) != 0x00 {
#         t.Error("Memory 0x0002 is not 0x00")
#     }

#     if cpu.Memory.Fetch(0x0003) != 0x00 {
#         t.Error("Memory 0x0003 is not 0x00")
#     }


# // Irq

# def test_Irq(self):

#     cpu.Registers.P = 0xfb
#     self.cpu_pc(0x0100)

#     cpu.Interrupt(Irq, true)
#     self.memory_set(0xfffe, 0x40)
#     self.memory_set(0xffff, 0x01)

#     cpu.PerformInterrupts()

#     if cpu.pull() != 0xfb {
#         t.Error("Memory is not 0xfb")
#     }

#     if cpu.pull16() != 0x0100 {
#         t.Error("Memory is not 0x0100")
#     }

#     if cpu.Registers.PC != 0x0140 {
#         t.Error("Register PC is not 0x0140")
#     }

#     if cpu.GetInterrupt(Irq) {
#         t.Error("Interrupt is set")
#     }


# // Nmi

# def test_Nmi(self):

#     cpu.Registers.P = 0xff
#     self.cpu_pc(0x0100)

#     cpu.Interrupt(Nmi, true)
#     self.memory_set(0xfffa, 0x40)
#     self.memory_set(0xfffb, 0x01)

#     cpu.PerformInterrupts()

#     if cpu.pull() != 0xff {
#         t.Error("Memory is not 0xff")
#     }

#     if cpu.pull16() != 0x0100 {
#         t.Error("Memory is not 0x0100")
#     }

#     if cpu.Registers.PC != 0x0140 {
#         t.Error("Register PC is not 0x0140")
#     }

#     if cpu.GetInterrupt(Nmi) {
#         t.Error("Interrupt is set")
#     }


# // Rst

# def test_Rst(self):

#     self.cpu_pc(0x0100)

#     cpu.Interrupt(Rst, true)
#     self.memory_set(0xfffc, 0x40)
#     self.memory_set(0xfffd, 0x01)

#     cpu.PerformInterrupts()

#     if cpu.Registers.PC != 0x0140 {
#         t.Error("Register PC is not 0x0140")
#     }

#     if cpu.GetInterrupt(Rst) {
#         t.Error("Interrupt is set")
#     }

