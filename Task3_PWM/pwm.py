from pygmyhdl import *


@chunk
def pwm_simple(clk_i, pwm_o, threshold):

    cnt = Bus(len(threshold), name='cnt')  # Create a counter with the same number of bits as the threshold.

    # naliczanie licznika z zegarem
    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1

    # ustawienie wyjscia pwm zaleznosci czy licznik przekroczyl ustawiony threshold
    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold


@chunk
def pwm_less_simple(clk_i, pwm_o, threshold, duration):
    # The log2 of the pulse duration determines the number of bits needed
    # in the counter. The log2 value is rounded up to the next integer value.
    import math
    length = math.ceil(math.log(duration, 2))
    cnt = Bus(length, name='cnt')

    # Augment the counter with a comparator to adjust the pulse duration.
    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
        # Reset the counter to zero once it reaches one less than the desired duration.
        # So if the duration is 3, the counter will count 0, 1, 2, 0, 1, 2...
        if cnt == duration - 1:
            cnt.next = 0

    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold


@chunk
def pwm_glitchless(clk_i, pwm_o, threshold, interval):
    import math
    length = math.ceil(math.log(interval, 2))
    cnt = Bus(length)

    threshold_r = Bus(length, name='threshold_r')  # Create a register to hold the threshold value.

    @seq_logic(clk_i.posedge)
    def cntr_logic():
        cnt.next = cnt + 1
        if cnt == interval - 1:
            cnt.next = 0
            threshold_r.next = threshold  # The threshold only changes at the end of a pulse.

    @comb_logic
    def output_logic():
        pwm_o.next = cnt < threshold_r

def test_bench(num_cycles):
    clk.next = 0
    threshold.next = 3  # Start with threshold of 3.
    yield delay(1)
    for cycle in range(num_cycles):
        clk.next = 0
        # Raise the threshold to 8 after 15 cycles.
        if cycle >= 14:
            threshold.next = 8
        yield delay(1)
        clk.next = 1
        yield delay(1)

initialize()
clk = Wire(name='clk')
pwm = Wire(name='pwm')
threshold = Bus(4, name='threshold')
pwm_less_simple(clk, pwm, threshold, 10)

simulate(test_bench(20))
show_waveforms(tick=True, start_time=19)

#Utworz .v i .vhd z ostatniego pwm
toVerilog(pwm_glitchless, clk_i=clk, pwm_o=pwm, threshold=threshold, interval=19)
toVHDL(pwm_glitchless, clk_i=clk, pwm_o=pwm, threshold=threshold, interval=19)