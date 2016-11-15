"""Contains a number of useful physical constants"""
from numpy import pi

c = 299792e3        # Speed of light in m/s
m_e = 9.10938e-31   # Electron mass in kg
m_p = 1.672622e-27  # Proton mass in kg
m_p_m_e = 1836.153  # m_p/m_e
e_0 = 8.854e-12     # Permittivity of free space in Farads/meter
q_e = 1.6021766e-19  # Electron charge in coulombs
mu_0 = 4 * pi * 1e-7
Re = 6367.4447 * 1e3    # Earth radius in m
Rmoon = 1737.5 * 1e3    # Moon radius in m
k_B = 1.38065 * 1e-23   # Boltzmann constant in J/Kelvin
AU_km = 1.496 * 1e8     # Astronomical unit in km
Rs_km = 6.955 * 1e5     # Sun radius in km
solar_rot_period_d = 25.38    # Solar rotation period in days
solar_rot_period_s = solar_rot_period_d * 24 * 60 * 60  # Solar rotation period in seconds
