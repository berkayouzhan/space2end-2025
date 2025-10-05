"""
Major Cities Population Database
Contains population and density data for major cities worldwide
Used for impact risk assessment and casualty estimation
"""

MAJOR_CITIES_POPULATION = {
    # TÜRKİYE - Büyük Şehirler
    'İstanbul': {'lat': 41.01, 'lng': 28.98, 'population': 15840900, 'density': 2976},
    'Ankara': {'lat': 39.93, 'lng': 32.85, 'population': 5747325, 'density': 306},
    'İzmir': {'lat': 38.42, 'lng': 27.14, 'population': 4425789, 'density': 374},
    'Bursa': {'lat': 40.18, 'lng': 29.07, 'population': 3147818, 'density': 292},
    'Antalya': {'lat': 36.89, 'lng': 30.71, 'population': 2619832, 'density': 126},
    'Adana': {'lat': 37.00, 'lng': 35.32, 'population': 2258718, 'density': 158},
    'Konya': {'lat': 37.87, 'lng': 32.48, 'population': 2277017, 'density': 57},
    'Gaziantep': {'lat': 37.06, 'lng': 37.38, 'population': 2130432, 'density': 330},
    'Şanlıurfa': {'lat': 37.16, 'lng': 38.79, 'population': 2155805, 'density': 115},
    'Mersin': {'lat': 36.81, 'lng': 34.64, 'population': 1916432, 'density': 121},
    'Kocaeli': {'lat': 40.85, 'lng': 29.88, 'population': 2033441, 'density': 520},
    'Diyarbakır': {'lat': 37.91, 'lng': 40.24, 'population': 1783431, 'density': 118},
    'Hatay': {'lat': 36.40, 'lng': 36.35, 'population': 1686043, 'density': 307},
    'Manisa': {'lat': 38.62, 'lng': 27.43, 'population': 1468279, 'density': 110},
    'Kayseri': {'lat': 38.73, 'lng': 35.49, 'population': 1441523, 'density': 86},
    'Samsun': {'lat': 41.29, 'lng': 36.34, 'population': 1371081, 'density': 143},
    'Balıkesir': {'lat': 39.65, 'lng': 27.89, 'population': 1257590, 'density': 85},
    'Mardin': {'lat': 37.31, 'lng': 40.74, 'population': 880312, 'density': 81},
    'Van': {'lat': 38.49, 'lng': 43.38, 'population': 1149342, 'density': 59},
    'Kahramanmaraş': {'lat': 37.58, 'lng': 36.92, 'population': 1168163, 'density': 82},
    'Denizli': {'lat': 37.77, 'lng': 29.09, 'population': 1056332, 'density': 89},
    'Sakarya': {'lat': 40.76, 'lng': 30.40, 'population': 1042649, 'density': 213},
    'Eskişehir': {'lat': 39.78, 'lng': 30.52, 'population': 906396, 'density': 66},
    'Tekirdağ': {'lat': 40.98, 'lng': 27.51, 'population': 1081065, 'density': 168},
    'Trabzon': {'lat': 41.00, 'lng': 39.72, 'population': 811901, 'density': 173},
    'Malatya': {'lat': 38.35, 'lng': 38.31, 'population': 809114, 'density': 65},
    
    # Avrupa
    'Moskova': {'lat': 55.75, 'lng': 37.62, 'population': 13200000, 'density': 5100},
    'Londra': {'lat': 51.51, 'lng': -0.13, 'population': 9540576, 'density': 5701},
    'Paris': {'lat': 48.86, 'lng': 2.35, 'population': 11020000, 'density': 20641},
    'Berlin': {'lat': 52.52, 'lng': 13.40, 'population': 3677472, 'density': 4115},
    'Madrid': {'lat': 40.42, 'lng': -3.70, 'population': 6700000, 'density': 5400},
    'Roma': {'lat': 41.90, 'lng': 12.50, 'population': 4342212, 'density': 2236},
    'Atina': {'lat': 37.98, 'lng': 23.73, 'population': 3168846, 'density': 7984},
    
    # Asya
    'Tokyo': {'lat': 35.68, 'lng': 139.65, 'population': 37400000, 'density': 6168},
    'Delhi': {'lat': 28.70, 'lng': 77.10, 'population': 32900000, 'density': 11320},
    'Şangay': {'lat': 31.23, 'lng': 121.47, 'population': 28500000, 'density': 3826},
    'Pekin': {'lat': 39.90, 'lng': 116.41, 'population': 21500000, 'density': 1311},
    'Mumbai': {'lat': 19.08, 'lng': 72.88, 'population': 20700000, 'density': 20680},
    'Seul': {'lat': 37.57, 'lng': 126.98, 'population': 9776000, 'density': 16364},
    'Jakarta': {'lat': -6.21, 'lng': 106.85, 'population': 10770000, 'density': 16494},
    'Manila': {'lat': 14.60, 'lng': 120.98, 'population': 14158573, 'density': 46178},
    'Bangkok': {'lat': 13.76, 'lng': 100.50, 'population': 10722000, 'density': 5300},
    'Tahran': {'lat': 35.69, 'lng': 51.42, 'population': 9135000, 'density': 11800},
    'Kahire': {'lat': 30.04, 'lng': 31.24, 'population': 21300000, 'density': 19376},
    
    # Amerika
    'New York': {'lat': 40.71, 'lng': -74.01, 'population': 18604000, 'density': 10194},
    'Los Angeles': {'lat': 34.05, 'lng': -118.24, 'population': 12460000, 'density': 3276},
    'Mexico City': {'lat': 19.43, 'lng': -99.13, 'population': 21900000, 'density': 6000},
    'São Paulo': {'lat': -23.55, 'lng': -46.63, 'population': 22430000, 'density': 7216},
    'Buenos Aires': {'lat': -34.60, 'lng': -58.38, 'population': 15370000, 'density': 14308},
    'Bogotá': {'lat': 4.71, 'lng': -74.07, 'population': 11170000, 'density': 4310},
    'Lima': {'lat': -12.05, 'lng': -77.04, 'population': 11180000, 'density': 3008},
    
    # Afrika
    'Lagos': {'lat': 6.45, 'lng': 3.40, 'population': 15380000, 'density': 13128},
    'Kinshasa': {'lat': -4.32, 'lng': 15.31, 'population': 15628000, 'density': 1300},
    'Johannesburg': {'lat': -26.20, 'lng': 28.05, 'population': 5926000, 'density': 2364},
    
    # Okyanusya
    'Sidney': {'lat': -33.87, 'lng': 151.21, 'population': 5367000, 'density': 433},
}

