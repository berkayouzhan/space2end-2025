"""
Asteroid Impact Visualizer - Flask Backend
NASA Space Apps Challenge 2025
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import requests
import random
import math
import os
from datetime import datetime, timedelta
import numpy as np

from data import SOLAR_SYSTEM_ASTEROIDS, COMETS, CHICXULUB_IMPACTOR, MAJOR_CITIES_POPULATION

app = Flask(__name__)
CORS(app)

app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

NASA_API_KEY = os.environ.get('NASA_API_KEY', 'DEMO_KEY')
NASA_NEO_API_URL = 'https://api.nasa.gov/neo/rest/v1'
GEONAMES_USERNAME = os.environ.get('GEONAMES_USERNAME', 'demo')

@app.route('/api/get_asteroid_data', methods=['GET'])
def get_asteroid_data():
    """Fetch asteroid data from NASA API or database."""
    try:
        source = request.args.get('source')
        data_source = request.args.get('data_source', 'database')
        
        if source == 'solar':
            asteroid_key = request.args.get('asteroid', 'apophis')
            if asteroid_key in SOLAR_SYSTEM_ASTEROIDS:
                asteroid_data = SOLAR_SYSTEM_ASTEROIDS[asteroid_key]
                
                # If API mode, try to get live data for this asteroid
                if data_source == 'api':
                    live_data = try_fetch_live_data_for_asteroid(asteroid_data)
                    if live_data:
                        return jsonify({'success': True, 'asteroid': live_data, 'source': 'NASA API (Live)'})
                
                # Return database data
                return jsonify({'success': True, 'asteroid': asteroid_data, 'source': 'Database'})
        
        elif source == 'comets':
            object_key = request.args.get('object', 'halley')
            if object_key in COMETS:
                return jsonify({'success': True, 'asteroid': COMETS[object_key], 'source': 'Database'})
        
        elif source == 'chicxulub':
            return jsonify({'success': True, 'asteroid': CHICXULUB_IMPACTOR, 'source': 'Database'})
        
        return jsonify({'success': True, 'asteroid': get_sample_asteroid_data()})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'asteroid': get_sample_asteroid_data()}), 200

def try_fetch_live_data_for_asteroid(db_asteroid):
    """Try to fetch live data from NASA API for a known asteroid."""
    try:
        # Try to find this asteroid in NASA API by name or ID
        asteroid_id = db_asteroid.get('id', '')
        asteroid_name = db_asteroid.get('name', '')
        
        # For well-known asteroids, try direct lookup
        if asteroid_id:
            try:
                url = f"{NASA_NEO_API_URL}/neo/{asteroid_id}?api_key={NASA_API_KEY}"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    parsed = parse_asteroid_data(data)
                    print(f"[API] Found live data for {asteroid_name}")
                    return parsed
            except:
                pass
        
        # If direct lookup fails, search in recent feed
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        url = f"{NASA_NEO_API_URL}/feed?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&api_key={NASA_API_KEY}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        # Search for matching asteroid in feed
        for date_key in data.get('near_earth_objects', {}):
            for asteroid in data['near_earth_objects'][date_key]:
                if asteroid.get('id') == asteroid_id or asteroid.get('name', '').lower() in asteroid_name.lower():
                    parsed = parse_asteroid_data(asteroid)
                    print(f"[API] Found {asteroid_name} in recent feed")
                    return parsed
        
        print(f"[API] No live data found for {asteroid_name}, using database")
        return None
        
    except Exception as e:
        print(f"[API] Error fetching live data: {e}")
        return None


def fetch_from_nasa_api():
    """Fetch real-time data from NASA NeoWs API."""
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        url = f"{NASA_NEO_API_URL}/feed?start_date={start_date.strftime('%Y-%m-%d')}&end_date={end_date.strftime('%Y-%m-%d')}&api_key={NASA_API_KEY}"
        
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        all_asteroids = []
        for date_key in data.get('near_earth_objects', {}):
            all_asteroids.extend(data['near_earth_objects'][date_key])
        
        if all_asteroids:
            asteroid = random.choice(all_asteroids)
            return jsonify({'success': True, 'asteroid': parse_asteroid_data(asteroid), 'source': 'NASA API'})
        
        return jsonify({'success': False, 'error': 'No asteroids found', 'asteroid': get_sample_asteroid_data()})
    
    except requests.exceptions.RequestException as e:
        print(f"NASA API Error: {e}")
        return jsonify({'success': False, 'error': f'API Error: {str(e)}', 'asteroid': get_sample_asteroid_data()}), 200


def parse_asteroid_data(asteroid_data):
    """Parse NASA API response."""
    try:
        diameter_min = asteroid_data['estimated_diameter']['meters']['estimated_diameter_min']
        diameter_max = asteroid_data['estimated_diameter']['meters']['estimated_diameter_max']
        diameter_avg = (diameter_min + diameter_max) / 2
        
        close_approach = asteroid_data.get('close_approach_data', [{}])[0]
        velocity_kmh = float(close_approach.get('relative_velocity', {}).get('kilometers_per_hour', 50000))
        velocity_ms = velocity_kmh * 1000 / 3600
        
        orbital_data = asteroid_data.get('orbital_data', {})
        
        return {
            'id': asteroid_data.get('id', 'unknown'),
            'name': asteroid_data.get('name', 'Unknown Asteroid'),
            'diameter_m': diameter_avg,
            'velocity_ms': velocity_ms,
            'velocity_kmh': velocity_kmh,
            'is_hazardous': asteroid_data.get('is_potentially_hazardous_asteroid', False),
            'absolute_magnitude': asteroid_data.get('absolute_magnitude_h', 20),
            'orbital_period': orbital_data.get('orbital_period', 365),
            'miss_distance_km': float(close_approach.get('miss_distance', {}).get('kilometers', 1000000))
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return get_sample_asteroid_data()

def get_sample_asteroid_data():
    """Fallback sample data."""
    return {
        'id': 'sample_001',
        'name': '(Sample) 2023 DW',
        'diameter_m': 150,
        'velocity_ms': 18000,
        'velocity_kmh': 64800,
        'is_hazardous': True,
        'absolute_magnitude': 22.5,
        'orbital_period': 271,
        'miss_distance_km': 500000
    }


def calculate_atmospheric_entry(diameter_m, velocity_ms, density_kg_m3, angle_deg):
    """Calculate atmospheric entry effects (ablation, airburst)."""
    angle_rad = math.radians(angle_deg)
    radius_m = diameter_m / 2
    initial_mass = (4/3) * math.pi * (radius_m ** 3) * density_kg_m3
    
    if diameter_m < 25:
        size_factor = 0.0
        ablation_type = "Complete Atmospheric Burn"
    elif diameter_m < 50:
        size_factor = 0.2
        ablation_type = "Airburst (Explosion in Atmosphere)"
    elif diameter_m < 140:
        size_factor = 0.6
        ablation_type = "Partial Fragmentation"
    else:
        size_factor = 0.85
        ablation_type = "Surface Impact with Minor Ablation"
    
    velocity_factor = min(1.0, velocity_ms / 25000)
    angle_factor = math.sin(angle_rad)
    
    mass_retention = size_factor * (1 - 0.1 * velocity_factor * angle_factor)
    mass_retention = max(0.0, min(1.0, mass_retention))
    
    final_mass = initial_mass * mass_retention
    mass_lost = initial_mass - final_mass
    
    airburst_altitude_km = 0
    if diameter_m < 50:
        airburst_altitude_km = 50 - (diameter_m * 0.6)
    
    velocity_retention = 0.5 + (0.5 * mass_retention)
    final_velocity_ms = velocity_ms * velocity_retention
    
    energy_lost_joules = 0.5 * mass_lost * (velocity_ms ** 2)
    
    return {
        'initial_diameter_m': diameter_m,
        'final_diameter_m': diameter_m * (mass_retention ** (1/3)),
        'initial_mass_kg': initial_mass,
        'final_mass_kg': final_mass,
        'mass_lost_kg': mass_lost,
        'mass_retention_percent': mass_retention * 100,
        'initial_velocity_ms': velocity_ms,
        'final_velocity_ms': final_velocity_ms,
        'velocity_lost_ms': velocity_ms - final_velocity_ms,
        'energy_lost_atmosphere_joules': energy_lost_joules,
        'airburst_altitude_km': airburst_altitude_km,
        'ablation_type': ablation_type,
        'reaches_ground': mass_retention > 0.01,
        'warning': 'Most mass vaporized in atmosphere!' if mass_retention < 0.3 else 
                   'Partial fragmentation expected' if mass_retention < 0.7 else 
                   'Substantial ground impact expected'
    }


class AsteroidMaterial:
    """Asteroid material properties."""
    def __init__(self, name, density, tensile_strength, ablation_heat, 
                 emissivity, drag_coefficient=0.75):
        self.name = name
        self.density = density
        self.tensile_strength = tensile_strength
        self.ablation_heat = ablation_heat
        self.emissivity = emissivity
        self.drag_coefficient = drag_coefficient
        
    @staticmethod
    def get_chondrite():
        return AsteroidMaterial("Chondrite (Stony)", 3000, 3e6, 8e6, 0.9, 0.75)
    
    @staticmethod
    def get_iron():
        return AsteroidMaterial("Iron", 7500, 300e6, 10e6, 0.7, 0.75)
    
    @staticmethod
    def get_cometary():
        return AsteroidMaterial("Cometary", 1000, 2e3, 2e6, 0.95, 0.75)
    
    @staticmethod
    def get_material_by_name(name):
        materials = {
            'chondrite': AsteroidMaterial.get_chondrite(),
            'stony': AsteroidMaterial.get_chondrite(),
            'iron': AsteroidMaterial.get_iron(),
            'cometary': AsteroidMaterial.get_cometary()
        }
        return materials.get(name.lower(), AsteroidMaterial.get_chondrite())


class AtmosphereModel:
    """Atmospheric density and temperature model."""
    @staticmethod
    def density(altitude_m):
        rho_0 = 1.225
        
        if altitude_m < 11000:
            H = 8500
        elif altitude_m < 25000:
            H = 6000
        elif altitude_m < 50000:
            H = 7500
        else:
            H = 9000
        
        rho_a = rho_0 * math.exp(-altitude_m / H)
        return max(rho_a, 1e-10)
    
    @staticmethod
    def speed_of_sound(altitude_m):
        if altitude_m < 11000:
            T = 288.15 - 0.0065 * altitude_m
        elif altitude_m < 25000:
            T = 216.65
        else:
            T = 216.65 + 0.003 * (altitude_m - 25000)
        
        c = math.sqrt(1.4 * 287 * T)
        return c


class FragmentationModel:
    """Pancake and discrete fragmentation models."""
    @staticmethod
    def check_fragmentation(velocity_ms, altitude_m, material):
        rho_a = AtmosphereModel.density(altitude_m)
        dynamic_pressure = 0.5 * rho_a * (velocity_ms ** 2)
        should_fragment = dynamic_pressure > material.tensile_strength
        return should_fragment, dynamic_pressure
    
    @staticmethod
    def pancake_model(radius_m, velocity_ms, altitude_m, dt):
        rho_a = AtmosphereModel.density(altitude_m)
        expansion_rate = velocity_ms * math.sqrt(rho_a / 3000)
        new_radius = radius_m + expansion_rate * dt
        return new_radius
    
    @staticmethod
    def discrete_fragmentation(mass_kg, num_fragments=10):
        fragment_mass = mass_kg / num_fragments
        return [fragment_mass] * num_fragments


def simulate_atmospheric_entry_advanced(
    diameter_m, velocity_ms, entry_angle_deg, material_type='chondrite',
    initial_altitude_m=100000, fragmentation_model='pancake', dt=0.01, max_time=300
):
    """Advanced atmospheric entry simulation with numerical integration."""
    material = AsteroidMaterial.get_material_by_name(material_type)
    
    t = 0.0
    altitude = initial_altitude_m
    velocity = velocity_ms
    angle_rad = math.radians(entry_angle_deg)
    radius = diameter_m / 2
    mass = (4/3) * math.pi * (radius ** 3) * material.density
    
    vx = velocity * math.cos(angle_rad)
    vy = -velocity * math.sin(angle_rad)
    
    x = 0.0
    y = altitude
    
    fragmented = False
    fragments = []
    
    history = {
        'time': [], 'altitude': [], 'velocity': [], 'mass': [], 'radius': [],
        'luminosity': [], 'dynamic_pressure': [], 'deposition_energy': []
    }
    
    Gamma = material.drag_coefficient
    Lambda = 0.5
    Zeta = material.ablation_heat
    Tau = 0.1
    
    total_energy_deposited = 0.0
    peak_luminosity = 0.0
    airburst_altitude = None
    max_dynamic_pressure = 0.0
    
    steps = 0
    max_steps = int(max_time / dt)
    
    while steps < max_steps and y > 0:
        # Mevcut durum
        velocity = math.sqrt(vx**2 + vy**2)
        rho_a = AtmosphereModel.density(y)
        A = math.pi * (radius ** 2)  # Kesit alanı
        
        if mass <= 0 or velocity < 100:  # Kütle bitti veya çok yavaşladı
            break
        
        # Parçalanma kontrolü
        if not fragmented:
            should_fragment, dynamic_pressure = FragmentationModel.check_fragmentation(
                velocity, y, material
            )
            
            if should_fragment:
                fragmented = True
                if fragmentation_model == 'pancake':
                    # Pancake: Yarıçap artar
                    radius = FragmentationModel.pancake_model(radius, velocity, y, dt)
                    A = math.pi * (radius ** 2)
                elif fragmentation_model == 'discrete':
                    # Discrete: Parçalara ayrıl (basitleştirilmiş - ana cismi takip et)
                    fragments = FragmentationModel.discrete_fragmentation(mass, 10)
                    # Sadece en büyük parçayı takip et (basitleştirme)
                    mass = max(fragments)
                    radius = ((3 * mass) / (4 * math.pi * material.density)) ** (1/3)
                    A = math.pi * (radius ** 2)
        
        # Denklem 1: Aerodinamik yavaşlama (dv/dt)
        # dv/dt = -(Gamma * A * rho_a * v²) / m
        drag_force = Gamma * A * rho_a * (velocity ** 2)
        dv_dt = -drag_force / mass
        
        # Denklem 2: Termal ablasyon (dm/dt)
        # dm/dt = -(Lambda * A * rho_a * v³) / (2 * Zeta)
        dm_dt = -(Lambda * A * rho_a * (velocity ** 3)) / (2 * Zeta)
        
        # Denklem 3: Işıma (I)
        # I = -0.5 * Tau * (dm/dt) * v²
        luminosity = -0.5 * Tau * dm_dt * (velocity ** 2)
        
        # Maksimum parlaklık (airburst noktası yaklaşımı)
        if luminosity > peak_luminosity:
            peak_luminosity = luminosity
            airburst_altitude = y / 1000  # km
        
        # Enerji biriktirme
        energy_deposited_step = 0.5 * abs(dm_dt) * dt * (velocity ** 2)
        total_energy_deposited += energy_deposited_step
        
        # Dinamik basınç
        dynamic_pressure = 0.5 * rho_a * (velocity ** 2)
        max_dynamic_pressure = max(max_dynamic_pressure, dynamic_pressure)
        
        # Runge-Kutta 4. Derece entegrasyonu (basitleştirilmiş Euler için şimdilik)
        # Hız güncelleme
        velocity_new = velocity + dv_dt * dt
        
        # Kütle güncelleme
        mass_new = mass + dm_dt * dt
        mass_new = max(mass_new, 0)  # Negatif olamaz
        
        # Yarıçap güncelleme (kütleden)
        if mass_new > 0:
            radius = ((3 * mass_new) / (4 * math.pi * material.density)) ** (1/3)
        
        # Pozisyon güncelleme
        ax = -drag_force * vx / (mass * velocity) if velocity > 0 else 0
        ay = -drag_force * vy / (mass * velocity) - 9.81 if velocity > 0 else -9.81  # Yerçekimi
        
        vx_new = vx + ax * dt
        vy_new = vy + ay * dt
        
        x += vx * dt
        y += vy * dt
        
        # Güncelle
        vx = vx_new
        vy = vy_new
        mass = mass_new
        velocity = velocity_new
        
        # Kaydet
        history['time'].append(t)
        history['altitude'].append(y / 1000)  # km
        history['velocity'].append(velocity / 1000)  # km/s
        history['mass'].append(mass / 1000)  # ton
        history['radius'].append(radius)  # m
        history['luminosity'].append(luminosity)  # Watt
        history['dynamic_pressure'].append(dynamic_pressure / 1e6)  # MPa
        history['deposition_energy'].append(total_energy_deposited)
        
        t += dt
        steps += 1
    
    # TNT eşdeğeri (kiloton)
    tnt_equivalent_kt = total_energy_deposited / (4.184 * 10**12)
    
    return {
        'success': True,
        'initial_conditions': {
            'diameter_m': diameter_m,
            'velocity_ms': velocity_ms,
            'entry_angle_deg': entry_angle_deg,
            'material': material.name,
            'initial_altitude_km': initial_altitude_m / 1000,
            'initial_mass_kg': (4/3) * math.pi * ((diameter_m/2) ** 3) * material.density
        },
        'final_state': {
            'altitude_km': y / 1000,
            'velocity_ms': velocity,
            'mass_kg': mass,
            'radius_m': radius
        },
        'key_results': {
            'airburst_altitude_km': airburst_altitude if airburst_altitude else y / 1000,
            'peak_luminosity_watts': peak_luminosity,
            'total_energy_deposited_joules': total_energy_deposited,
            'tnt_equivalent_kilotons': tnt_equivalent_kt,
            'max_dynamic_pressure_mpa': max_dynamic_pressure / 1e6,
            'fragmented': fragmented,
            'fragmentation_model': fragmentation_model if fragmented else 'none'
        },
        'time_series': history,
        'material_properties': {
            'density': material.density,
            'tensile_strength_mpa': material.tensile_strength / 1e6,
            'ablation_heat_mj_kg': material.ablation_heat / 1e6,
            'emissivity': material.emissivity
        }
    }


def calculate_kinetic_energy(diameter_m, density_kg_m3, velocity_ms):
    """Calculate kinetic energy of asteroid."""
    radius_m = diameter_m / 2
    volume_m3 = (4/3) * math.pi * (radius_m ** 3)
    mass_kg = volume_m3 * density_kg_m3
    
    kinetic_energy_joules = 0.5 * mass_kg * (velocity_ms ** 2)
    
    # TNT eşdeğeri (1 kiloton TNT = 4.184 × 10^12 Joules)
    tnt_kilotons = kinetic_energy_joules / (4.184 * 10**12)
    tnt_megatons = tnt_kilotons / 1000
    
    return {
        'mass_kg': mass_kg,
        'kinetic_energy_joules': kinetic_energy_joules,
        'tnt_kilotons': tnt_kilotons,
        'tnt_megatons': tnt_megatons
    }


def determine_airburst_altitude(diameter_m, density_kg_m3, velocity_ms, angle_deg):
    """
    Adım 1.2: Havada infilak irtifasını belirle
    Küçük ve orta boyutlu asteroidler için atmosferde en yüksek enerji salımı irtifası
    """
    # Giriş açısı faktörü
    angle_rad = math.radians(angle_deg)
    sin_angle = math.sin(angle_rad)
    
    # Ablasyon parametresi (yoğunluğa bağlı)
    # Taşlı: yüksek yoğunluk, daha düşük irtifada patlar
    # Buzlu: düşük yoğunluk, daha yüksek irtifada patlar
    if density_kg_m3 > 2500:  # Taşlı
        h0 = 8.0  # km
        alpha = 0.6
    elif density_kg_m3 > 1500:  # Orta yoğunluk
        h0 = 15.0
        alpha = 0.7
    else:  # Buzlu
        h0 = 25.0
        alpha = 0.8
    
    # Boyut faktörü: küçük asteroidler daha yüksekte patlar
    size_factor = max(0.2, min(1.0, diameter_m / 100))
    
    # Hız faktörü: yüksek hız = daha fazla sürtünme = daha yüksek irtifa
    velocity_factor = velocity_ms / 20000  # Normalize
    
    # İrtifa hesabı (km)
    airburst_altitude_km = h0 * (1 - alpha * size_factor) * (1 + 0.3 * velocity_factor) * sin_angle
    airburst_altitude_km = max(0, min(50, airburst_altitude_km))  # 0-50 km arası
    
    return airburst_altitude_km


def determine_impact_type(diameter_m, density_kg_m3, velocity_ms, angle_deg, is_ocean):
    """
    Adım 2: Çarpma tipini belirle
    - Havada İnfilak (Airburst)
    - Yer Çarpması (Surface Impact)
    - Su Çarpması (Ocean Impact)
    """
    # Atmosferik giriş analizi
    atm_data = calculate_atmospheric_entry(diameter_m, velocity_ms, density_kg_m3, angle_deg)
    
    # Kritik çap eşiği (yoğunluğa göre)
    # Taşlı asteroidler için ~50-60m eşiği (yoğunluk ~3100 kg/m³)
    if density_kg_m3 > 2500:  # Taşlı
        critical_diameter = 55
    elif density_kg_m3 > 1500:  # Orta
        critical_diameter = 40
    else:  # Buzlu
        critical_diameter = 30
    
    # Havada infilak irtifası
    airburst_alt = determine_airburst_altitude(diameter_m, density_kg_m3, velocity_ms, angle_deg)
    
    # Çarpma tipi belirleme
    if diameter_m < critical_diameter or not atm_data['reaches_ground']:
        impact_type = "Airburst"
        applicable_hazards = ['overpressure', 'wind_blast', 'thermal_radiation']
    elif is_ocean:
        impact_type = "Ocean Impact"
        applicable_hazards = ['overpressure', 'wind_blast', 'thermal_radiation', 'tsunami']
    else:
        impact_type = "Surface Impact"
        applicable_hazards = ['overpressure', 'wind_blast', 'thermal_radiation', 
                             'seismic', 'ejecta', 'cratering']
    
    return {
        'impact_type': impact_type,
        'applicable_hazards': applicable_hazards,
        'airburst_altitude_km': airburst_alt,
        'atmospheric_data': atm_data
    }


def calculate_overpressure(distance_m, energy_joules, altitude_km=0):
    """
    Adım 3: Aşırı Basınç Tehlikesi
    Zirve aşırı basıncını Paskal (Pa) olarak hesapla
    
    Sedov-Taylor blast wave theory kullanarak
    ΔP = P0 * (R0/r)^α
    """
    if distance_m <= 0:
        return 1e9  # Sonsuz basınç
    
    # Enerjiyi TNT eşdeğerine çevir (kg)
    tnt_kg = energy_joules / (4.184 * 10**6)
    
    # Karakteristik yarıçap (m)
    R0 = (tnt_kg ** (1/3)) * 10  # 10 m/kg^(1/3)
    
    # Havada infilak düzeltmesi
    if altitude_km > 0:
        # Yüksek irtifa patlamaları daha geniş alana yayılır
        altitude_factor = 1 + (altitude_km / 10)
        R0 *= altitude_factor
    
    # Ölçeklendirme
    scaled_distance = distance_m / R0
    
    # Aşırı basınç hesabı (ampirik formül)
    if scaled_distance < 0.1:
        overpressure_pa = 1e7  # 10 MPa (çok yakın)
    elif scaled_distance < 1:
        overpressure_pa = 1e6 / (scaled_distance ** 1.5)
    else:
        overpressure_pa = 2e5 / (scaled_distance ** 2)
    
    return max(0, overpressure_pa)


def calculate_wind_blast(distance_m, energy_joules, altitude_km=0):
    """
    Adım 3: Rüzgar Patlaması Tehlikesi
    Zirve rüzgar hızını m/s olarak hesapla
    """
    if distance_m <= 0:
        return 1000  # Çok yüksek
    
    # Aşırı basınçtan rüzgar hızı tahmini
    overpressure_pa = calculate_overpressure(distance_m, energy_joules, altitude_km)
    
    # Rankine-Hugoniot ilişkisi (basitleştirilmiş)
    # v ≈ sqrt(2 * ΔP / ρ_air)
    air_density = 1.225  # kg/m³
    wind_speed_ms = math.sqrt(2 * overpressure_pa / air_density)
    
    return min(1000, wind_speed_ms)  # Maksimum 1000 m/s


def calculate_thermal_radiation(distance_m, energy_joules, altitude_km=0):
    """
    Adım 3: Termal Radyasyon Tehlikesi
    Termal akıyı J/m² olarak hesapla
    """
    if distance_m <= 0:
        return 1e10  # Sonsuz
    
    # Patlamanın ışınım enerjisi (toplam enerjinin ~30-40%)
    radiation_energy = energy_joules * 0.35
    
    # Küresel yayılım (4πr²)
    surface_area = 4 * math.pi * (distance_m ** 2)
    
    # Havada infilak düzeltmesi
    if altitude_km > 0:
        # Yüksek irtifadan daha geniş alana yayılır
        altitude_factor = 1 + (altitude_km / 20)
        surface_area *= altitude_factor
    
    # Atmosferik soğurma (mesafe ile azalır)
    attenuation = math.exp(-distance_m / 50000)  # 50 km karakteristik uzunluk
    
    thermal_flux = (radiation_energy / surface_area) * attenuation
    
    return max(0, thermal_flux)


def calculate_seismic_magnitude(energy_joules):
    """
    Adım 3: Sismik Sarsıntı Tehlikesi
    Richter ölçeğinde büyüklük
    """
    if energy_joules <= 0:
        return 0
    
    # Richter magnitude: M = (log10(E) - 4.8) / 1.5
    magnitude = (math.log10(energy_joules) - 4.8) / 1.5
    
    return max(0, magnitude)


def calculate_ejecta_thickness(distance_m, crater_diameter_m):
    """
    Adım 3: Ejekta Püskürtüsü Tehlikesi
    Ejekta örtüsü kalınlığını metre (m) olarak hesapla
    
    McGetchin et al. (1973) modeli:
    t_e = t0 * (R_crater / r)^3
    """
    if distance_m <= 0 or crater_diameter_m <= 0:
        return 0
    
    crater_radius_m = crater_diameter_m / 2
    
    # Krater kenarındaki başlangıç kalınlığı (yaklaşık)
    t0 = crater_radius_m * 0.1  # Krater derinliğinin ~10%'si
    
    # Mesafe faktörü
    if distance_m < crater_radius_m:
        # Krater içi
        thickness = t0 * 2
    else:
        # Krater dışı - kuvvet kanunu azalması
        scaled_distance = distance_m / crater_radius_m
        thickness = t0 * (1 / scaled_distance ** 3)
    
    return max(0, thickness)


def calculate_tsunami_wave_height(distance_km, impact_energy_joules, water_depth_m, crater_diameter_km):
    """
    Adım 3: Tsunami Tehlikesi (Su Çarpması için)
    Kıyı şeridine ulaştığında beklenen dalga yüksekliğini (run-up) hesapla
    
    Ward & Asphaug (2000) modeli (basitleştirilmiş)
    """
    if distance_km <= 0:
        return 0
    
    # TNT eşdeğeri (Megaton)
    tnt_megatons = impact_energy_joules / (4.184 * 10**15)
    
    # Başlangıç tsunami yüksekliği (çarpma noktasında)
    # H0 ≈ (E^0.25) * crater_factor
    crater_factor = min(1.0, crater_diameter_km / 2.0)
    initial_height_m = (tnt_megatons ** 0.25) * 3 * crater_factor
    
    # Su derinliği faktörü
    if water_depth_m < 50:
        depth_factor = 0.3  # Sığ su - tsunami zayıf
    elif water_depth_m < 200:
        depth_factor = 0.6
    elif water_depth_m < 1000:
        depth_factor = 0.9
    else:
        depth_factor = 1.0  # Derin okyanus - tam etki
    
    initial_height_m *= depth_factor
    
    # Mesafe ile azalma (geometrik yayılma)
    # H(r) = H0 / sqrt(r)
    if distance_km < 1:
        distance_km = 1  # Minimum mesafe
    
    wave_height_m = initial_height_m / math.sqrt(distance_km)
    
    # Kıyıya ulaştığında run-up (yükseklik artışı)
    # Shallow water effect: ~2-4x artış
    runup_factor = 3.0
    final_height_m = wave_height_m * runup_factor
    
    return max(0, final_height_m)


# ============================================================================
# VULNERABILITY MODELS: RUMPF METHODOLOGY
# ============================================================================

def enhanced_fujita_scale_casualties(wind_speed_ms, population, sheltered_fraction=0.87):
    """
    Adım 5: Rüzgar için Geliştirilmiş Fujita (EF) Ölçeği
    
    EF Ölçeği ve yapısal hasar seviyesi:
    - EF0: 29-38 m/s - Hafif hasar
    - EF1: 38-49 m/s - Orta hasar
    - EF2: 50-60 m/s - Önemli hasar
    - EF3: 61-74 m/s - Ciddi hasar
    - EF4: 75-89 m/s - Yıkıcı hasar
    - EF5: >90 m/s - İnanılmaz hasar
    """
    unsheltered_pop = population * (1 - sheltered_fraction)
    sheltered_pop = population * sheltered_fraction
    
    casualties = 0
    
    # Korunmasız nüfus için kayıp oranları
    if wind_speed_ms < 29:
        unsheltered_rate = 0.001  # %0.1
        sheltered_rate = 0.0
    elif wind_speed_ms < 38:  # EF0
        unsheltered_rate = 0.01  # %1
        sheltered_rate = 0.001  # %0.1
    elif wind_speed_ms < 49:  # EF1
        unsheltered_rate = 0.05  # %5
        sheltered_rate = 0.01  # %1
    elif wind_speed_ms < 60:  # EF2
        unsheltered_rate = 0.15  # %15
        sheltered_rate = 0.05  # %5
    elif wind_speed_ms < 74:  # EF3
        unsheltered_rate = 0.35  # %35
        sheltered_rate = 0.15  # %15
    elif wind_speed_ms < 89:  # EF4
        unsheltered_rate = 0.60  # %60
        sheltered_rate = 0.35  # %35
    else:  # EF5
        unsheltered_rate = 0.85  # %85
        sheltered_rate = 0.60  # %60
    
    casualties = (unsheltered_pop * unsheltered_rate) + (sheltered_pop * sheltered_rate)
    
    return casualties


def ejecta_load_casualties(ejecta_thickness_m, population, sheltered_fraction=0.87):
    """
    Adım 5: Ejekta Yükü için Kayıp Hesaplaması
    
    p_e = t_e * ρ_e * g_0
    ρ_e = 1600 kg/m³ (ejekta yoğunluğu)
    g_0 = 9.81 m/s² (yerçekimi)
    
    Yapısal sınırlar:
    - Ahşap ev: ~2 kPa
    - Betonarme: ~10 kPa
    """
    if ejecta_thickness_m <= 0:
        return 0
    
    ejecta_density = 1600  # kg/m³
    g = 9.81  # m/s²
    
    # Ejekta yükü (Pa)
    ejecta_load_pa = ejecta_thickness_m * ejecta_density * g
    
    sheltered_pop = population * sheltered_fraction
    
    # Yapısal çökmme eşikleri
    wood_collapse_threshold = 2000  # Pa (2 kPa)
    concrete_collapse_threshold = 10000  # Pa (10 kPa)
    
    casualties = 0
    
    if ejecta_load_pa > concrete_collapse_threshold:
        # Tüm binalar çöker - %10 ölüm oranı (korunaklı nüfus için)
        casualties = sheltered_pop * 0.10
    elif ejecta_load_pa > wood_collapse_threshold:
        # Ahşap binalar çöker - %5 ölüm oranı
        casualties = sheltered_pop * 0.05
    
    return casualties


def thermal_burn_casualties(thermal_flux_j_m2, population, sheltered_fraction=0.87):
    """
    Adım 5: Termal Radyasyon için Yanık Kayıpları
    
    Üçüncü derece yanık eşikleri:
    - 1. derece: ~200 kJ/m²
    - 2. derece: ~400 kJ/m²
    - 3. derece: ~800 kJ/m²
    """
    unsheltered_pop = population * (1 - sheltered_fraction)
    
    # kJ/m² ye çevir
    thermal_flux_kj_m2 = thermal_flux_j_m2 / 1000
    
    casualties = 0
    
    # Sadece korunmasız nüfus etkilenir (binalar termal radyasyondan korur)
    if thermal_flux_kj_m2 < 200:
        casualty_rate = 0.0
    elif thermal_flux_kj_m2 < 400:  # 1. derece
        casualty_rate = 0.01  # %1
    elif thermal_flux_kj_m2 < 800:  # 2. derece
        casualty_rate = 0.05  # %5
    else:  # 3. derece - ölümcül
        casualty_rate = 0.30  # %30
    
    casualties = unsheltered_pop * casualty_rate
    
    return casualties


def overpressure_casualties(overpressure_pa, population, sheltered_fraction=0.87):
    """
    Adım 5: Aşırı Basınç için Kayıp Hesaplaması
    
    Yapısal hasar eşikleri:
    - 3 kPa: Camlar kırılır
    - 20 kPa: Ahşap binalar hasar görür
    - 35 kPa: Betonarme hasarı
    - 70 kPa: Ağır yapısal hasar
    - 140 kPa: Beton binaların yıkılması
    """
    unsheltered_pop = population * (1 - sheltered_fraction)
    sheltered_pop = population * sheltered_fraction
    
    # kPa'ya çevir
    overpressure_kpa = overpressure_pa / 1000
    
    casualties = 0
    
    if overpressure_kpa < 3:
        unsheltered_rate = 0.0
        sheltered_rate = 0.0
    elif overpressure_kpa < 20:
        unsheltered_rate = 0.01
        sheltered_rate = 0.001
    elif overpressure_kpa < 35:
        unsheltered_rate = 0.05
        sheltered_rate = 0.01
    elif overpressure_kpa < 70:
        unsheltered_rate = 0.20
        sheltered_rate = 0.05
    elif overpressure_kpa < 140:
        unsheltered_rate = 0.50
        sheltered_rate = 0.20
    else:  # Extreme
        unsheltered_rate = 0.95
        sheltered_rate = 0.70
    
    casualties = (unsheltered_pop * unsheltered_rate) + (sheltered_pop * sheltered_rate)
    
    return casualties


def seismic_casualties(magnitude_richter, population, sheltered_fraction=0.87):
    """
    Adım 5: Sismik Sarsıntı için Kayıp Hesaplaması
    """
    if magnitude_richter < 5.0:
        casualty_rate = 0.0
    elif magnitude_richter < 6.0:
        casualty_rate = 0.001  # %0.1
    elif magnitude_richter < 7.0:
        casualty_rate = 0.01  # %1
    elif magnitude_richter < 8.0:
        casualty_rate = 0.05  # %5
    else:
        casualty_rate = 0.15  # %15
    
    return population * casualty_rate


def crater_casualties(crater_radius_m, distance_m, population):
    """
    Adım 5: Krater içindeki toplam kayıp
    """
    if distance_m < crater_radius_m:
        # Krater içinde %100 kayıp
        return population
    else:
        return 0


# ============================================================================
# GRID-BASED POPULATION EXPOSURE MAPPING
# ============================================================================

def create_population_grid(center_lat, center_lng, max_radius_km, grid_resolution_km=1):
    """
    Adım 4: Nüfus yoğunluğu için grid oluştur
    
    Args:
        center_lat, center_lng: Çarpma noktası koordinatları
        max_radius_km: Maksimum etki yarıçapı
        grid_resolution_km: Grid hücre boyutu (km)
    
    Returns:
        Grid hücreleri listesi: [(lat, lng, distance_km, population_density), ...]
    """
    # Basit grid oluşturma (gerçek projede GeoTIFF/CSV veri kullanılmalı)
    # Şimdilik GeoNames API veya tahmini yoğunluk kullanıyoruz
    
    grid_cells = []
    
    # Enlem/boylam başına km (yaklaşık)
    km_per_degree_lat = 111.0
    km_per_degree_lng = 111.0 * math.cos(math.radians(center_lat))
    
    # Grid boyutları
    num_cells = int(max_radius_km / grid_resolution_km) * 2
    
    for i in range(-num_cells, num_cells + 1):
        for j in range(-num_cells, num_cells + 1):
            # Grid hücresi koordinatları
            cell_lat = center_lat + (i * grid_resolution_km / km_per_degree_lat)
            cell_lng = center_lng + (j * grid_resolution_km / km_per_degree_lng)
            
            # Çarpma noktasına mesafe
            distance_km = math.sqrt(
                ((cell_lat - center_lat) * km_per_degree_lat) ** 2 +
                ((cell_lng - center_lng) * km_per_degree_lng) ** 2
            )
            
            # Maksimum yarıçap içindeyse ekle
            if distance_km <= max_radius_km:
                # Nüfus yoğunluğu tahmini (gerçek projede GeoTIFF/API'den alınmalı)
                # Şimdilik mesafeye göre azalan basit model
                base_density = estimate_population_density_simple(cell_lat, cell_lng)
                
                # Alan (km²)
                cell_area_km2 = grid_resolution_km ** 2
                
                # Hücre nüfusu
                cell_population = base_density * cell_area_km2
                
                grid_cells.append({
                    'lat': cell_lat,
                    'lng': cell_lng,
                    'distance_km': distance_km,
                    'distance_m': distance_km * 1000,
                    'population': cell_population,
                    'density': base_density
                })
    
    return grid_cells


def get_nearest_city_population(lat, lng, max_distance_km=300):
    """
    En yakın büyük şehri bulur ve nüfus yoğunluğunu hesaplar
    
    Args:
        lat, lng: Konum koordinatları
        max_distance_km: Maksimum arama mesafesi (km)
    
    Returns:
        Dict: Şehir bilgisi ve tahmini yoğunluk
    """
    nearest_city = None
    min_distance = float('inf')
    
    for city_name, city_data in MAJOR_CITIES_POPULATION.items():
        # Mesafe hesapla (yaklaşık)
        lat_diff = lat - city_data['lat']
        lng_diff = lng - city_data['lng']
        distance_km = math.sqrt((lat_diff * 111) ** 2 + (lng_diff * 111 * math.cos(math.radians(lat))) ** 2)
        
        if distance_km < min_distance:
            min_distance = distance_km
            nearest_city = {
                'name': city_name,
                'distance_km': distance_km,
                'population': city_data['population'],
                'density': city_data['density'],
                'lat': city_data['lat'],
                'lng': city_data['lng']
            }
    
    if nearest_city and nearest_city['distance_km'] <= max_distance_km:
        # Mesafeye göre yoğunluk azalması
        # Şehir merkezinden uzaklaştıkça yoğunluk azalır
        distance_factor = max(0.1, 1 - (nearest_city['distance_km'] / max_distance_km))
        estimated_density = int(nearest_city['density'] * distance_factor)
        
        nearest_city['estimated_density'] = max(10, estimated_density)  # Minimum 10 kişi/km²
        nearest_city['reason'] = f"{nearest_city['name']} şehrinden {nearest_city['distance_km']:.0f} km uzaklıkta"
        return nearest_city
    
    return None

def estimate_population_density_simple(lat, lng):
    """
    GELİŞTİRİLMİŞ nüfus yoğunluğu tahmini (kişi/km²)
    
    1. Önce en yakın büyük şehri kontrol et
    2. Şehir bulunamazsa enleme göre tahmin yap
    """
    # Önce yakın şehirlere bak
    nearest_city = get_nearest_city_population(lat, lng, max_distance_km=300)
    
    if nearest_city:
        return nearest_city['estimated_density']
    
    # Şehir bulunamadıysa fallback: enleme göre kabaca tahmin
    abs_lat = abs(lat)
    
    if abs_lat < 10:  # Ekvator
        return 50
    elif abs_lat < 30:  # Tropikal
        return 100
    elif abs_lat < 50:  # Ilıman
        return 150
    else:  # Kutup
        return 5


# ============================================================================
# YARDIMCI FONKSİYONLAR: POPÜLASYON VE TSUNAMİ
# ============================================================================

def get_population_density_from_geonames(lat, lng, radius_km=50):
    """
    GeoNames API kullanarak bölgenin gerçek nüfus yoğunluğunu çeker
    """
    try:
        # GeoNames findNearbyPlaceName endpoint - en yakın yerleşim yerlerini bulur
        url = f'http://api.geonames.org/findNearbyPlaceNameJSON?lat={lat}&lng={lng}&radius={radius_km}&maxRows=10&username={GEONAMES_USERNAME}'
        
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'geonames' in data and len(data['geonames']) > 0:
            # En yakın şehirlerin popülasyonunu al
            total_population = 0
            total_area = 0
            cities_count = 0
            
            for place in data['geonames'][:5]:  # İlk 5 yerleşim
                if 'population' in place and place['population'] > 0:
                    pop = place['population']
                    # Kabaca şehir alanı tahmini (pop/1000 km²)
                    estimated_area = max(10, pop / 1000)  # Minimum 10 km²
                    total_population += pop
                    total_area += estimated_area
                    cities_count += 1
            
            if cities_count > 0 and total_area > 0:
                # Ortalama yoğunluk
                density = total_population / total_area
                
                # En yakın şehir bilgisi
                nearest_city = data['geonames'][0]
                city_name = nearest_city.get('name', 'Unknown')
                country = nearest_city.get('countryName', 'Unknown')
                distance = nearest_city.get('distance', 0)
                
                return {
                    'density': round(density),
                    'nearest_city': city_name,
                    'country': country,
                    'distance_km': round(float(distance), 2),
                    'population': total_population,
                    'cities_in_range': cities_count,
                    'source': 'GeoNames API'
                }
        
        # Veri bulunamazsa varsayılan
        return None
        
    except Exception as e:
        print(f"GeoNames API Error: {e}")
        return None


def estimate_population_affected(impact_lat, impact_lng, damage_zones, is_ocean=False, ocean_name='Ocean', tsunami_height_m=0, tsunami_range_km=0):
    """Estimate affected population and casualties."""
    
    # GLOBAL EXTINCTION EVENT CHECK (Chicxulub-level impacts)
    light_damage_km = damage_zones.get('light_damage_km', 0)
    
    # If damage radius > 5000 km, this is a global extinction event
    if light_damage_km > 5000:
        world_population = 8_000_000_000  # Current world population
        return {
            'total_affected': world_population,
            'estimated_casualties': world_population,
            'casualties_by_zone': {
                'total_destruction': int(world_population * 0.4),
                'heavy_damage': int(world_population * 0.3),
                'moderate_damage': int(world_population * 0.2),
                'light_damage': int(world_population * 0.1)
            },
            'crater_casualties': int(world_population * 0.1),
            'thermal_casualties': int(world_population * 0.2),
            'shockwave_casualties': int(world_population * 0.2),
            'wind_casualties': int(world_population * 0.15),
            'earthquake_casualties': int(world_population * 0.15),
            'tsunami_casualties': int(world_population * 0.2) if is_ocean else 0,
            'population_density': 60,
            'location_info': '🌍 GLOBAL EXTINCTION EVENT',
            'data_source': 'Global Impact Model',
            'note': '⚠️ This asteroid would cause a mass extinction event affecting all life on Earth'
        }
    
    if is_ocean:
        # OPTİMİZE EDİLMİŞ POPÜLASYON TAHMİNİ
        # Tsunami menzili ve büyüklüğüne göre etkilenen kıyı nüfusu
        
        # 1. Okyanus türüne göre kıyı yoğunluğu ve yakınlık faktörü
        if 'Mediterranean' in ocean_name:
            # Akdeniz - çok yoğun nüfuslu kıyılar, küçük deniz
            coastal_density = 250  # İtalya, Yunanistan, Türkiye, Mısır
            coastal_coverage = 0.4  # Kıyıların %40'ı yerleşim
            typical_distance_to_coast = 200  # Küçük deniz, kıyılar yakın
        elif 'Pacific' in ocean_name:
            # Pasifik - DEV OKYANUS, ortası boş!
            coastal_density = 150  # Japonya, Çin, ABD kıyıları
            coastal_coverage = 0.15  # Kıyılar UZAK - sadece %15 etkilenir
            typical_distance_to_coast = 2000  # Ortalama 2000 km kıyıya uzaklık
        elif 'Atlantic' in ocean_name:
            # Atlantik - orta boyut okyanus
            coastal_density = 120  # ABD, Avrupa, Afrika kıyıları
            coastal_coverage = 0.25
            typical_distance_to_coast = 1500
        elif 'Indian' in ocean_name:
            # Hint Okyanusu - yoğun kıyılar ama geniş
            coastal_density = 180  # Hindistan, Endonezya, Afrika
            coastal_coverage = 0.3
            typical_distance_to_coast = 1200
        elif 'Southern' in ocean_name or 'Antarctic' in ocean_name:
            # Güney Okyanusu / Antarktika - neredeyse hiç yerleşim yok
            coastal_density = 2  # Araştırma istasyonları
            coastal_coverage = 0.005  # Neredeyse hiç yok
            typical_distance_to_coast = 3000  # Çok uzak
        elif 'Arctic' in ocean_name:
            # Kuzey Kutup Okyanusu - çok az yerleşim
            coastal_density = 5  # Alaska, Grönland, Rusya kıyıları
            coastal_coverage = 0.05
            typical_distance_to_coast = 1000
        elif 'Black' in ocean_name:
            # Karadeniz - küçük deniz, yoğun kıyılar
            coastal_density = 200  # Türkiye, Ukrayna, Rusya, Romanya
            coastal_coverage = 0.45
            typical_distance_to_coast = 250
        elif 'Red' in ocean_name:
            # Kızıldeniz - dar deniz
            coastal_density = 80  # Mısır, Suudi Arabistan
            coastal_coverage = 0.3
            typical_distance_to_coast = 150
        elif 'Persian' in ocean_name or 'Gulf' in ocean_name:
            # Basra Körfezi - küçük körfez, yoğun
            coastal_density = 220  # İran, Irak, Kuveyt, BAE
            coastal_coverage = 0.5
            typical_distance_to_coast = 100
        else:
            # Diğer denizler
            coastal_density = 100
            coastal_coverage = 0.2
            typical_distance_to_coast = 800
        
        # 2. Tsunami ATTENUATION (azalma) modeli
        # Tsunami yüksekliği mesafeyle azalır: H(r) = H₀ / √r
        # Çarpma noktasından kıyıya ortalama mesafe
        max_tsunami_range_km = tsunami_range_km  # Hesaplanan menzil değerini kullan
        
        # Kıyıya ulaştığında tsunami yüksekliği
        # Basitleştirilmiş attenuation: her 1000 km'de %70 azalma
        distance_factor = max(0.1, math.exp(-typical_distance_to_coast / 2000))
        coastal_tsunami_height = tsunami_height_m * distance_factor
        
        # 3. Etkilenen alan hesabı - DÜZELTİLMİŞ VE GERÇEKÇİ
        # Sadece tsunami MENZİLİ içindeki kıyılar etkilenir
        coastal_area = 0  # Varsayılan değer
        if typical_distance_to_coast > max_tsunami_range_km:
            # Tsunami kıyıya ulaşamaz - çok uzak!
            total_affected = 0
            casualties = 0
        else:
            # DÜZELTİLMİŞ HESAPLAMA:
            # effective_range küçük denizlerde çok büyük olmamalı
            # Küçük denizlerde (Mediterranean, Black Sea) kıyıya mesafe zaten küçük
            # bu yüzden etki alanı da sınırlı olmalı
            
            # Etkilenen kıyı uzunluğu için gerçekçi hesaplama
            if 'Mediterranean' in ocean_name or 'Black' in ocean_name or 'Red' in ocean_name or 'Gulf' in ocean_name:
                # Küçük denizler için - çok sınırlı etki alanı
                # Sadece çarpma noktası yakınındaki kıyılar etkilenir
                effective_coastal_range = min(500, max_tsunami_range_km * 0.3)  # Maksimum 500 km kıyı
            else:
                # Büyük okyanuslar için - geniş etki alanı
                effective_range = max_tsunami_range_km - typical_distance_to_coast
                effective_range = max(0, effective_range)
                effective_coastal_range = effective_range * coastal_coverage
            
            # Etkilenen kıyı uzunluğu (km)
            # Basitleştirilmiş: çarpma noktası etrafındaki yay uzunluğu
            coastal_length_km = min(2000, 2 * math.pi * effective_coastal_range * 0.5)  # Maksimum 2000 km
            
            # Kıyı alanı: uzunluk * iç penetrasyon (tsunami kıyıdan ne kadar içeri girer)
            # Tsunami yüksekliği > 10m ise 2-5 km içeri girer
            inland_penetration_km = min(3, coastal_tsunami_height / 8)  # Azaltıldı, max 3 km
            coastal_area = coastal_length_km * inland_penetration_km
            
            # Etkilenen nüfus - DÜZELTİLMİŞ
            # Tüm kıyı yoğunlukta insan olmaz, sadece yerleşim yerleri
            effective_density = coastal_density * 0.3  # Sadece %30'u gerçek yerleşim
            total_affected = int(coastal_area * effective_density)
            
            # 4. Kayıplar - tsunami yüksekliğine göre (kıyıdaki yükseklik)
            if coastal_tsunami_height > 30:
                casualty_rate = 0.35  # %35 kayıp
            elif coastal_tsunami_height > 15:
                casualty_rate = 0.20  # %20 kayıp
            elif coastal_tsunami_height > 5:
                casualty_rate = 0.10  # %10 kayıp
            else:
                casualty_rate = 0.03  # %3 kayıp (küçük tsunami)
            
            casualties = int(total_affected * casualty_rate)
        
        # OKYANUS ÇARPMALARI İÇİN DETAYLI ETKİ DAĞILIMI
        # Tsunami ile ilgili tüm kayıplar (kıyılarda)
        tsunami_casualties = casualties
        
        # Diğer etkiler minimal (okyanus ortasında)
        crater_casualties_ocean = 0  # Denizde kimse yok
        thermal_casualties_ocean = 0  # Termal radyasyon suda emiliyor
        shockwave_casualties_ocean = 0  # Şok dalgası suda zayıflıyor
        wind_casualties_ocean = 0  # Rüzgar etkisi minimal
        earthquake_casualties_ocean = int(casualties * 0.1)  # Kıyılarda sismik etki
        tsunami_direct_casualties = int(casualties * 0.9)  # Tsunami'nin kendisi
        
        return {
            'total_affected': total_affected,
            'estimated_casualties': casualties,
            'casualties_by_zone': {
                'total_destruction': int(casualties * 0.7) if casualties > 0 else 0,
                'heavy_damage': int(casualties * 0.2) if casualties > 0 else 0,
                'moderate_damage': int(casualties * 0.08) if casualties > 0 else 0,
                'light_damage': int(casualties * 0.02) if casualties > 0 else 0
            },
            # YENİ: Detaylı etki türüne göre kayıp dağılımı (okyanus)
            'crater_casualties': crater_casualties_ocean,
            'thermal_casualties': thermal_casualties_ocean,
            'shockwave_casualties': shockwave_casualties_ocean,
            'wind_casualties': wind_casualties_ocean,
            'earthquake_casualties': earthquake_casualties_ocean,
            'tsunami_casualties': tsunami_direct_casualties,
            'population_density': 0,  # Okyanus - direkt popülasyon yok
            'coastal_density': coastal_density,
            'note': f'Ocean impact - Distance to coast: ~{typical_distance_to_coast} km',
            'location_info': f'Tsunami impact zone: {int(coastal_area)} km² of coastline' if coastal_area > 0 else f'Tsunami does NOT reach coast (range: {max_tsunami_range_km} km < distance: {typical_distance_to_coast} km)',
            'data_source': 'Optimized tsunami propagation model',
            'coastal_tsunami_height_m': round(coastal_tsunami_height, 1),
            'tsunami_attenuation_info': f'Initial: {tsunami_height_m:.1f}m → Coastal: {coastal_tsunami_height:.1f}m (distance factor: {distance_factor:.2%})'
        }
    
    # Kara çarpması - GELİŞMİŞ NÜF US MODELİ
    # Önce en yakın şehre bak
    geonames_data = None  # Başlangıç değeri
    nearest_city = get_nearest_city_population(impact_lat, impact_lng, max_distance_km=300)
    
    if nearest_city:
        # Yakın şehir bulundu
        base_density = nearest_city['estimated_density']
        location_info = f"{nearest_city['name']} ({nearest_city['distance_km']:.0f} km uzaklıkta)"
        data_source = f'City-based estimate (Nearest: {nearest_city["name"]})'
    else:
        # Şehir bulunamadı - GeoNames API dene
        geonames_data = get_population_density_from_geonames(impact_lat, impact_lng, radius_km=100)
        
        if geonames_data and geonames_data['density'] > 0:
            # GeoNames'den gelen gerçek veri
            base_density = geonames_data['density']
            location_info = f"{geonames_data['nearest_city']}, {geonames_data['country']} ({geonames_data['distance_km']} km away)"
            data_source = 'GeoNames API (Real Data)'
        else:
            # API başarısız olursa fallback - enleme göre tahmin
            abs_lat = abs(impact_lat)
            
            if abs_lat < 10:  # Ekvator bölgesi
                base_density = 50
            elif abs_lat < 30:  # Tropikal bölge
                base_density = 100
            elif abs_lat < 50:  # Ilıman bölge
                base_density = 150
            else:  # Kutup bölgeleri
                base_density = 5
            
            location_info = f"Lat: {impact_lat:.2f}, Lng: {impact_lng:.2f}"
            data_source = 'Estimated (API unavailable)'
    
    # Alanları hesapla (daire alanı: π * r²)
    total_destruction_area = math.pi * (damage_zones['total_destruction_km'] ** 2)
    heavy_damage_area = math.pi * (damage_zones['heavy_damage_km'] ** 2) - total_destruction_area
    moderate_damage_area = math.pi * (damage_zones['moderate_damage_km'] ** 2) - heavy_damage_area - total_destruction_area
    light_damage_area = math.pi * (damage_zones['light_damage_km'] ** 2) - moderate_damage_area - heavy_damage_area - total_destruction_area
    
    # Popülasyon tahmini (alan * yoğunluk * ölüm oranı)
    casualties_total_destruction = int(total_destruction_area * base_density * 0.95)  # 95% ölüm
    casualties_heavy = int(heavy_damage_area * base_density * 0.60)  # 60% ölüm
    casualties_moderate = int(moderate_damage_area * base_density * 0.25)  # 25% ölüm
    casualties_light = int(light_damage_area * base_density * 0.05)  # 5% ölüm
    
    total_casualties = casualties_total_destruction + casualties_heavy + casualties_moderate + casualties_light
    total_affected = int((total_destruction_area + heavy_damage_area + moderate_damage_area + light_damage_area) * base_density)
    
    # DETAYLI ETKİ TÜRÜNE GÖRE KAYIP DAĞILIMI
    # Krater içinde - tamamen buharlaşma (%100 kayıp)
    crater_radius_km = damage_zones.get('total_destruction_km', 0) / 2
    crater_area = math.pi * (crater_radius_km ** 2)
    crater_casualties = int(crater_area * base_density)
    
    # Fireball (termal radyasyon) - krater dışında ama yakın mesafe
    # Yaklaşık krater yarıçapının 3-5 katı mesafede termal etkiler önemli
    fireball_radius_km = damage_zones.get('heavy_damage_km', 0)
    fireball_area = math.pi * (fireball_radius_km ** 2) - crater_area
    # Termal radyasyondan %40 kayıp (ciddi yanıklar)
    thermal_casualties = int(fireball_area * base_density * 0.4)
    
    # Shock wave (basınç dalgası) - orta mesafe
    shockwave_radius_km = damage_zones.get('moderate_damage_km', 0)
    shockwave_area = math.pi * (shockwave_radius_km ** 2) - math.pi * (fireball_radius_km ** 2)
    # Basınç dalgasından %25 kayıp (kulak zarı patlaması, bina çökmesi)
    shockwave_casualties = int(shockwave_area * base_density * 0.25)
    
    # Wind blast (rüzgar patlaması) - geniş alan
    wind_radius_km = damage_zones.get('light_damage_km', 0)
    wind_area = math.pi * (wind_radius_km ** 2) - math.pi * (shockwave_radius_km ** 2)
    # Rüzgar patlamasından %10 kayıp (uçan enkaz, ağaçlar)
    wind_casualties = int(wind_area * base_density * 0.1)
    
    # Earthquake effect - en geniş alan (hafif hasar yarıçapının 1.5 katı)
    earthquake_radius_km = wind_radius_km * 1.5
    earthquake_area = math.pi * (earthquake_radius_km ** 2) - math.pi * (wind_radius_km ** 2)
    # Depremden %3 kayıp (yapısal hasarlar)
    earthquake_casualties = int(earthquake_area * base_density * 0.03)
    
    result = {
        'total_affected': total_affected,
        'estimated_casualties': total_casualties,
        'casualties_by_zone': {
            'total_destruction': casualties_total_destruction,
            'heavy_damage': casualties_heavy,
            'moderate_damage': casualties_moderate,
            'light_damage': casualties_light
        },
        # YENİ: Detaylı etki türüne göre kayıp dağılımı
        'crater_casualties': crater_casualties,
        'thermal_casualties': thermal_casualties,
        'shockwave_casualties': shockwave_casualties,
        'wind_casualties': wind_casualties,
        'earthquake_casualties': earthquake_casualties,
        'population_density': base_density,
        'location_info': location_info,
        'data_source': data_source
    }
    
    # GeoNames verisi varsa ekle
    if geonames_data:
        result['geonames_data'] = geonames_data
    
    return result


def check_ocean_with_geonames(lat, lng):
    """
    GeoNames Ocean API kullanarak nokta okyanus/deniz mi kontrol eder
    """
    try:
        url = f'http://api.geonames.org/oceanJSON?lat={lat}&lng={lng}&username={GEONAMES_USERNAME}'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if 'ocean' in data and 'name' in data['ocean']:
            return True, data['ocean']['name']
        else:
            return False, "Land"
    except Exception as e:
        print(f"GeoNames Ocean API Error: {e}")
        # API başarısız olursa fallback kullan
        return None, None


def fallback_ocean_check(impact_lat, impact_lng):
    """
    GeoNames API başarısız olursa kullanılacak basit koordinat kontrolü
    Bu yöntem %100 doğru değildir, sadece yaklaşık bir tahmindir
    """
    is_ocean = False
    ocean_name = "Unknown"
    
    # Kutup bölgeleri - büyük ölçüde okyanus (Antarktika hariç)
    if impact_lat < -65:
        # Güney Kutbu - Antarktika ve çevresi
        if impact_lat < -75:
            # Antarktika kıtası olabilir
            ocean_name = "Antarctic Region (Land/Ice)"
            is_ocean = False
        else:
            # Güney Okyanusu
            is_ocean = True
            ocean_name = "Southern Ocean"
    
    elif impact_lat > 70:
        # Kuzey Kutbu - Arctic Ocean
        is_ocean = True
        ocean_name = "Arctic Ocean"
    
    # Pasifik Okyanusu (En büyük okyanus - geniş enlem aralığı)
    # GENİŞLETİLMİŞ: Daha fazla koordinat aralığı
    elif (-65 < impact_lat < 65) and ((100 < impact_lng <= 180) or (-180 < impact_lng < -60)):
        is_ocean = True
        ocean_name = "Pacific Ocean"
    
    # Atlantik Okyanusu (Kuzey ve Güney Atlantik)
    elif (-65 < impact_lat < 70) and (-60 < impact_lng < -10):
        is_ocean = True
        ocean_name = "Atlantic Ocean"
    
    # Hint Okyanusu (Güney Asya, Afrika arası)
    elif (-65 < impact_lat < 25) and (20 < impact_lng < 120):
        is_ocean = True
        ocean_name = "Indian Ocean"
    
    # Akdeniz
    elif (30 < impact_lat < 44) and (-6 < impact_lng < 36):
        # Kara alanlarını hariç tut (basitleştirilmiş)
        is_land = False
        
        # Türkiye anakarası kontrolü
        if (impact_lat > 36.5 and impact_lng > 26 and impact_lng < 36):
            is_land = True
        # Yunanistan kontrolü  
        elif (impact_lat > 38.5 and impact_lng > 19 and impact_lng < 28):
            is_land = True
        # İtalya kontrolü
        elif (impact_lat > 41.5 and impact_lng > 8 and impact_lng < 18):
            is_land = True
        
        if not is_land:
            is_ocean = True
            ocean_name = "Mediterranean Sea"
    
    # Karadeniz
    elif (41 < impact_lat < 47) and (27 < impact_lng < 42):
        is_ocean = True
        ocean_name = "Black Sea"
    
    # Kızıldeniz
    elif (12 < impact_lat < 30) and (32 < impact_lng < 44):
        is_ocean = True
        ocean_name = "Red Sea"
    
    # Basra Körfezi
    elif (24 < impact_lat < 30) and (48 < impact_lng < 57):
        is_ocean = True
        ocean_name = "Persian Gulf"
    
    # Eğer hiçbir okyanusa uymuyorsa kara
    if not is_ocean:
        ocean_name = "Land"
    
    return is_ocean, ocean_name


def check_tsunami_risk(impact_lat, impact_lng, crater_diameter_km, kinetic_energy_joules):
    """
    Tsunami riskini kontrol eder
    GeoNames API ile gerçek okyanus/deniz tespiti yapar
    """
    # Koordinat normalizasyonu: Boylam -180 ile 180 arasında olmalı
    while impact_lng > 180:
        impact_lng -= 360
    while impact_lng < -180:
        impact_lng += 360
    
    # ÖNCELİKLE: GeoNames API ile gerçek kontrol yap
    api_is_ocean, api_ocean_name = check_ocean_with_geonames(impact_lat, impact_lng)
    
    if api_is_ocean is not None:
        # API başarılı - gerçek veriyi kullan
        is_ocean = api_is_ocean
        ocean_name = api_ocean_name
        try:
            print(f"[OK] GeoNames API: Lat={impact_lat:.2f}, Lng={impact_lng:.2f} -> {ocean_name} (Ocean: {is_ocean})")
        except:
            pass
    else:
        # API başarısız - fallback koordinat kontrolü
        try:
            print(f"[WARN] GeoNames API unavailable, using fallback coordinate check")
        except:
            pass
        is_ocean, ocean_name = fallback_ocean_check(impact_lat, impact_lng)
    
    tsunami_risk = "None"
    tsunami_height_m = 0
    tsunami_range_km = 0
    
    if is_ocean:
        # Tsunami yüksekliği ve menzili tahmini
        # Daha gerçekçi formül: Enerji ve krater boyutuna göre
        
        # TNT eşdeğeri (Megaton)
        tnt_megatons = kinetic_energy_joules / (4.184 * 10**15)
        
        # OPTİMİZE EDİLMİŞ TSUNAMI MODELİ
        # Ward & Asphaug (2000) formülü basitleştirilmiş versiyonu
        # Başlangıç tsunami yüksekliği: H₀ ≈ krater_derinliği * 0.6
        crater_depth_estimate = (crater_diameter_km * 1000) / 5  # metre
        
        # Daha gerçekçi başlangıç yüksekliği hesabı
        # Enerji bazlı: H₀ ≈ (E^0.25) / 10
        base_height = (tnt_megatons ** 0.25) * 3  # Daha yumuşak artış
        
        # Krater boyutu faktörü (küçük asteroidler küçük tsunami yapar)
        crater_factor = min(1.0, crater_diameter_km / 2.0)  # 2 km krater = tam etki
        
        # Nihai başlangıç yüksekliği
        initial_height = base_height * crater_factor
        
        if tnt_megatons > 1000:  # Dinozor-killer seviyesi
            tsunami_risk = "Extreme"
            tsunami_height_m = min(300, initial_height * 10)  # Max 300m
            tsunami_range_km = 10000
        elif tnt_megatons > 100:  # Çok büyük çarpma
            tsunami_risk = "Extreme"
            tsunami_height_m = min(100, initial_height * 5)  # Max 100m
            tsunami_range_km = 5000
        elif tnt_megatons > 10:  # Büyük çarpma
            tsunami_risk = "High"
            tsunami_height_m = min(50, initial_height * 3)  # Max 50m
            tsunami_range_km = 3000
        elif tnt_megatons > 1:  # Orta çarpma
            tsunami_risk = "Moderate"
            tsunami_height_m = min(25, initial_height * 2)  # Max 25m
            tsunami_range_km = 1500
        else:  # Küçük çarpma
            tsunami_risk = "Low"
            tsunami_height_m = min(10, initial_height * 1.5)  # Max 10m
            tsunami_range_km = 500
    
    # Eğer hiçbir okyanusa uymuyorsa kara
    if not is_ocean:
        ocean_name = "Land"
    
    # Debug: Log koordinatları
    try:
        print(f"Location check: Lat={impact_lat:.2f}, Lng={impact_lng:.2f} -> {ocean_name} (Ocean: {is_ocean})")
    except:
        pass
    
    return {
        'is_ocean_impact': is_ocean,
        'location_type': ocean_name,
        'tsunami_risk': tsunami_risk,
        'tsunami_height_m': round(tsunami_height_m, 1),
        'tsunami_range_km': round(tsunami_range_km, 0),
        'coordinates': f"{impact_lat:.2f}°, {impact_lng:.2f}°",  # Debug için
        'warning': 'CRITICAL: Coastal areas within range should evacuate immediately!' if tsunami_risk in ['High', 'Extreme'] else 
                   'WARNING: Coastal areas should be alert.' if tsunami_risk == 'Moderate' else
                   'Tsunami risk is minimal.' if tsunami_risk == 'Low' else 'No tsunami risk (land impact).',
        # Popülasyon hesaplaması için ek parametreler
        '_internal_tsunami_height': tsunami_height_m,  # İç kullanım için
        '_internal_tsunami_range': tsunami_range_km
    }


# ============================================================================
# MAIN INTEGRATION: RUMPF ADVANCED IMPACT RISK ASSESSMENT
# ============================================================================

def calculate_advanced_impact_assessment(
    diameter_m, 
    density_kg_m3, 
    velocity_ms, 
    angle_deg, 
    impact_lat, 
    impact_lng,
    water_depth_m=0,
    unsheltered_fraction=0.13,
    grid_resolution_km=5
):
    """
    Rumpf Metodolojisi - Kapsamlı Asteroid Çarpma Risk Değerlendirmesi
    
    TÜM ADIMLAR:
    1. Atmosferik Giriş Analizi
    2. Çarpma Tipi Belirleme
    3. Tehlike Şiddeti Hesaplaması
    4. Maruz Kalma Haritalaması
    5. Hassasiyet ve Kayıp Hesaplaması
    6. Toplama ve Raporlama
    """
    
    # ========== ADIM 1: ATMOSFERİK GİRİŞ ANALİZİ ==========
    energy_data = calculate_kinetic_energy(diameter_m, density_kg_m3, velocity_ms)
    airburst_altitude_km = determine_airburst_altitude(diameter_m, density_kg_m3, velocity_ms, angle_deg)
    
    # ========== ADIM 2: ÇARPMA TİPİ BELİRLEME ==========
    # Okyanus kontrolü
    is_ocean, ocean_name = check_ocean_with_geonames(impact_lat, impact_lng)
    if is_ocean is None:
        is_ocean, ocean_name = fallback_ocean_check(impact_lat, impact_lng)
    
    impact_type_data = determine_impact_type(diameter_m, density_kg_m3, velocity_ms, angle_deg, is_ocean)
    impact_type = impact_type_data['impact_type']
    applicable_hazards = impact_type_data['applicable_hazards']
    
    # Krater hesabı (sadece yere ulaşan çarpmalar için)
    if impact_type != "Airburst":
        atm_data = impact_type_data['atmospheric_data']
        final_diameter_m = atm_data['final_diameter_m']
        final_velocity_ms = atm_data['final_velocity_ms']
        
        angle_rad = math.radians(angle_deg)
        velocity_factor = (final_velocity_ms / 12000) ** 0.44
        angle_factor = (math.sin(angle_rad)) ** 0.33
        crater_diameter_m = 1.8 * final_diameter_m * velocity_factor * angle_factor * 13
        crater_radius_m = crater_diameter_m / 2
    else:
        crater_diameter_m = 0
        crater_radius_m = 0
    
    # ========== ADIM 3 & 4: TEHLİKE ŞİDDETİ VE MARUZ KALMA HARITALAMASI ==========
    # Maksimum etki yarıçapını belirle
    max_radius_km = max(50, (energy_data['kinetic_energy_joules'] ** 0.33) / 5000)
    max_radius_km = min(max_radius_km, 500)  # Maksimum 500 km
    
    # Grid oluştur
    try:
        print(f"Creating population grid with {max_radius_km} km radius...")
    except:
        pass
    grid_cells = create_population_grid(impact_lat, impact_lng, max_radius_km, grid_resolution_km)
    try:
        print(f"Grid created with {len(grid_cells)} cells")
    except:
        pass
    
    # ========== ADIM 5: HASSASİYET VE KAYIP HESAPLAMALARI ==========
    # Her tehlike için toplam kayıplar
    casualties_by_hazard = {
        'overpressure': 0,
        'wind_blast': 0,
        'thermal_radiation': 0,
        'seismic': 0,
        'ejecta': 0,
        'cratering': 0,
        'tsunami': 0
    }
    
    # Sismik büyüklük (global)
    seismic_magnitude = calculate_seismic_magnitude(energy_data['kinetic_energy_joules'])
    
    # Her grid hücresi için tehlike şiddetini ve kayıpları hesapla
    sheltered_fraction = 1 - unsheltered_fraction
    
    for cell in grid_cells:
        distance_m = cell['distance_m']
        population = cell['population']
        
        if population < 0.1:  # Çok az nüfus varsa atla
            continue
        
        # Kraterleşme (sadece krater içi)
        if 'cratering' in applicable_hazards:
            crater_loss = crater_casualties(crater_radius_m, distance_m, population)
            casualties_by_hazard['cratering'] += crater_loss
            
            # Krater içindeyse diğer tehlikeleri hesaplama (herkes ölmüş)
            if crater_loss >= population * 0.99:
                continue
        
        # Aşırı Basınç
        if 'overpressure' in applicable_hazards:
            overpressure_pa = calculate_overpressure(distance_m, energy_data['kinetic_energy_joules'], airburst_altitude_km)
            casualties_by_hazard['overpressure'] += overpressure_casualties(overpressure_pa, population, sheltered_fraction)
        
        # Rüzgar Patlaması
        if 'wind_blast' in applicable_hazards:
            wind_speed_ms = calculate_wind_blast(distance_m, energy_data['kinetic_energy_joules'], airburst_altitude_km)
            casualties_by_hazard['wind_blast'] += enhanced_fujita_scale_casualties(wind_speed_ms, population, sheltered_fraction)
        
        # Termal Radyasyon
        if 'thermal_radiation' in applicable_hazards:
            thermal_flux = calculate_thermal_radiation(distance_m, energy_data['kinetic_energy_joules'], airburst_altitude_km)
            casualties_by_hazard['thermal_radiation'] += thermal_burn_casualties(thermal_flux, population, sheltered_fraction)
        
        # Sismik Sarsıntı
        if 'seismic' in applicable_hazards:
            casualties_by_hazard['seismic'] += seismic_casualties(seismic_magnitude, population, sheltered_fraction)
        
        # Ejekta
        if 'ejecta' in applicable_hazards and crater_diameter_m > 0:
            ejecta_thickness = calculate_ejecta_thickness(distance_m, crater_diameter_m)
            casualties_by_hazard['ejecta'] += ejecta_load_casualties(ejecta_thickness, population, sheltered_fraction)
    
    # Tsunami (ayrı hesaplama - kıyı bölgeleri için)
    if 'tsunami' in applicable_hazards and is_ocean:
        # Basitleştirilmiş tsunami kayıp tahmini
        tsunami_data = check_tsunami_risk(impact_lat, impact_lng, crater_diameter_m / 1000, energy_data['kinetic_energy_joules'])
        tsunami_casualties = estimate_population_affected(
            impact_lat, impact_lng, 
            {'total_destruction_km': 0, 'heavy_damage_km': 0, 'moderate_damage_km': 0, 'light_damage_km': 0},
            is_ocean, ocean_name,
            tsunami_data.get('_internal_tsunami_height', 0),
            tsunami_data.get('_internal_tsunami_range', 0)
        )
        casualties_by_hazard['tsunami'] = tsunami_casualties.get('estimated_casualties', 0)
    
    # ========== ADIM 6: TOPLAMA VE RAPORLAMA ==========
    # Her tehlikeden en yüksek kayıp sayısını al (çakışmaları önlemek için)
    # Not: Gerçek Rumpf metodolojisinde daha karmaşık bir birleştirme yapılır
    total_casualties = max(casualties_by_hazard.values())  # En yıkıcı tehlike
    
    # Alternatif: Tüm tehlikelerin toplamı (üst sınır tahmini)
    total_casualties_sum = sum(casualties_by_hazard.values())
    
    # Ortalama olarak en yüksek ve toplamın ortasını alalım
    total_casualties = (total_casualties + total_casualties_sum) / 3
    
    return {
        'impact_type': impact_type,
        'kinetic_energy_mt': energy_data['tnt_megatons'],
        'total_casualties': int(total_casualties),
        'casualties_by_hazard': {k: int(v) for k, v in casualties_by_hazard.items()},
        'parameters': {
            'diameter_m': diameter_m,
            'density_kg_m3': density_kg_m3,
            'velocity_ms': velocity_ms,
            'angle_deg': angle_deg,
            'impact_location': f"{impact_lat:.2f}°, {impact_lng:.2f}°",
            'crater_diameter_m': crater_diameter_m,
            'airburst_altitude_km': airburst_altitude_km,
            'seismic_magnitude': round(seismic_magnitude, 2),
            'unsheltered_fraction': unsheltered_fraction,
            'grid_cells_analyzed': len(grid_cells)
        }
    }


def format_results_as_markdown(results):
    """
    Sonuçları Markdown tablosu olarak formatla
    """
    markdown = "# Asteroid Çarpma Risk Değerlendirmesi\n\n"
    markdown += "## C. Rumpf Metodolojisi - Gelişmiş Analiz\n\n"
    markdown += "---\n\n"
    
    markdown += "| Kategori | Değer |\n"
    markdown += "|----------|-------|\n"
    markdown += "| **Özet Bilgiler** | |\n"
    markdown += f"| Çarpma Tipi | **{results['impact_type']}** |\n"
    markdown += f"| Kinetik Enerji (MT) | **{results['kinetic_energy_mt']:.2f}** Megaton TNT |\n"
    markdown += f"| Toplam Beklenen Kayıplar | **{results['total_casualties']:,}** kişi |\n"
    markdown += "| | |\n"
    markdown += "| **Tehlikeye Göre Kayıp Dağılımı** | |\n"
    markdown += f"| Aşırı Basınç | {results['casualties_by_hazard']['overpressure']:,} |\n"
    markdown += f"| Rüzgar Patlaması | {results['casualties_by_hazard']['wind_blast']:,} |\n"
    markdown += f"| Termal Radyasyon | {results['casualties_by_hazard']['thermal_radiation']:,} |\n"
    markdown += f"| Sismik Sarsıntı | {results['casualties_by_hazard']['seismic']:,} |\n"
    markdown += f"| Ejekta Püskürtüsü | {results['casualties_by_hazard']['ejecta']:,} |\n"
    markdown += f"| Kraterleşme | {results['casualties_by_hazard']['cratering']:,} |\n"
    markdown += f"| Tsunami | {results['casualties_by_hazard']['tsunami']:,} |\n"
    markdown += "| | |\n"
    markdown += "| **Parametreler** | |\n"
    markdown += f"| Asteroid Çapı | {results['parameters']['diameter_m']:.1f} m |\n"
    markdown += f"| Yoğunluk | {results['parameters']['density_kg_m3']:.0f} kg/m³ |\n"
    markdown += f"| Çarpma Hızı | {results['parameters']['velocity_ms']:.0f} m/s |\n"
    markdown += f"| Çarpma Açısı | {results['parameters']['angle_deg']:.0f}° |\n"
    markdown += f"| Konum | {results['parameters']['impact_location']} |\n"
    markdown += f"| Krater Çapı | {results['parameters']['crater_diameter_m']:.1f} m |\n"
    markdown += f"| Havada İnfilak İrtifası | {results['parameters']['airburst_altitude_km']:.1f} km |\n"
    markdown += f"| Sismik Büyüklük | {results['parameters']['seismic_magnitude']:.2f} Richter |\n"
    markdown += f"| Korunmasız Nüfus | %{results['parameters']['unsheltered_fraction']*100:.0f} |\n"
    markdown += f"| Analiz Edilen Grid Hücresi | {results['parameters']['grid_cells_analyzed']} |\n"
    
    markdown += "\n---\n\n"
    markdown += "*Bu analiz C. Rumpf ve arkadaşlarının 'Asteroid Impact Risk' metodolojisine dayanmaktadır.*\n"
    
    return markdown


@app.route('/api/calculate_impact', methods=['POST'])
def calculate_impact():
    """Calculate impact energy and crater size."""
    try:
        data = request.get_json()
        
        diameter_m = float(data.get('diameter_m', 100))
        velocity_ms = float(data.get('velocity_ms', 20000))
        angle_deg = float(data.get('angle_deg', 45))
        density = float(data.get('density', 3000))  # Taşlı asteroid için tipik yoğunluk
        impact_lat = data.get('impact_lat', 41.0082)
        impact_lng = data.get('impact_lng', 28.9784)
        
        # ÖNEMLİ: Atmosferik giriş hesaplaması
        atmospheric_data = calculate_atmospheric_entry(diameter_m, velocity_ms, density, angle_deg)
        
        # Yere ulaşan gerçek değerler (atmosferde yanma sonrası)
        final_diameter_m = atmospheric_data['final_diameter_m']
        final_velocity_ms = atmospheric_data['final_velocity_ms']
        final_mass_kg = atmospheric_data['final_mass_kg']
        
        # Eğer asteroid tamamen yandıysa
        if not atmospheric_data['reaches_ground']:
            # Hava patlaması (airburst) - yine de hasar var ama krater yok
            final_diameter_m = max(1, final_diameter_m)  # Minimum 1m
            final_velocity_ms = max(100, final_velocity_ms)  # Minimum hız
        
        # Asteroid kütlesini hesapla (atmosferden sonra)
        radius_m = final_diameter_m / 2
        volume_m3 = (4/3) * math.pi * (radius_m ** 3)
        mass_kg = volume_m3 * density
        
        # Kinetik enerji: E = 1/2 * m * v² (atmosferden sonraki değerlerle)
        kinetic_energy_joules = 0.5 * final_mass_kg * (final_velocity_ms ** 2)
        
        # TNT eşdeğeri (1 ton TNT = 4.184 × 10^9 Joules)
        tnt_equivalent_tons = kinetic_energy_joules / (4.184 * 10**9)
        tnt_equivalent_megatons = tnt_equivalent_tons / 10**6
        
        # Krater çapı tahmini (Collins et al. 2005 formülü basitleştirilmiş versiyonu)
        # D_crater ≈ 1.8 * D_asteroid * (velocity/12000)^0.44 * sin(angle)^0.33
        # Atmosferden sonraki değerlerle hesaplanır
        angle_rad = math.radians(angle_deg)
        velocity_factor = (final_velocity_ms / 12000) ** 0.44
        angle_factor = (math.sin(angle_rad)) ** 0.33
        crater_diameter_m = 1.8 * final_diameter_m * velocity_factor * angle_factor * 13
        
        # Hava patlaması durumunda krater olmayabilir veya çok küçük olabilir
        if not atmospheric_data['reaches_ground']:
            crater_diameter_m = crater_diameter_m * 0.1  # Çok küçük krater veya hiç yok
        
        # Krater derinliği (yaklaşık olarak çapın 1/5'i)
        crater_depth_m = crater_diameter_m / 5
        
        # Etki yarıçapı (hasar alanları)
        # Yakındaki bölgede tam yıkım (krater yarıçapının 2 katı)
        total_destruction_radius_km = (crater_diameter_m / 2) * 2 / 1000
        
        # Ağır hasar (krater yarıçapının 5 katı)
        heavy_damage_radius_km = (crater_diameter_m / 2) * 5 / 1000
        
        # Orta hasar (enerji bazlı tahmin)
        moderate_damage_radius_km = (kinetic_energy_joules ** 0.33) / 10000
        
        # Hafif hasar
        light_damage_radius_km = moderate_damage_radius_km * 2
        
        # Hasar bölgeleri
        damage_zones = {
            'total_destruction_km': total_destruction_radius_km,
            'heavy_damage_km': heavy_damage_radius_km,
            'moderate_damage_km': moderate_damage_radius_km,
            'light_damage_km': light_damage_radius_km
        }
        
        # Tsunami riski kontrolü (önce bunu yap çünkü is_ocean bilgisi gerekli)
        tsunami_data = check_tsunami_risk(impact_lat, impact_lng, crater_diameter_m / 1000, kinetic_energy_joules)
        
        # Popülasyon etkisi tahmini (okyanus bilgisi ve tsunami parametreleri ile)
        population_impact = estimate_population_affected(
            impact_lat, 
            impact_lng, 
            damage_zones, 
            tsunami_data['is_ocean_impact'],
            tsunami_data.get('location_type', 'Ocean'),
            tsunami_data.get('_internal_tsunami_height', 0),
            tsunami_data.get('_internal_tsunami_range', 0)
        )
        
        return jsonify({
            'success': True,
            'impact_data': {
                'atmospheric_entry': atmospheric_data,  # YENİ: Atmosferik giriş verisi
                'mass_kg': mass_kg,
                'mass_tons': mass_kg / 1000,
                'kinetic_energy_joules': kinetic_energy_joules,
                'tnt_equivalent_tons': tnt_equivalent_tons,
                'tnt_equivalent_megatons': tnt_equivalent_megatons,
                'crater_diameter_m': crater_diameter_m,
                'crater_diameter_km': crater_diameter_m / 1000,
                'crater_depth_m': crater_depth_m,
                'damage_zones': damage_zones,
                'population_impact': population_impact,
                'tsunami_data': tsunami_data
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/calculate_seismic_effect', methods=['POST'])
def calculate_seismic_effect():
    """Convert impact energy to seismic magnitude."""
    try:
        data = request.get_json()
        kinetic_energy_joules = float(data.get('kinetic_energy_joules', 0))
        
        if kinetic_energy_joules <= 0:
            return jsonify({
                'success': False,
                'error': 'Geçersiz enerji değeri'
            }), 400
        
        # Richter ölçeği formülü: M = (log10(E) - 4.8) / 1.5
        # E: Joule cinsinden enerji
        magnitude_richter = (math.log10(kinetic_energy_joules) - 4.8) / 1.5
        
        # Moment magnitude (daha modern): Mw = (2/3) * log10(E) - 6.0
        magnitude_moment = (2/3) * math.log10(kinetic_energy_joules) - 6.0
        
        # Etki açıklaması
        if magnitude_richter < 4.0:
            description = "Hafif titreşimler, lokal etkiler"
            impact_level = "low"
        elif magnitude_richter < 6.0:
            description = "Orta şiddette deprem, bölgesel hasar"
            impact_level = "moderate"
        elif magnitude_richter < 7.5:
            description = "Güçlü deprem, yaygın hasar"
            impact_level = "high"
        else:
            description = "Yıkıcı deprem, kıtasal etkiler"
            impact_level = "catastrophic"
        
        # Hissedilme mesafesi tahmini (km)
        felt_distance_km = 10 ** (0.5 * magnitude_richter)
        
        return jsonify({
            'success': True,
            'seismic_data': {
                'magnitude_richter': round(magnitude_richter, 2),
                'magnitude_moment': round(magnitude_moment, 2),
                'description': description,
                'impact_level': impact_level,
                'felt_distance_km': round(felt_distance_km, 2)
            }
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.route('/api/simulate_atmospheric_entry', methods=['POST'])
def simulate_entry():
    """Atmospheric entry simulation endpoint."""
    try:
        data = request.get_json()
        
        # Parametreleri al
        diameter_m = float(data.get('diameter_m'))
        velocity_ms = float(data.get('velocity_ms'))
        entry_angle_deg = float(data.get('entry_angle_deg', 18))
        material_type = data.get('material_type', 'chondrite').lower()
        initial_altitude_m = float(data.get('initial_altitude_m', 100000))
        fragmentation_model = data.get('fragmentation_model', 'pancake').lower()
        time_step = float(data.get('time_step', 0.01))
        
        # Validasyon
        if diameter_m <= 0 or diameter_m > 10000:
            return jsonify({
                'success': False,
                'error': 'Çap 0-10,000 metre arasında olmalıdır'
            }), 400
        
        if velocity_ms < 5000 or velocity_ms > 75000:
            return jsonify({
                'success': False,
                'error': 'Hız 5,000-75,000 m/s arasında olmalıdır'
            }), 400
        
        if entry_angle_deg < 5 or entry_angle_deg > 90:
            return jsonify({
                'success': False,
                'error': 'Giriş açısı 5-90 derece arasında olmalıdır'
            }), 400
        
        if material_type not in ['chondrite', 'stony', 'iron', 'cometary']:
            return jsonify({
                'success': False,
                'error': 'Geçersiz malzeme tipi'
            }), 400
        
        # Simülasyonu çalıştır
        try:
            print(f"\n{'='*60}")
            print(f"ATMOSPHERIC ENTRY SIMULATION")
            print(f"{'='*60}")
            print(f"Diameter: {diameter_m} m")
            print(f"Velocity: {velocity_ms} m/s ({velocity_ms/1000:.1f} km/s)")
            print(f"Angle: {entry_angle_deg} deg")
            print(f"Material: {material_type}")
            print(f"Fragmentation: {fragmentation_model}")
            print(f"{'='*60}\n")
        except:
            pass
        
        results = simulate_atmospheric_entry_advanced(
            diameter_m=diameter_m,
            velocity_ms=velocity_ms,
            entry_angle_deg=entry_angle_deg,
            material_type=material_type,
            initial_altitude_m=initial_altitude_m,
            fragmentation_model=fragmentation_model,
            dt=time_step
        )
        
        try:
            print(f"\nRESULTS:")
            print(f"  Airburst Altitude: {results['key_results']['airburst_altitude_km']:.1f} km")
            print(f"  Energy: {results['key_results']['tnt_equivalent_kilotons']:.1f} kt")
            print(f"  Fragmented: {results['key_results']['fragmented']}")
            print(f"{'='*60}\n")
        except:
            pass
        
        return jsonify(results)
    
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Eksik parametre: {str(e)}'
        }), 400
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Simülasyon hatası: {str(e)}'
        }), 500


@app.route('/api/simulate_chelyabinsk', methods=['GET'])
def simulate_chelyabinsk():
    """Chelyabinsk 2013 event simulation for validation."""
    try:
        # Çelyabinsk parametreleri
        # Kaynak: Brown et al. (2013), Popova et al. (2013)
        results = simulate_atmospheric_entry_advanced(
            diameter_m=19,  # 18-20 m
            velocity_ms=19000,  # ~19 km/s
            entry_angle_deg=18,  # ~18 derece
            material_type='chondrite',  # LL kondrit
            initial_altitude_m=100000,
            fragmentation_model='pancake',  # Sürekli parçalanma gözlemlendi
            dt=0.01
        )
        
        # Gözlemsel verilerle karşılaştırma
        observed = {
            'airburst_altitude_km': 27.5,  # 27-30 km arası
            'energy_kilotons': 450,  # 400-500 kt arası
            'initial_mass_tons': 11000,  # 9,000-13,000 ton
            'entry_velocity_km_s': 19.0
        }
        
        simulated = {
            'airburst_altitude_km': results['key_results']['airburst_altitude_km'],
            'energy_kilotons': results['key_results']['tnt_equivalent_kilotons'],
            'initial_mass_tons': results['initial_conditions']['initial_mass_kg'] / 1000,
            'entry_velocity_km_s': results['initial_conditions']['velocity_ms'] / 1000
        }
        
        # Hata hesaplama
        altitude_error = abs(simulated['airburst_altitude_km'] - observed['airburst_altitude_km']) / observed['airburst_altitude_km'] * 100
        energy_error = abs(simulated['energy_kilotons'] - observed['energy_kilotons']) / observed['energy_kilotons'] * 100
        
        comparison = {
            'observed': observed,
            'simulated': simulated,
            'errors': {
                'altitude_error_percent': altitude_error,
                'energy_error_percent': energy_error
            },
            'validation': {
                'altitude_match': altitude_error < 15,  # %15 içinde
                'energy_match': energy_error < 20,  # %20 içinde
                'overall_valid': altitude_error < 15 and energy_error < 20
            }
        }
        
        return jsonify({
            'success': True,
            'event_name': 'Chelyabinsk Superbolide (2013)',
            'simulation_results': results,
            'comparison': comparison,
            'references': [
                'Brown et al. (2013) - The Flux of Small Near-Earth Objects Colliding with the Earth',
                'Popova et al. (2013) - Chelyabinsk Airburst, Damage Assessment, Meteorite Recovery',
                'Borovička et al. (2013) - The Trajectory, Structure and Origin of the Chelyabinsk Asteroidal Impactor'
            ]
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Simülasyon hatası: {str(e)}'
        }), 500


@app.route('/api/calculate_advanced_impact', methods=['POST'])
def calculate_advanced_impact():
    """Advanced impact assessment using Rumpf methodology."""
    try:
        data = request.get_json()
        
        # Gerekli parametreler
        diameter_m = float(data.get('diameter_m'))
        density_kg_m3 = float(data.get('density_kg_m3', 3000))
        velocity_ms = float(data.get('velocity_ms'))
        angle_deg = float(data.get('angle_deg', 45))
        impact_lat = float(data.get('impact_lat'))
        impact_lng = float(data.get('impact_lng'))
        
        # Opsiyonel parametreler
        water_depth_m = float(data.get('water_depth_m', 0))
        unsheltered_fraction = float(data.get('unsheltered_fraction', 0.13))
        grid_resolution_km = float(data.get('grid_resolution_km', 5))
        return_markdown = data.get('return_markdown', False)
        
        # Parametre validasyonu
        if diameter_m <= 0 or diameter_m > 10000:
            return jsonify({
                'success': False,
                'error': 'Asteroid çapı 0-10,000 metre arasında olmalıdır'
            }), 400
        
        if velocity_ms <= 0 or velocity_ms > 100000:
            return jsonify({
                'success': False,
                'error': 'Çarpma hızı 0-100,000 m/s arasında olmalıdır'
            }), 400
        
        if angle_deg < 0 or angle_deg > 90:
            return jsonify({
                'success': False,
                'error': 'Çarpma açısı 0-90 derece arasında olmalıdır'
            }), 400
        
        if abs(impact_lat) > 90 or abs(impact_lng) > 180:
            return jsonify({
                'success': False,
                'error': 'Geçersiz koordinatlar'
            }), 400
        
        # Gelişmiş impact assessment hesapla
        try:
            print(f"\n{'='*60}")
            print(f"RUMPF METHODOLOGY - ADVANCED IMPACT ASSESSMENT")
            print(f"{'='*60}")
            print(f"Diameter: {diameter_m} m")
            print(f"Density: {density_kg_m3} kg/m3")
            print(f"Velocity: {velocity_ms} m/s")
            print(f"Angle: {angle_deg} deg")
            print(f"Location: {impact_lat:.2f}, {impact_lng:.2f}")
            print(f"{'='*60}\n")
        except:
            pass  # Windows encoding hatalarını yoksay
        
        results = calculate_advanced_impact_assessment(
            diameter_m=diameter_m,
            density_kg_m3=density_kg_m3,
            velocity_ms=velocity_ms,
            angle_deg=angle_deg,
            impact_lat=impact_lat,
            impact_lng=impact_lng,
            water_depth_m=water_depth_m,
            unsheltered_fraction=unsheltered_fraction,
            grid_resolution_km=grid_resolution_km
        )
        
        try:
            print(f"\nRESULTS:")
            print(f"  Impact Type: {results['impact_type']}")
            print(f"  Energy: {results['kinetic_energy_mt']:.2f} MT")
            print(f"  Total Casualties: {results['total_casualties']:,}")
            print(f"{'='*60}\n")
        except:
            pass  # Windows encoding hatalarını yoksay
        
        if return_markdown:
            # Markdown formatında döndür
            markdown_output = format_results_as_markdown(results)
            return jsonify({
                'success': True,
                'markdown': markdown_output,
                'results': results
            })
        else:
            # JSON formatında döndür
            return jsonify({
                'success': True,
                'results': results
            })
    
    except KeyError as e:
        return jsonify({
            'success': False,
            'error': f'Eksik parametre: {str(e)}'
        }), 400
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Hesaplama hatası: {str(e)}'
        }), 500


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/formulas')
def formulas():
    return render_template('formulas.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

