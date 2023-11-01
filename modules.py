import prop
from sqlite import read_stream, write_stream, write_block
import numpy as np
from scipy import optimize


def root(func, a, root_tol):
    x = float(optimize.root(func, a, tol = root_tol).x)
    return x


class RHE:
    def __init__(self, stream11, stream12, stream21, stream22, T12, dT, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)
        self.T12 = T12
        self.dT = dT

    def calc(self):

        T11 = read_stream(self.stream11)['T']
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        cp = float(read_stream(self.stream11)['X'])
        T12 = self.T12
        H12 = T12*cp

        T21 = read_stream(self.stream21)['T']
        P21 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        step = (H11 - H12) / self.h_steps

        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = h11 / cp
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dT - min_dt

        G2 = root(G2_func, 0.1*G1*(H11-H12)/(prop.t_p(T11, P21, fluid2)["H"]-H21), self.root_tolerance)

        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = h11/cp
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT[:-1])

        T22 = t2[0]
        T12 = t1[-1]
        S12 = 0
        Q12 = 0
        H22 = prop.t_p(T22, P21, fluid2)["H"]
        S22 = prop.t_p(T22, P21, fluid2)["S"]
        Q22 = prop.t_p(T22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, cp)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('RHE', Q[-1], min_dt)
        pass


class Pump:
    def __init__(self, stream1, stream2, p_out, kpd_pump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.kpd_pump
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H2 - H1)
        write_block('PUMP', N, 0)
        pass


class Turb:
    def __init__(self, stream1, stream2, p_out, kpd_turb):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_turb = kpd_turb

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 - (H1 - H2t) * self.kpd_turb
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H1 - H2)
        write_block('T', N, 0)
        pass


