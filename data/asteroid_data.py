"""
Asteroid and Comet Database
Contains real astronomical data for Near-Earth Objects (NEOs), main belt asteroids, and comets
"""

# ============================================================================
# SOLAR SYSTEM ASTEROIDS DATABASE
# ============================================================================

SOLAR_SYSTEM_ASTEROIDS = {
    'apophis': {
        'id': '99942',
        'name': '99942 Apophis',
        'diameter_m': 370,
        'velocity_ms': 12600,
        'velocity_kmh': 45360,
        'is_hazardous': True,
        'absolute_magnitude': 19.7,
        'orbital_period': 323.6,
        'miss_distance_km': 31000,
        'description': 'Potansiyel tehlikeli asteroid - 2029 ve 2036 yakın geçişleri'
    },
    'bennu': {
        'id': '101955',
        'name': '101955 Bennu',
        'diameter_m': 490,
        'velocity_ms': 27700,
        'velocity_kmh': 99720,
        'is_hazardous': True,
        'absolute_magnitude': 20.9,
        'orbital_period': 436.6,
        'miss_distance_km': 750000,
        'description': 'OSIRIS-REx hedefi, numune alındı'
    },
    'ryugu': {
        'id': '162173',
        'name': '162173 Ryugu',
        'diameter_m': 900,
        'velocity_ms': 31600,
        'velocity_kmh': 113760,
        'is_hazardous': False,
        'absolute_magnitude': 19.3,
        'orbital_period': 473.9,
        'miss_distance_km': 3000000,
        'description': 'Hayabusa2 hedefi, başarıyla numune toplandı'
    },
    'ceres': {
        'id': '1',
        'name': '1 Ceres',
        'diameter_m': 940000,
        'velocity_ms': 17900,
        'velocity_kmh': 64440,
        'is_hazardous': False,
        'absolute_magnitude': 3.36,
        'orbital_period': 1680,
        'miss_distance_km': 263000000,
        'description': 'Cüce gezegen, en büyük asteroid'
    },
    'vesta': {
        'id': '4',
        'name': '4 Vesta',
        'diameter_m': 525000,
        'velocity_ms': 19300,
        'velocity_kmh': 69480,
        'is_hazardous': False,
        'absolute_magnitude': 3.20,
        'orbital_period': 1325,
        'miss_distance_km': 177000000,
        'description': 'İkinci en büyük asteroid, Dawn uzay aracı ziyaret etti'
    },
    'pallas': {
        'id': '2',
        'name': '2 Pallas',
        'diameter_m': 512000,
        'velocity_ms': 17600,
        'velocity_kmh': 63360,
        'is_hazardous': False,
        'absolute_magnitude': 4.13,
        'orbital_period': 1686,
        'miss_distance_km': 235000000,
        'description': 'Üçüncü en büyük asteroid'
    },
    'eros': {
        'id': '433',
        'name': '433 Eros',
        'diameter_m': 16840,
        'velocity_ms': 24300,
        'velocity_kmh': 87480,
        'is_hazardous': False,
        'absolute_magnitude': 10.4,
        'orbital_period': 643,
        'miss_distance_km': 22000000,
        'description': 'İlk incelenen NEA, NEAR Shoemaker indi (2001)'
    },
    'itokawa': {
        'id': '25143',
        'name': '25143 Itokawa',
        'diameter_m': 535,
        'velocity_ms': 25300,
        'velocity_kmh': 91080,
        'is_hazardous': False,
        'absolute_magnitude': 19.2,
        'orbital_period': 556,
        'miss_distance_km': 1500000,
        'description': 'Hayabusa misyonu hedefi, ilk asteroid numunesini getirdi'
    },
    '2013tv135': {
        'id': '2013 TV135',
        'name': '2013 TV135',
        'diameter_m': 400,
        'velocity_ms': 14800,
        'velocity_kmh': 53280,
        'is_hazardous': True,
        'absolute_magnitude': 20.3,
        'orbital_period': 798,
        'miss_distance_km': 6700000,
        'description': 'Potansiyel tehlikeli asteroid'
    },
    'didymos': {
        'id': '65803',
        'name': '65803 Didymos',
        'diameter_m': 780,
        'velocity_ms': 19800,
        'velocity_kmh': 71280,
        'is_hazardous': True,
        'absolute_magnitude': 18.4,
        'orbital_period': 770,
        'miss_distance_km': 5900000,
        'description': 'DART misyonu hedefi (2022) - gezegen savunma testi'
    },
    'psyche': {
        'id': '16',
        'name': '16 Psyche',
        'diameter_m': 226000,
        'velocity_ms': 18200,
        'velocity_kmh': 65520,
        'is_hazardous': False,
        'absolute_magnitude': 5.9,
        'orbital_period': 1826,
        'miss_distance_km': 300000000,
        'description': 'Metalik asteroid, NASA Psyche misyon hedefi'
    },
    'hygiea': {
        'id': '10',
        'name': '10 Hygiea',
        'diameter_m': 434000,
        'velocity_ms': 16700,
        'velocity_kmh': 60120,
        'is_hazardous': False,
        'absolute_magnitude': 5.43,
        'orbital_period': 2030,
        'miss_distance_km': 280000000,
        'description': 'Dördüncü en büyük asteroid'
    },
    'davida': {
        'id': '511',
        'name': '511 Davida',
        'diameter_m': 326000,
        'velocity_ms': 17100,
        'velocity_kmh': 61560,
        'is_hazardous': False,
        'absolute_magnitude': 6.22,
        'orbital_period': 1969,
        'miss_distance_km': 320000000,
        'description': 'C-tipi, karbon açısından zengin'
    },
    'interamnia': {
        'id': '704',
        'name': '704 Interamnia',
        'diameter_m': 310000,
        'velocity_ms': 17400,
        'velocity_kmh': 62640,
        'is_hazardous': False,
        'absolute_magnitude': 6.30,
        'orbital_period': 2030,
        'miss_distance_km': 295000000,
        'description': 'F-tipi, karanlık asteroid'
    },
    'europa': {
        'id': '52',
        'name': '52 Europa',
        'diameter_m': 302000,
        'velocity_ms': 18500,
        'velocity_kmh': 66600,
        'is_hazardous': False,
        'absolute_magnitude': 6.31,
        'orbital_period': 2044,
        'miss_distance_km': 290000000,
        'description': 'C-tipi asteroid (Jüpiter uydusu değil)'
    },
    'gaspra': {
        'id': '951',
        'name': '951 Gaspra',
        'diameter_m': 12200,
        'velocity_ms': 20800,
        'velocity_kmh': 74880,
        'is_hazardous': False,
        'absolute_magnitude': 11.46,
        'orbital_period': 1199,
        'miss_distance_km': 205000000,
        'description': 'İlk fotoğraflanan asteroid (Galileo, 1991)'
    },
    'mathilde': {
        'id': '253',
        'name': '253 Mathilde',
        'diameter_m': 52800,
        'velocity_ms': 19600,
        'velocity_kmh': 70560,
        'is_hazardous': False,
        'absolute_magnitude': 10.3,
        'orbital_period': 1590,
        'miss_distance_km': 250000000,
        'description': 'NEAR Shoemaker ziyaret etti (1997)'
    },
    'steins': {
        'id': '2867',
        'name': '2867 Šteins',
        'diameter_m': 5300,
        'velocity_ms': 21200,
        'velocity_kmh': 76320,
        'is_hazardous': False,
        'absolute_magnitude': 13.0,
        'orbital_period': 1355,
        'miss_distance_km': 215000000,
        'description': 'E-tipi, Rosetta ziyaret etti (2008)'
    },
    'lutetia': {
        'id': '21',
        'name': '21 Lutetia',
        'diameter_m': 100000,
        'velocity_ms': 19200,
        'velocity_kmh': 69120,
        'is_hazardous': False,
        'absolute_magnitude': 7.35,
        'orbital_period': 1454,
        'miss_distance_km': 225000000,
        'description': 'M-tipi, Rosetta ziyaret etti (2010)'
    },
    'phaethon': {
        'id': '3200',
        'name': '3200 Phaethon',
        'diameter_m': 5100,
        'velocity_ms': 30200,
        'velocity_kmh': 108720,
        'is_hazardous': True,
        'absolute_magnitude': 14.6,
        'orbital_period': 524,
        'miss_distance_km': 10000000,
        'description': 'Geminid meteor yağmurunun kaynağı'
    },
    'icarus': {
        'id': '1566',
        'name': '1566 Icarus',
        'diameter_m': 1400,
        'velocity_ms': 28900,
        'velocity_kmh': 104040,
        'is_hazardous': True,
        'absolute_magnitude': 16.9,
        'orbital_period': 409,
        'miss_distance_km': 6300000,
        'description': 'Güneşe çok yaklaşan asteroid'
    },
    'toutatis': {
        'id': '4179',
        'name': '4179 Toutatis',
        'diameter_m': 4600,
        'velocity_ms': 11000,
        'velocity_kmh': 39600,
        'is_hazardous': True,
        'absolute_magnitude': 15.3,
        'orbital_period': 1470,
        'miss_distance_km': 1500000,
        'description': 'Düzensiz şekilli, yakın geçişler yapan'
    },
    'geographos': {
        'id': '1620',
        'name': '1620 Geographos',
        'diameter_m': 5100,
        'velocity_ms': 14200,
        'velocity_kmh': 51120,
        'is_hazardous': True,
        'absolute_magnitude': 15.6,
        'orbital_period': 508,
        'miss_distance_km': 10000000,
        'description': 'Uzun silindir şeklinde'
    },
    'florence': {
        'id': '3122',
        'name': '3122 Florence',
        'diameter_m': 4900,
        'velocity_ms': 13500,
        'velocity_kmh': 48600,
        'is_hazardous': True,
        'absolute_magnitude': 14.1,
        'orbital_period': 859,
        'miss_distance_km': 7000000,
        'description': '2017 yakın geçişinde keşfedildi'
    },
    'vesta_4': {
        'id': '1981 ET3',
        'name': '1981 ET3',
        'diameter_m': 1800,
        'velocity_ms': 22400,
        'velocity_kmh': 80640,
        'is_hazardous': False,
        'absolute_magnitude': 16.4,
        'orbital_period': 1100,
        'miss_distance_km': 45000000,
        'description': 'Mars Trojan asteroid'
    },
    'atira': {
        'id': '163693',
        'name': '163693 Atira',
        'diameter_m': 4800,
        'velocity_ms': 27100,
        'velocity_kmh': 97560,
        'is_hazardous': False,
        'absolute_magnitude': 16.1,
        'orbital_period': 296,
        'miss_distance_km': 30000000,
        'description': 'Yörüngesi tamamen Dünya içinde'
    },
    'cruithne': {
        'id': '3753',
        'name': '3753 Cruithne',
        'diameter_m': 5000,
        'velocity_ms': 21700,
        'velocity_kmh': 78120,
        'is_hazardous': False,
        'absolute_magnitude': 15.1,
        'orbital_period': 364,
        'miss_distance_km': 12000000,
        'description': 'Dünya\'nın yarı-uydusu'
    },
    'golevka': {
        'id': '6489',
        'name': '6489 Golevka',
        'diameter_m': 530,
        'velocity_ms': 20500,
        'velocity_kmh': 73800,
        'is_hazardous': True,
        'absolute_magnitude': 19.2,
        'orbital_period': 1139,
        'miss_distance_km': 4800000,
        'description': 'Yarkovsky etkisi gözlemlendi'
    },
    'castalia': {
        'id': '4769',
        'name': '4769 Castalia',
        'diameter_m': 1400,
        'velocity_ms': 24800,
        'velocity_kmh': 89280,
        'is_hazardous': True,
        'absolute_magnitude': 16.9,
        'orbital_period': 1095,
        'miss_distance_km': 5200000,
        'description': 'İkili asteroid (iki loblu)'
    },
    'bacchus': {
        'id': '2063',
        'name': '2063 Bacchus',
        'diameter_m': 1100,
        'velocity_ms': 26400,
        'velocity_kmh': 95040,
        'is_hazardous': True,
        'absolute_magnitude': 17.6,
        'orbital_period': 1134,
        'miss_distance_km': 12000000,
        'description': 'Apollo grubu, S-tipi'
    }
}

