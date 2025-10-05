"""
Data module for Asteroid Impact Visualizer
Contains asteroid and city population databases
"""

from .asteroid_data import SOLAR_SYSTEM_ASTEROIDS, COMETS, CHICXULUB_IMPACTOR
from .city_data import MAJOR_CITIES_POPULATION

__all__ = [
    'SOLAR_SYSTEM_ASTEROIDS',
    'COMETS',
    'CHICXULUB_IMPACTOR',
    'MAJOR_CITIES_POPULATION'
]