class HTR:
    def __init__(self, stream11, stream12, stream21, stream22, dt, root_tolerance, h_steps, dt_RHE):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)
        self.dt_RHE = dt_RHE

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        T11 = read_stream(self.stream11)['T']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']

        P21 = read_stream(self.stream21)['P']
        T21 = read_stream(self.stream21)['T']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']
        fluid2 = read_stream(self.stream21)['X']

        def T22_func(T22):
            T22 = min(T22, read_stream('RHE-R')['T']-self.dt_RHE)
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            step = (H22 - H21) / self.h_steps
            for i in range(self.h_steps + 1):
                t2[i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + step
                    dQ = G2 * (h22 - h21)
                    h21 = h22
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                    h11 = h12
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt

        if T21 > T11:
            T22 = T21
            T12 = T11
            H12 = prop.t_p(T12, P11, fluid1)["H"]
            S12 = prop.t_p(T12, P11, fluid1)["S"]
            Q12 = prop.t_p(T12, P11, fluid1)["Q"]
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            S22 = prop.t_p(T22, P21, fluid2)["S"]
            Q22 = prop.t_p(T22, P21, fluid2)["Q"]
            write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
            write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
            write_block('HTR', 0, 0)
            pass

        T22 = root(T22_func, 1, self.root_tolerance)
        if T22 > read_stream('RHE-R')['T']-self.dt_RHE:
            T22 = read_stream('RHE-R')['T']-self.dt_RHE

        H22 = prop.t_p(T22, P21, fluid2)["H"]
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        step = (H22 - H21) / self.h_steps
        for i in range(self.h_steps + 1):
            t2[i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + step
                dQ = G2 * (h22 - h21)
                h21 = h22
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                h11 = h12
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[-1]
        T12 = t1[0]

        H12 = prop.t_p(T12, P11, fluid1)["H"]
        S12 = prop.t_p(T12, P11, fluid1)["S"]
        Q12 = prop.t_p(T12, P11, fluid1)["Q"]
        H22 = prop.t_p(T22, P21, fluid2)["H"]
        S22 = prop.t_p(T22, P21, fluid2)["S"]
        Q22 = prop.t_p(T22, P21, fluid2)["Q"]
        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('HTR', Q[-1], min_dt)
        pass


class LTR:
    def __init__(self, stream11, stream12, stream21, stream22, dt, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P11 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        T11 = read_stream(self.stream11)['T']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']

        P21 = read_stream(self.stream21)['P']
        T21 = read_stream(self.stream21)['T']
        H21 = read_stream(self.stream21)['H']
        G2 = read_stream(self.stream21)['G']
        fluid2 = read_stream(self.stream21)['X']

        def T22_func(T22):
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            step = (H22 - H21) / self.h_steps
            for i in range(self.h_steps + 1):
                t2[i] = prop.h_p(h21, P21, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + step
                    dQ = G2 * (h22 - h21)
                    h21 = h22
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                    h11 = h12
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt

        if T21 < T11:
            T22 = root(T22_func, 1, self.root_tolerance)
        else:
            T22 = T21
            T12 = T11
            H12 = prop.t_p(T12, P11, fluid1)["H"]
            S12 = prop.t_p(T12, P11, fluid1)["S"]
            Q12 = prop.t_p(T12, P11, fluid1)["Q"]
            H22 = prop.t_p(T22, P21, fluid2)["H"]
            S22 = prop.t_p(T22, P21, fluid2)["S"]
            Q22 = prop.t_p(T22, P21, fluid2)["Q"]
            write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
            write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
            write_block('LTR', 0, 0)

        H22 = prop.t_p(T22, P21, fluid2)["H"]
        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        step = (H22 - H21) / self.h_steps
        for i in range(self.h_steps + 1):
            t2[i] = prop.h_p(h21, P21, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + step
                dQ = G2 * (h22 - h21)
                h21 = h22
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t1[self.h_steps - i] = prop.h_p(h11, P11, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G1
                h11 = h12
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[-1]
        T12 = t1[0]

        H12 = prop.t_p(T12, P11, fluid1)["H"]
        S12 = prop.t_p(T12, P11, fluid1)["S"]
        Q12 = prop.t_p(T12, P11, fluid1)["Q"]
        H22 = prop.t_p(T22, P21, fluid2)["H"]
        S22 = prop.t_p(T22, P21, fluid2)["S"]
        Q22 = prop.t_p(T22, P21, fluid2)["Q"]

        write_stream(self.stream12, T12, P11, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream22, T22, P21, H22, S22, Q22, G2, fluid2)
        write_block('LTR', Q[-1], min_dt)
        pass


class SPLIT:
    def __init__(self, stream1, stream21, stream22, x):
        self.stream1 = stream1
        self.stream21 = stream21
        self.stream22 = stream22
        self.x = x

    def calc(self):
        self.G1 = read_stream(self.stream1)['G']
        G21 = self.G1*self.x
        G22 = self.G1*(1-self.x)
        write_stream(self.stream21,read_stream(self.stream1)['T'],read_stream(self.stream1)['P'],read_stream(self.stream1)['H'],read_stream(self.stream1)['S'],read_stream(self.stream1)['Q'],G21, read_stream(self.stream1)['X'])
        write_stream(self.stream22,read_stream(self.stream1)['T'],read_stream(self.stream1)['P'],read_stream(self.stream1)['H'],read_stream(self.stream1)['S'],read_stream(self.stream1)['Q'],G22, read_stream(self.stream1)['X'])


class C:
    def __init__(self, stream11, stream12, stream21, stream22, T12, dt, root_tolerance, h_steps):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream21 = stream21
        self.stream22 = stream22
        self.dt = dt
        self.T12 = T12
        self.root_tolerance = root_tolerance
        self.h_steps = int(h_steps)

    def calc(self):
        P1 = read_stream(self.stream11)['P']
        H11 = read_stream(self.stream11)['H']
        G1 = read_stream(self.stream11)['G']
        fluid1 = read_stream(self.stream11)['X']
        T12 = self.T12
        H12 =prop.t_p(T12,P1, fluid1)['H']

        P2 = read_stream(self.stream21)['P']
        H21 = read_stream(self.stream21)['H']
        fluid2 = read_stream(self.stream21)['X']
        step = (H11 - H12) / self.h_steps
        def G2_func(G2):
            t1 = np.zeros(self.h_steps + 1)
            t2 = np.zeros(self.h_steps + 1)
            Q = np.zeros(self.h_steps + 1)
            h11 = H11
            h21 = H21
            for i in range(self.h_steps + 1):
                t1[i] = prop.h_p(h11, P1, fluid1)["T"]
                if i < self.h_steps:
                    h12 = h11 - step
                    dQ = G1 * (h11 - h12)
                    h11 = h12
                    Q[i + 1] = Q[i] + dQ
            for i in range(self.h_steps + 1):
                t2[self.h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
                if i < self.h_steps:
                    h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                    h21 = h22
            DT = t1 - t2
            min_dt = min(DT)
            return self.dt - min_dt
        G2 = root(G2_func, G1*(H11-H12)/(prop.t_p(T12, P2, fluid2)["H"]-H21), self.root_tolerance)

        t1 = np.zeros(self.h_steps + 1)
        t2 = np.zeros(self.h_steps + 1)
        Q = np.zeros(self.h_steps + 1)
        h11 = H11
        h21 = H21
        for i in range(self.h_steps + 1):
            t1[i] = prop.h_p(h11, P1, fluid1)["T"]
            if i < self.h_steps:
                h12 = h11 - step
                dQ = G1 * (h11 - h12)
                h11 = h12
                Q[i + 1] = Q[i] + dQ
        for i in range(self.h_steps + 1):
            t2[self.h_steps - i] = prop.h_p(h21, P2, fluid2)["T"]
            if i < self.h_steps:
                h22 = h21 + (Q[self.h_steps - i] - Q[self.h_steps - i - 1]) / G2
                h21 = h22
        DT = t1 - t2
        min_dt = min(DT)
        T22 = t2[0]
        Q12 = prop.t_p(T12, P1, fluid1)["Q"]
        H22 = prop.t_p(T22, P2, fluid2)["H"]
        S22 = prop.t_p(T22, P2, fluid2)["S"]
        Q22 = prop.t_p(T22, P2, fluid2)["Q"]
        T12 = prop.h_p(H12, P1, fluid1)["T"]
        S12 = prop.h_p(H12, P1, fluid1)["S"]
        T21 = prop.h_p(H21, P2, fluid2)["T"]
        S21 = prop.h_p(H21, P2, fluid2)["S"]
        Q21 = prop.h_p(H21, P2, fluid2)["Q"]
        write_stream(self.stream12, T12, P1, H12, S12, Q12, G1, fluid1)
        write_stream(self.stream21, T21, P2, H21, S21, Q21, G2, fluid2)
        write_stream(self.stream22, T22, P2, H22, S22, Q22, G2, fluid2)
        write_block('C', Q[-1], min_dt)
        pass


class MC:
    def __init__(self, stream1, stream2, p_out, kpd_pump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.kpd_pump
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H2 - H1)
        write_block('MC', N, 0)
        pass


class RC:
    def __init__(self, stream1, stream2, p_out, kpd_pump):
        self.stream1 = stream1
        self.stream2 = stream2
        self.p_out = p_out
        self.kpd_pump = kpd_pump

    def calc(self):
        H1 = read_stream(self.stream1)['H']
        S1 = read_stream(self.stream1)['S']
        G = read_stream(self.stream1)['G']
        fluid = read_stream(self.stream1)['X']
        H2t = prop.p_s(self.p_out, S1, fluid)["H"]
        H2 = H1 + (H2t - H1) / self.kpd_pump
        T2 = prop.h_p(H2, self.p_out, fluid)["T"]
        S2 = prop.h_p(H2, self.p_out, fluid)["S"]
        Q2 = prop.h_p(H2, self.p_out, fluid)["Q"]
        write_stream(self.stream2, T2, self.p_out, H2, S2, Q2, G, fluid)
        N = G * (H2 - H1)
        write_block('RC', N, 0)
        pass


class MIX:
    def __init__(self, stream11,stream12,stream2):
        self.stream11 = stream11
        self.stream12 = stream12
        self.stream2 = stream2

    def calc(self):
        G11 = read_stream(self.stream11)['G']
        G12 = read_stream(self.stream12)['G']
        H11 = read_stream(self.stream11)['H']
        H12 = read_stream(self.stream12)['H']
        fluid = read_stream(self.stream12)['X']
        P2 = (read_stream(self.stream11)['P'] + read_stream(self.stream12)['P'])/ 2
        G2 = G11 + G12
        H2 = (G11*H11 + G12*H12)/G2
        T2 = prop.h_p(H2,P2,fluid)['T']
        S2 = prop.h_p(H2,P2,fluid)['S']
        Q2 = prop.h_p(H2,P2,fluid)['Q']
        write_stream(self.stream2, T2, P2, H2, S2, Q2, G2, fluid)