# ============================================================================
# COMETS DATABASE
# ============================================================================

COMETS = {
    'halley': {
        'id': '1P/Halley',
        'name': "1P/Halley",
        'diameter_m': 11000,
        'velocity_ms': 70560,
        'velocity_kmh': 254016,
        'is_hazardous': False,
        'absolute_magnitude': 4.0,
        'orbital_period': 27375,
        'miss_distance_km': 88000000,
        'description': 'En ünlü periyodik kuyruklu yıldız, son geçiş 1986'
    },
    'hyakutake': {
        'id': 'C/1996 B2',
        'name': "C/1996 B2 Hyakutake",
        'diameter_m': 4200,
        'velocity_ms': 40000,
        'velocity_kmh': 144000,
        'is_hazardous': False,
        'absolute_magnitude': 5.5,
        'orbital_period': 72000,
        'miss_distance_km': 15000000,
        'description': '1996 da Dünya ya çok yaklaşan parlak kuyruklu yıldız'
    },
    'hale-bopp': {
        'id': 'C/1995 O1',
        'name': "C/1995 O1 Hale-Bopp",
        'diameter_m': 60000,
        'velocity_ms': 44000,
        'velocity_kmh': 158400,
        'is_hazardous': False,
        'absolute_magnitude': -1.0,
        'orbital_period': 93600,
        'miss_distance_km': 197000000,
        'description': '1997 de gözlenen en parlak kuyruklulardan biri, dev çekirdek'
    },
    'oumuamua': {
        'id': '1I/2017 U1',
        'name': "1I/'Oumuamua",
        'diameter_m': 230,
        'velocity_ms': 87300,
        'velocity_kmh': 314280,
        'is_hazardous': False,
        'absolute_magnitude': 22.0,
        'orbital_period': -1,
        'miss_distance_km': 24000000,
        'description': 'İlk tespit edilen yıldızlararası cisim (2017), gizemli puro şekli'
    },
    'borisov': {
        'id': '2I/Borisov',
        'name': "2I/Borisov",
        'diameter_m': 1000,
        'velocity_ms': 32200,
        'velocity_kmh': 115920,
        'is_hazardous': False,
        'absolute_magnitude': 17.8,
        'orbital_period': -1,
        'miss_distance_km': 300000000,
        'description': 'İlk tespit edilen yıldızlararası kuyruklu yıldız (2019)'
    },
    'shoemaker-levy': {
        'id': 'D/1993 F2',
        'name': "D/1993 F2 Shoemaker-Levy 9",
        'diameter_m': 5000,
        'velocity_ms': 60000,
        'velocity_kmh': 216000,
        'is_hazardous': False,
        'absolute_magnitude': 14.0,
        'orbital_period': 0,
        'miss_distance_km': 0,
        'description': '1994 te Jüpiter e çarpan parçalanmış kuyruklu yıldız, tarihi olay'
    },
    'encke': {
        'id': '2P/Encke',
        'name': "2P/Encke",
        'diameter_m': 4800,
        'velocity_ms': 69800,
        'velocity_kmh': 251280,
        'is_hazardous': False,
        'absolute_magnitude': 9.8,
        'orbital_period': 1204,
        'miss_distance_km': 51000000,
        'description': 'En kısa yörünge periyotlu kuyruklu yıldızlardan, Taurid meteor yağmuru'
    },
    'swift-tuttle': {
        'id': '109P/Swift-Tuttle',
        'name': "109P/Swift-Tuttle",
        'diameter_m': 26000,
        'velocity_ms': 60000,
        'velocity_kmh': 216000,
        'is_hazardous': True,
        'absolute_magnitude': 5.4,
        'orbital_period': 49272,
        'miss_distance_km': 130000000,
        'description': 'Perseid meteor yağmurunun kaynağı, büyük ve hızlı, gelecek tehdit'
    }
}

# ============================================================================
# HISTORIC IMPACTORS
# ============================================================================

# Chicxulub - Dinozorları Yok Eden Asteroid (66 milyon yıl önce)
CHICXULUB_IMPACTOR = {
    'id': 'Chicxulub',
    'name': '🦖 Chicxulub Impactor',
    'diameter_m': 10000,
    'velocity_ms': 20000,
    'velocity_kmh': 72000,
    'is_hazardous': True,
    'absolute_magnitude': 15.0,
    'orbital_period': 0,
    'miss_distance_km': 0,
    'description': 'Dinozorları ve Dünya türlerinin %75\'ini yok eden asteroid (66 milyon yıl önce, Meksika Yucatán Yarımadası)'
}

