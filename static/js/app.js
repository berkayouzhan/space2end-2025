/* ============================================================================
   ADIM 3.4: BACKEND İLE İLETİŞİM VE ANA UYGULAMA MANTIĞI
   ============================================================================ */

// Global state
const appState = {
    asteroidData: null,
    impactData: null,
    seismicData: null,
    currentLanguage: 'en', // Default language is English
    dataSource: 'api' // 'api' or 'database'
};

// ============================================================================
// Data Source Switcher
// ============================================================================

function switchDataSource(source) {
    appState.dataSource = source;
    
    // Update button states
    const apiBtn = document.getElementById('dataSourceApi');
    const dbBtn = document.getElementById('dataSourceDatabase');
    
    if (source === 'api') {
        apiBtn.classList.add('active');
        apiBtn.style.border = '2px solid var(--primary-color)';
        apiBtn.style.background = 'rgba(59, 130, 246, 0.2)';
        dbBtn.classList.remove('active');
        dbBtn.style.border = '2px solid var(--border-color)';
        dbBtn.style.background = 'rgba(26, 31, 58, 0.5)';
    } else {
        dbBtn.classList.add('active');
        dbBtn.style.border = '2px solid var(--primary-color)';
        dbBtn.style.background = 'rgba(59, 130, 246, 0.2)';
        apiBtn.classList.remove('active');
        apiBtn.style.border = '2px solid var(--border-color)';
        apiBtn.style.background = 'rgba(26, 31, 58, 0.5)';
    }
    
    // Show notification
    const message = source === 'api' 
        ? (appState.currentLanguage === 'en' ? 'Using Live NASA API data' : 'Canlı NASA API verileri kullanılıyor')
        : (appState.currentLanguage === 'en' ? 'Using pre-loaded database' : 'Önyüklenmiş veritabanı kullanılıyor');
    showInfo(message);
    
    console.log(`Data source switched to: ${source}`);
}

// ============================================================================
// Language Switcher
// ============================================================================

function switchLanguage(lang) {
    appState.currentLanguage = lang;
    
    // Update button states
    document.getElementById('lang-en').classList.toggle('active', lang === 'en');
    document.getElementById('lang-tr').classList.toggle('active', lang === 'tr');
    
    // Update all elements with data-lang attributes
    const elements = document.querySelectorAll('[data-lang-en][data-lang-tr]');
    elements.forEach(el => {
        const text = el.getAttribute(`data-lang-${lang}`);
        if (text) {
            if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                el.value = text;
            } else if (el.tagName === 'OPTION') {
                el.textContent = text;
            } else {
                el.textContent = text;
            }
        }
    });
    
    // Update HTML lang attribute
    document.documentElement.lang = lang;
    
    // Update FAB text
    const fabText = document.querySelector('.fab-text');
    if (fabText) {
        fabText.textContent = lang === 'en' ? 'Run Simulation' : 'Simülasyonu Başlat';
    }
    
    // Update simulation button text
    const simBtn = document.getElementById('runSimulationBtn');
    if (simBtn && !simBtn.disabled) {
        simBtn.innerHTML = lang === 'en' ? '🚀 Run Simulation' : '🚀 Simülasyonu Başlat';
    }
    
    // If results are visible, refresh them with new language
    if (appState.impactData && appState.seismicData) {
        displaySimulationResults(appState.impactData, appState.seismicData);
    }
    
    // Update 3D visualizations if they exist
    if (appState.impactData) {
        try {
            if (document.getElementById('craterTopography').children.length > 0) {
                update3DCraterTopography(appState.impactData);
            }
            if (document.getElementById('craterCrossSection').children.length > 0) {
                updateCraterCrossSection(appState.impactData);
            }
        } catch (e) {
            // Ignore errors if visualizations not yet created
        }
    }
    
    console.log(`Language switched to: ${lang === 'en' ? 'English' : 'Türkçe'}`);
}

// ============================================================================
// Sayfa Yüklendiğinde Başlangıç
// ============================================================================

document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
});

function initializeApp() {
    // UI Event Listeners
    setupEventListeners();
    
    // Slider değerlerini güncelle
    updateSliderValues();
    
    // Başlangıç verisini yükle
    loadSampleAsteroid();
}

// ============================================================================
// Event Listeners
// ============================================================================

function setupEventListeners() {
    // Slider'lar için real-time değer güncelleme
    const sliders = ['diameter', 'velocity', 'angle'];
    sliders.forEach(id => {
        const slider = document.getElementById(id);
        if (slider) {
            slider.addEventListener('input', () => updateSliderValues());
        }
    });

    // Asteroid kaynağı değişimi
    document.getElementById('asteroidSource').addEventListener('change', (e) => {
        const source = e.target.value;
        const solarPanel = document.getElementById('solarSystemSelection');
        const cometsPanel = document.getElementById('cometsSelection');
        
        solarPanel.style.display = source === 'solar' ? 'block' : 'none';
        cometsPanel.style.display = source === 'comets' ? 'block' : 'none';
        
        // Otomatik yükle (custom hariç)
        if (source !== 'custom') {
            loadAsteroidData();
        }
    });

    // Asteroid yükleme
    document.getElementById('loadAsteroidBtn').addEventListener('click', loadAsteroidData);

    // Simülasyon başlatma
    document.getElementById('runSimulationBtn').addEventListener('click', runSimulation);
}

function updateSliderValues() {
    // Tüm slider değerlerini ekrana yansıt
    const sliderMappings = {
        'diameter': 'diameterValue',
        'velocity': 'velocityValue',
        'angle': 'angleValue'
    };

    Object.entries(sliderMappings).forEach(([sliderId, valueId]) => {
        const slider = document.getElementById(sliderId);
        const valueSpan = document.getElementById(valueId);
        
        if (slider && valueSpan) {
            let value = slider.value;
            
            // Hız için binlik ayracı ekle
            if (sliderId === 'velocity') {
                value = parseInt(value).toLocaleString('tr-TR');
            }
            
            valueSpan.textContent = value;
        }
    });
}

// ============================================================================
// ADIM 2.1: Asteroid Verisi Yükleme
// ============================================================================

async function loadAsteroidData() {
    const source = document.getElementById('asteroidSource').value;
    const loadBtn = document.getElementById('loadAsteroidBtn');
    
    loadBtn.disabled = true;
    loadBtn.innerHTML = '<span class="loading"></span>';

    try {
        let url = '/api/get_asteroid_data';
        
        // Kaynak tipine göre panel göster/gizle
        const solarPanel = document.getElementById('solarSystemSelection');
        const cometsPanel = document.getElementById('cometsSelection');
        solarPanel.style.display = 'none';
        cometsPanel.style.display = 'none';
        
        // Add data source parameter
        const dataSourceParam = '&data_source=' + appState.dataSource;
        
        if (source === 'solar') {
            solarPanel.style.display = 'block';
            const selectedAsteroid = document.getElementById('solarAsteroid').value;
            url += '?source=solar&asteroid=' + selectedAsteroid + dataSourceParam;
        } else if (source === 'comets') {
            cometsPanel.style.display = 'block';
            const selectedObj = document.getElementById('cometObject').value;
            url += '?source=comets&object=' + selectedObj + dataSourceParam;
        } else if (source === 'chicxulub') {
            url += '?source=chicxulub' + dataSourceParam;
        } else if (source === 'custom') {
            showInfo(t('manualInputInfo'));
            loadBtn.disabled = false;
            const loadText = appState.currentLanguage === 'en' ? 'Load' : 'Yükle';
            loadBtn.textContent = loadText;
            return;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (data.success && data.asteroid) {
            appState.asteroidData = data.asteroid;
            updateUIWithAsteroidData(data.asteroid);
            
            showSuccess(`${t('asteroidLoaded')}: ${data.asteroid.name}`);
        } else {
            showError(t('asteroidLoadFailed') + ': ' + (data.error || t('unknownError')));
        }
    } catch (error) {
        console.error('API Error:', error);
        showError(t('connectionError') + ': ' + error.message);
    } finally {
        loadBtn.disabled = false;
        const loadText = appState.currentLanguage === 'en' ? 'Load' : 'Yükle';
        loadBtn.textContent = loadText;
    }
}

function loadSampleAsteroid() {
    // Başlangıçta örnek veri yükle
    loadAsteroidData();
}

function updateUIWithAsteroidData(asteroid) {
    document.getElementById('asteroidName').value = asteroid.name;
    
    // Çap için dinamik max değeri ayarla (Chicxulub gibi büyük asteroidler için)
    const diameterSlider = document.getElementById('diameter');
    const diameter = Math.round(asteroid.diameter_m);
    if (diameter > 1000) {
        // Büyük asteroidler için max değeri artır
        diameterSlider.max = Math.max(20000, diameter * 1.2); // 20 km'ye kadar
    } else {
        diameterSlider.max = 1000; // Normal max
    }
    diameterSlider.value = diameter;
    
    document.getElementById('velocity').value = Math.round(asteroid.velocity_kmh);
    updateSliderValues();
}

// ============================================================================
// ADIM 2.2 & 2.3: Simülasyon Çalıştırma
// ============================================================================

async function runSimulation() {
    const btn = document.getElementById('runSimulationBtn');
    const fab = document.getElementById('fabSimulation');
    
    btn.disabled = true;
    const calculatingText = appState.currentLanguage === 'en' ? '⏳ Calculating...' : '⏳ Hesaplanıyor...';
    btn.innerHTML = calculatingText;
    
    // FAB animation
    if (fab) {
        fab.classList.add('loading');
        fab.querySelector('.fab-icon').textContent = '⏳';
    }

    try {
        // HER ZAMAN GELİŞMİŞ SİMÜLASYON ÇALIŞTIR
        const impactLocation = window.impactMap ? impactMap.getImpactLocation() : { lat: 41.0082, lng: 28.9784 };
        
        const params = {
            diameter_m: parseFloat(document.getElementById('diameter').value),
            velocity_ms: parseFloat(document.getElementById('velocity').value) * 1000 / 3600, // km/h -> m/s
            angle_deg: parseFloat(document.getElementById('angle').value),
            density: 3000,  // Sabit yoğunluk (taşlı asteroid)
            density_kg_m3: 3000,
            entry_angle_deg: parseFloat(document.getElementById('angle').value),
            impact_lat: impactLocation.lat,
            impact_lng: impactLocation.lng
        };

        // Temel hesaplamaları yap (harita ve atmosfer için)
        await runBasicSimulation(params);
        
        showSuccess(t('simulationCompleted'));

    } catch (error) {
        console.error('Simulation Error:', error);
        showError(t('simulationError') + ': ' + error.message);
    } finally {
        btn.disabled = false;
        const btnText = appState.currentLanguage === 'en' ? '🚀 Run Simulation' : '🚀 Simülasyonu Başlat';
        btn.innerHTML = btnText;
        
        // Reset FAB
        if (fab) {
            fab.classList.remove('loading');
            fab.querySelector('.fab-icon').textContent = '🚀';
        }
    }
}

// Temel simülasyon (eski)
async function runBasicSimulation(params) {
    // 1. Çarpma etkisini hesapla
    const impactResponse = await fetch('/api/calculate_impact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params)
    });
        
    const impactResult = await impactResponse.json();

    if (!impactResult.success) {
        throw new Error(impactResult.error || t('impactCalculationFailed'));
    }

    appState.impactData = impactResult.impact_data;

    // 2. Sismik etkiyi hesapla
    const seismicResponse = await fetch('/api/calculate_seismic_effect', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            kinetic_energy_joules: impactResult.impact_data.kinetic_energy_joules
        })
    });

    const seismicResult = await seismicResponse.json();

    if (!seismicResult.success) {
        throw new Error(seismicResult.error || t('seismicCalculationFailed'));
    }

    appState.seismicData = seismicResult.seismic_data;

    // 3. Sonuçları göster
    displaySimulationResults(appState.impactData, appState.seismicData);

    // 4. Haritayı güncelle
    updateMapAndVisualization(appState.impactData, params);
}

// Rumpf metodolojisi simülasyonu
async function runRumpfSimulation(params) {
    const response = await fetch('/api/calculate_advanced_impact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            ...params,
            grid_resolution_km: 10,  // Hızlı hesaplama için
            return_markdown: false
        })
    });

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.error || 'Rumpf simülasyonu başarısız');
    }

    displayRumpfResults(result.results);
}

// Atmosferik giriş simülasyonu
async function runAtmosphericSimulation(params) {
    // Malzeme tipini yoğunluğa göre belirle
    let material_type = 'chondrite';
    if (params.density_kg_m3 > 6000) material_type = 'iron';
    else if (params.density_kg_m3 < 1500) material_type = 'cometary';

    const response = await fetch('/api/simulate_atmospheric_entry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            diameter_m: params.diameter_m,
            velocity_ms: params.velocity_ms,
            entry_angle_deg: params.entry_angle_deg,
            material_type: material_type,
            fragmentation_model: 'pancake'
        })
    });

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.error || 'Atmosferik simülasyon başarısız');
    }

    displayAtmosphericResults(result);
}

// Harita ve görselleştirme güncelleme
function updateMapAndVisualization(impactData, params) {
    // Haritayı güncelle
    setTimeout(() => {
        try {
            if (window.impactMap && impactMap.map) {
                impactMap.updateDamageZones(impactData);
                
                // USGS haritasını da güncelle
                if (typeof updateUSGSMapLocation === 'function') {
                    const location = impactMap.getImpactLocation();
                    updateUSGSMapLocation(location.lat, location.lng);
                }
            } else {
                console.warn('Harita yüklenemedi veya hazır değil');
            }
        } catch (error) {
            console.error('Harita güncelleme hatası:', error);
        }
    }, 500);
    
    // 3D Topografik görselleştirmeyi güncelle (sadece kara çarpması için)
    setTimeout(() => {
        if (!impactData.is_ocean) {
            try {
                update3DCraterTopography(impactData);
            } catch (error) {
                console.error('3D topografi güncelleme hatası:', error);
            }
        } else {
            // Okyanus çarpması - görselleştirmeyi gizle veya mesaj göster
            const topoContainer = document.getElementById('craterTopography');
            if (topoContainer) {
                topoContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #b4b9d6; font-size: 1.2rem; text-align: center; padding: 20px;"><div><p style="font-size: 3rem; margin-bottom: 10px;">🌊</p><p>Ocean Impact</p><p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.7;">No crater formed on land</p></div></div>';
            }
        }
    }, 600);
    
    // Kesit görselleştirmesini güncelle (sadece kara çarpması için)
    setTimeout(() => {
        if (!impactData.is_ocean) {
            try {
                updateCraterCrossSection(impactData);
            } catch (error) {
                console.error('Kesit güncelleme hatası:', error);
            }
        } else {
            // Okyanus çarpması - görselleştirmeyi gizle veya mesaj göster
            const crossContainer = document.getElementById('craterCrossSection');
            if (crossContainer) {
                crossContainer.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #b4b9d6; font-size: 1.2rem; text-align: center; padding: 20px;"><div><p style="font-size: 3rem; margin-bottom: 10px;">🌊</p><p>Ocean Impact</p><p style="font-size: 0.9rem; margin-top: 10px; opacity: 0.7;">No crater cross-section</p></div></div>';
            }
        }
    }, 700);
}

// ============================================================================
// 3D TOPOGRAPHIC CRATER VISUALIZATION
// ============================================================================

function update3DCraterTopography(impactData) {
    const container = document.getElementById('craterTopography');
    if (!container || typeof Plotly === 'undefined') {
        console.warn('Plotly yüklenmedi veya container bulunamadı');
        return;
    }
    
    const craterRadius = (impactData.crater_diameter_km * 1000) / 2; // metre cinsinden yarıçap
    const craterDepth = impactData.crater_depth_m;
    const rimHeight = craterDepth * 0.15; // Kenar yüksekliği ~%15 derinlik
    
    // Grid oluştur
    const gridSize = 100;
    const range = craterRadius * 2.5; // Krater çevresini de göster
    const x = [];
    const y = [];
    const z = [];
    
    for (let i = 0; i < gridSize; i++) {
        const xRow = [];
        const yRow = [];
        const zRow = [];
        
        for (let j = 0; j < gridSize; j++) {
            const xi = -range + (2 * range * i / (gridSize - 1));
            const yj = -range + (2 * range * j / (gridSize - 1));
            
            xRow.push(xi);
            yRow.push(yj);
            
            // Kraterin derinliğini hesapla (parabolik profil)
            const distFromCenter = Math.sqrt(xi * xi + yj * yj);
            let elevation = 0;
            
            if (distFromCenter <= craterRadius) {
                // Krater içi - parabolik çukur
                const normalized = distFromCenter / craterRadius;
                elevation = -craterDepth * (1 - normalized * normalized);
                
                // Krater kenarında yükselti
                if (normalized > 0.85) {
                    const rimFactor = (normalized - 0.85) / 0.15;
                    elevation += rimHeight * Math.sin(rimFactor * Math.PI);
                }
            } else if (distFromCenter <= craterRadius * 1.5) {
                // Ejekta bölgesi - dışa doğru azalan yükselti
                const ejectaFactor = (distFromCenter - craterRadius) / (craterRadius * 0.5);
                elevation = rimHeight * Math.exp(-ejectaFactor * 3) * Math.cos(ejectaFactor * Math.PI);
            }
            
            zRow.push(elevation);
        }
        
        x.push(xRow);
        y.push(yRow);
        z.push(zRow);
    }
    
    const data = [{
        type: 'surface',
        x: x,
        y: y,
        z: z,
        colorscale: [
            [0, '#8B4513'],      // Koyu kahverengi (derin)
            [0.3, '#CD853F'],    // Orta kahverengi
            [0.5, '#DEB887'],    // Açık kahverengi
            [0.7, '#F4A460'],    // Kum rengi
            [0.85, '#D2691E'],   // Kenar (turuncu-kahve)
            [1, '#8B4513']       // Ejekta
        ],
        contours: {
            z: {
                show: true,
                usecolormap: true,
                highlightcolor: "#42f462",
                project: {z: true}
            }
        },
        lighting: {
            ambient: 0.5,
            diffuse: 0.9,
            specular: 0.6,
            roughness: 0.5,
            fresnel: 0.2
        }
    }];
    
    const layout = {
        title: {
            text: appState.currentLanguage === 'en' 
                ? `Crater: ${impactData.crater_diameter_km.toFixed(2)} km diameter, ${(craterDepth / 1000).toFixed(2)} km deep`
                : `Krater: ${impactData.crater_diameter_km.toFixed(2)} km çap, ${(craterDepth / 1000).toFixed(2)} km derinlik`,
            font: { color: '#ffffff', size: 14 }
        },
        scene: {
            xaxis: { 
                title: 'X (meters)',
                gridcolor: '#444',
                color: '#fff'
            },
            yaxis: { 
                title: 'Y (meters)',
                gridcolor: '#444',
                color: '#fff'
            },
            zaxis: { 
                title: 'Elevation (meters)',
                gridcolor: '#444',
                color: '#fff'
            },
            camera: {
                eye: { x: 1.5, y: 1.5, z: 1.2 }
            },
            bgcolor: '#0a0e27'
        },
        paper_bgcolor: '#1a1f3a',
        plot_bgcolor: '#0a0e27',
        margin: { l: 0, r: 0, t: 40, b: 0 },
        autosize: true
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['toImage'],
        displaylogo: false
    };
    
    Plotly.newPlot('craterTopography', data, layout, config);
}

// ============================================================================
// CRATER CROSS-SECTION VISUALIZATION
// ============================================================================

function updateCraterCrossSection(impactData) {
    const container = document.getElementById('craterCrossSection');
    if (!container || typeof Plotly === 'undefined') {
        console.warn('Plotly yüklenmedi veya container bulunamadı');
        return;
    }
    
    const craterRadius = (impactData.crater_diameter_km * 1000) / 2; // metre
    const craterDepth = impactData.crater_depth_m;
    const rimHeight = craterDepth * 0.15;
    const zones = impactData.damage_zones;
    
    // Krater profili noktaları
    const points = 200;
    const maxRange = Math.max(
        zones.light_damage_km * 1000,
        craterRadius * 3
    );
    
    const xProfile = [];
    const yProfile = [];
    
    for (let i = 0; i <= points; i++) {
        const x = -maxRange + (2 * maxRange * i / points);
        const distFromCenter = Math.abs(x);
        let y = 0;
        
        if (distFromCenter <= craterRadius) {
            const normalized = distFromCenter / craterRadius;
            y = -craterDepth * (1 - normalized * normalized);
            
            if (normalized > 0.85) {
                const rimFactor = (normalized - 0.85) / 0.15;
                y += rimHeight * Math.sin(rimFactor * Math.PI);
            }
        } else if (distFromCenter <= craterRadius * 1.5) {
            const ejectaFactor = (distFromCenter - craterRadius) / (craterRadius * 0.5);
            y = rimHeight * Math.exp(-ejectaFactor * 3) * Math.cos(ejectaFactor * Math.PI);
        }
        
        xProfile.push(x / 1000); // km'ye çevir
        yProfile.push(y / 1000);
    }
    
    // Hasar bölgeleri için şekiller
    const shapes = [
        // Tam yıkım (kırmızı)
        {
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: -zones.total_destruction_km,
            x1: zones.total_destruction_km,
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(211, 47, 47, 0.15)',
            line: { width: 0 }
        },
        // Ağır hasar (turuncu)
        {
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: -zones.heavy_damage_km,
            x1: zones.heavy_damage_km,
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(255, 87, 34, 0.1)',
            line: { width: 0 }
        },
        // Orta hasar (sarı)
        {
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: -zones.moderate_damage_km,
            x1: zones.moderate_damage_km,
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(255, 152, 0, 0.08)',
            line: { width: 0 }
        },
        // Hafif hasar (yeşil)
        {
            type: 'rect',
            xref: 'x',
            yref: 'paper',
            x0: -zones.light_damage_km,
            x1: zones.light_damage_km,
            y0: 0,
            y1: 1,
            fillcolor: 'rgba(251, 188, 4, 0.05)',
            line: { width: 0 }
        }
    ];
    
    const data = [
        // Krater profili
        {
            x: xProfile,
            y: yProfile,
            type: 'scatter',
            mode: 'lines',
            name: appState.currentLanguage === 'en' ? 'Crater Profile' : 'Krater Profili',
            line: {
                color: '#8B4513',
                width: 3
            },
            fill: 'tozeroy',
            fillcolor: 'rgba(139, 69, 19, 0.3)'
        },
        // Yüzey seviyesi
        {
            x: [-maxRange / 1000, maxRange / 1000],
            y: [0, 0],
            type: 'scatter',
            mode: 'lines',
            name: appState.currentLanguage === 'en' ? 'Ground Level' : 'Yüzey Seviyesi',
            line: {
                color: '#4CAF50',
                width: 2,
                dash: 'dash'
            }
        }
    ];
    
    const annotations = [
        {
            x: 0,
            y: -craterDepth / 1000,
            text: appState.currentLanguage === 'en' 
                ? `Depth: ${(craterDepth / 1000).toFixed(2)} km`
                : `Derinlik: ${(craterDepth / 1000).toFixed(2)} km`,
            showarrow: true,
            arrowhead: 2,
            ax: 0,
            ay: -40,
            font: { color: '#ffffff', size: 12 },
            bgcolor: 'rgba(0, 0, 0, 0.7)',
            bordercolor: '#d32f2f',
            borderwidth: 2
        },
        {
            x: craterRadius / 1000,
            y: rimHeight / 1000,
            text: appState.currentLanguage === 'en' 
                ? `Rim: ${(rimHeight).toFixed(0)} m`
                : `Kenar: ${(rimHeight).toFixed(0)} m`,
            showarrow: true,
            arrowhead: 2,
            ax: 30,
            ay: -30,
            font: { color: '#ffffff', size: 12 },
            bgcolor: 'rgba(0, 0, 0, 0.7)',
            bordercolor: '#ff9800'
        }
    ];
    
    const layout = {
        title: {
            text: appState.currentLanguage === 'en' 
                ? `Crater Cross-Section with Damage Zones`
                : `Hasar Bölgeleri ile Krater Kesiti`,
            font: { color: '#ffffff', size: 16 }
        },
        xaxis: {
            title: appState.currentLanguage === 'en' ? 'Distance (km)' : 'Mesafe (km)',
            gridcolor: '#444',
            color: '#fff',
            zeroline: true,
            zerolinecolor: '#666'
        },
        yaxis: {
            title: appState.currentLanguage === 'en' ? 'Elevation (km)' : 'Yükseklik (km)',
            gridcolor: '#444',
            color: '#fff',
            zeroline: true,
            zerolinecolor: '#666'
        },
        paper_bgcolor: '#1a1f3a',
        plot_bgcolor: '#0a0e27',
        margin: { l: 60, r: 30, t: 50, b: 60 },
        shapes: shapes,
        annotations: annotations,
        showlegend: true,
        legend: {
            x: 1,
            y: 1,
            bgcolor: 'rgba(26, 31, 58, 0.8)',
            font: { color: '#ffffff' }
        },
        autosize: true
    };
    
    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['toImage'],
        displaylogo: false
    };
    
    Plotly.newPlot('craterCrossSection', data, layout, config);
}

function displaySimulationResults(impactData, seismicData) {
    const resultsDiv = document.getElementById('resultsContent');
    
    // Show asteroid info card
    displayAsteroidInfo();
    
    const atmo = impactData.atmospheric_entry;
    
    // YENİ SONUÇ FORMATI - SADECE TEMEL BİLGİLER + DETAYLAR
    const html = `
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(147, 51, 234, 0.15)); padding: 1rem; border-radius: 8px; margin-bottom: 1.5rem; border-left: 4px solid var(--primary-color);">
            <h3 style="margin: 0 0 0.5rem 0; color: var(--primary-color);">🎯 ${t('basicInfo')}</h3>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('tntEquivalent')}:</div>
            <div class="result-value" style="font-size: 1.3rem; color: var(--danger-color);">
                ${formatNumber(impactData.tnt_equivalent_megatons)} ${t('megaton')}
            </div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('craterDiameter')}:</div>
            <div class="result-value">${impactData.crater_diameter_km.toFixed(2)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('craterDepth')}:</div>
            <div class="result-value">${(impactData.crater_depth_m / 1000).toFixed(2)} km</div>
        </div>
        
        <div class="result-item ${getSeismicClass(seismicData.impact_level)}">
            <div class="result-label">${t('earthquakeMagnitude')}:</div>
            <div class="result-value">${seismicData.magnitude_richter} Richter</div>
        </div>
        
        <div class="result-item">
            <div class="result-label" style="font-size: 0.85rem; color: var(--text-secondary);">
                ${seismicData.description}
            </div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('feltDistance')}:</div>
            <div class="result-value">${formatNumber(seismicData.felt_distance_km)} km</div>
        </div>
        
        <hr style="margin: 1.5rem 0; border-color: var(--border-color);">
        
        <div class="result-item">
            <strong style="font-size: 1.05rem;">${t('damageZones')}:</strong>
        </div>
        
        <div class="result-item">
            <div class="result-label">🔴 ${t('totalDestruction')}:</div>
            <div class="result-value">${impactData.damage_zones.total_destruction_km.toFixed(2)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">🟠 ${t('heavyDamage')}:</div>
            <div class="result-value">${impactData.damage_zones.heavy_damage_km.toFixed(2)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">🟡 ${t('moderateDamage')}:</div>
            <div class="result-value">${impactData.damage_zones.moderate_damage_km.toFixed(2)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">🟢 ${t('lightDamage')}:</div>
            <div class="result-value">${impactData.damage_zones.light_damage_km.toFixed(2)} km</div>
        </div>
        
        <hr style="margin: 1.5rem 0; border-color: var(--border-color);">
        
        <div class="result-item">
            <strong style="font-size: 1.05rem;">👥 ${t('humanImpact')}:</strong>
        </div>
        
        ${impactData.tsunami_data.is_ocean_impact ? `
        <div class="result-item" style="background: rgba(52, 168, 83, 0.1); padding: 0.75rem; border-radius: 6px;">
            <div class="result-label" style="color: var(--text-secondary); font-size: 0.85rem;">
                🌊 ${t('oceanImpact')} - ${impactData.tsunami_data.location_type}
            </div>
        </div>
        ` : `
        <div class="result-item" style="background: rgba(52, 168, 83, 0.1); padding: 0.5rem; border-radius: 6px;">
            <div class="result-label" style="font-size: 0.85rem;">
                🏔️ ${t('landImpact')} - ${impactData.tsunami_data.location_type}
            </div>
        </div>
        `}
        
        <div class="result-item">
            <div class="result-label">${t('affectedPopulation')}:</div>
            <div class="result-value">${formatNumber(impactData.population_impact.total_affected)} ${t('people')}</div>
        </div>
        
        <div class="result-item ${impactData.population_impact.estimated_casualties > 100000 ? 'danger-message' : ''}">
            <div class="result-label">${t('estimatedCasualties')}:</div>
            <div class="result-value" style="font-size: 1.2rem;">${formatNumber(impactData.population_impact.estimated_casualties)} ${t('people')}</div>
        </div>
        
        ${!impactData.tsunami_data.is_ocean_impact ? `
        <div class="result-item">
            <div class="result-label">${t('regionDensity')}:</div>
            <div class="result-value">${impactData.population_impact.population_density} ${t('people')}/km²</div>
        </div>
        
        ${impactData.population_impact.location_info ? `
        <div class="result-item" style="background: rgba(52, 168, 83, 0.1); padding: 0.5rem; border-radius: 4px;">
            <div class="result-label" style="font-size: 0.85rem;">
                📍 ${impactData.population_impact.location_info}
            </div>
        </div>
        ` : ''}
        
        <div class="result-item">
            <div class="result-label" style="font-size: 0.8rem; color: var(--text-secondary);">
                Data: ${impactData.population_impact.data_source || 'Estimated'}
            </div>
        </div>
        ` : ''}
        
        <hr style="margin: 1.5rem 0; border-color: var(--border-color);">
        
        <div class="result-item ${impactData.tsunami_data.tsunami_risk === 'None' ? '' : impactData.tsunami_data.tsunami_risk === 'Extreme' || impactData.tsunami_data.tsunami_risk === 'High' ? 'danger-message' : 'warning-message'}">
            <strong>🌊 ${t('tsunamiRisk')}: ${impactData.tsunami_data.tsunami_risk}</strong>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('impactLocation')}:</div>
            <div class="result-value">${impactData.tsunami_data.location_type}</div>
        </div>
        
        ${impactData.tsunami_data.coordinates ? `
        <div class="result-item">
            <div class="result-label" style="font-size: 0.85rem; color: var(--text-secondary);">
                ${t('coordinates')}: ${impactData.tsunami_data.coordinates}
            </div>
        </div>
        ` : ''}
        
        ${impactData.tsunami_data.is_ocean_impact ? `
        <div class="result-item">
            <div class="result-value">${impactData.tsunami_data.warning}</div>
        </div>
        ` : `
        <div class="result-item">
            <div class="result-value">${t('noTsunamiRisk')}</div>
        </div>
        `}
        
        <hr style="margin: 1.5rem 0; border: 2px solid var(--border-color);">
        
        <!-- DETAYLAR BÖLÜMÜ -->
        <div style="background: linear-gradient(135deg, rgba(251, 188, 4, 0.15), rgba(234, 67, 53, 0.15)); padding: 1rem; border-radius: 8px; margin: 1rem 0; border-left: 4px solid var(--warning-color);">
            <h3 style="margin: 0 0 0.5rem 0; color: var(--warning-color);">📋 ${t('detailedInfo')}</h3>
        </div>
        
        ${atmo ? `
        <h4 style="color: var(--secondary-color); margin: 1rem 0 0.75rem 0;">🌍 ${t('atmosphericEntry')}:</h4>
        
        <div class="result-item">
            <div class="result-label">${t('ablationType')}:</div>
            <div class="result-value">${atmo.ablation_type}</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('initialDiameter')} → ${t('finalDiameter')}:</div>
            <div class="result-value">${atmo.initial_diameter_m.toFixed(1)} m → ${atmo.final_diameter_m.toFixed(1)} m</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('initialVelocity')} → ${t('finalVelocity')}:</div>
            <div class="result-value">${(atmo.initial_velocity_ms / 1000).toFixed(2)} km/s → ${(atmo.final_velocity_ms / 1000).toFixed(2)} km/s</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('initialMass')} → ${t('finalMass')}:</div>
            <div class="result-value">${formatNumber(atmo.initial_mass_kg / 1000)} ${t('ton')} → ${formatNumber(atmo.final_mass_kg / 1000)} ${t('ton')}</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('massLost')}:</div>
            <div class="result-value">${(100 - atmo.mass_retention_percent).toFixed(1)}% (${formatNumber(atmo.mass_lost_kg / 1000)} ${t('ton')})</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('velocityLost')}:</div>
            <div class="result-value">${(atmo.velocity_lost_ms / 1000).toFixed(2)} km/s</div>
        </div>
        
        ${atmo.airburst_altitude_km > 0 ? `
        <div class="result-item warning-message">
            <div class="result-label">💥 ${t('airburstAltitude')}:</div>
            <div class="result-value">${atmo.airburst_altitude_km.toFixed(1)} km</div>
        </div>
        ` : ''}
        
        <div class="result-item" style="background: rgba(251, 188, 4, 0.1); padding: 0.5rem; border-radius: 4px;">
            <div class="result-label" style="font-size: 0.85rem;">
                ⚠️ ${atmo.warning}
            </div>
        </div>
        ` : ''}
        
        <h4 style="color: var(--secondary-color); margin: 1rem 0 0.75rem 0;">📊 ${t('additionalPhysical')}:</h4>
        
        <div class="result-item">
            <div class="result-label">${t('massReachingGround')}:</div>
            <div class="result-value">${formatNumber(impactData.mass_tons)} ${t('ton')}</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">${t('kineticEnergy')}:</div>
            <div class="result-value">${formatScientific(impactData.kinetic_energy_joules)} J</div>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

// ============================================================================
// ASTEROID INFO CARD
// ============================================================================

function displayAsteroidInfo() {
    const asteroidCard = document.getElementById('asteroidInfoCard');
    const asteroidContent = document.getElementById('asteroidInfoContent');
    
    if (!appState.asteroidData) {
        asteroidCard.style.display = 'none';
        return;
    }
    
    const asteroid = appState.asteroidData;
    
    // Asteroid type based on diameter and name
    let asteroidType = 'C-type (Carbonaceous)';
    let composition = {
        'Iron': 5,
        'Nickel': 2,
        'Silicates': 40,
        'Carbon': 30,
        'Water Ice': 15,
        'Other Minerals': 8
    };
    
    // Adjust composition based on asteroid
    if (asteroid.name.includes('Ceres') || asteroid.name.includes('Vesta')) {
        asteroidType = 'Dwarf Planet / Large Asteroid';
        composition = {
            'Silicates': 60,
            'Iron': 15,
            'Water Ice': 20,
            'Other Minerals': 5
        };
    } else if (asteroid.name.includes('Eros') || asteroid.name.includes('Apophis')) {
        asteroidType = 'S-type (Stony)';
        composition = {
            'Silicates': 70,
            'Iron': 15,
            'Nickel': 5,
            'Carbon': 5,
            'Other Minerals': 5
        };
    } else if (asteroid.name.includes('Bennu') || asteroid.name.includes('Ryugu')) {
        asteroidType = 'C-type (Carbonaceous)';
        composition = {
            'Carbon': 35,
            'Silicates': 35,
            'Water Ice': 15,
            'Iron': 8,
            'Organic Compounds': 7
        };
    } else if (asteroid.name.includes('Oumuamua') || asteroid.name.includes('Borisov') || asteroid.name.includes('Halley') || asteroid.name.includes('comet')) {
        asteroidType = 'Comet (Icy Body)';
        composition = {
            'Water Ice': 60,
            'Carbon Dioxide': 15,
            'Silicates': 10,
            'Carbon': 8,
            'Methane': 4,
            'Ammonia': 3
        };
    } else if (asteroid.diameter_m > 100000) {
        asteroidType = 'M-type (Metallic)';
        composition = {
            'Iron': 70,
            'Nickel': 20,
            'Silicates': 8,
            'Other Metals': 2
        };
    }
    
    // Generate HTML - Top row with main info
    let html = `
        <div class="info-item">
            <div class="info-item-label">${t('asteroidName')}:</div>
            <div class="info-item-value" style="font-size: 1.3rem;">${asteroid.name}</div>
        </div>
        
        <div class="info-item">
            <div class="info-item-label">${appState.currentLanguage === 'en' ? 'Type' : 'Tip'}:</div>
            <div class="info-item-value">${asteroidType}</div>
        </div>
        
        <div class="info-item">
            <div class="info-item-label">${appState.currentLanguage === 'en' ? 'Diameter' : 'Çap'}:</div>
            <div class="info-item-value">${asteroid.diameter_m >= 1000 ? (asteroid.diameter_m / 1000).toFixed(1) + ' km' : asteroid.diameter_m + ' m'}</div>
        </div>
        
        <div class="info-item">
            <div class="info-item-label">${appState.currentLanguage === 'en' ? 'Estimated Mass' : 'Tahmini Kütle'}:</div>
            <div class="info-item-value">${formatNumber(calculateMass(asteroid.diameter_m, 3000) / 1e9)} ${appState.currentLanguage === 'en' ? 'billion tons' : 'milyar ton'}</div>
        </div>
        
        <div class="info-item">
            <div class="info-item-label">${appState.currentLanguage === 'en' ? 'Velocity' : 'Hız'}:</div>
            <div class="info-item-value">${(asteroid.velocity_ms / 1000).toFixed(1)} km/s</div>
        </div>
    `;
    
    // Add composition bars
    html += `<div style="grid-column: 1 / -1; margin-top: 1rem;">
        <h4 style="color: var(--secondary-color); margin-bottom: 1rem; font-size: 1.1rem;">
            ${appState.currentLanguage === 'en' ? '🔬 Elemental Composition' : '🔬 Element Bileşimi'}
        </h4>
    </div>`;
    
    for (const [element, percentage] of Object.entries(composition)) {
        html += `
            <div class="info-item">
                <div class="info-item-label">${element}:</div>
                <div class="info-item-value">${percentage}%</div>
                <div class="composition-bar">
                    <div class="composition-fill" style="width: ${percentage}%;"></div>
                </div>
            </div>
        `;
    }
    
    asteroidContent.innerHTML = html;
    asteroidCard.style.display = 'block';
}

function calculateMass(diameter_m, density_kg_m3) {
    const radius = diameter_m / 2;
    const volume = (4/3) * Math.PI * Math.pow(radius, 3);
    return volume * density_kg_m3;
}

// ============================================================================
// Yardımcı Fonksiyonlar
// ============================================================================

function formatNumber(num) {
    if (num >= 1e6) {
        return (num / 1e6).toFixed(2) + ' M';
    } else if (num >= 1e3) {
        return (num / 1e3).toFixed(2) + ' K';
    }
    return num.toFixed(2);
}

function formatScientific(num) {
    return num.toExponential(2);
}

function getSeismicClass(level) {
    const classes = {
        'low': '',
        'moderate': 'warning-message',
        'high': 'danger-message',
        'catastrophic': 'danger-message'
    };
    return classes[level] || '';
}

// Translation dictionary
const translations = {
    en: {
        error: 'Error',
        asteroidLoaded: 'Asteroid loaded',
        asteroidLoadFailed: 'Failed to load asteroid data',
        unknownError: 'Unknown error',
        connectionError: 'Connection error',
        manualInputInfo: 'Use sliders for manual input',
        simulationCompleted: 'Simulation completed!',
        simulationError: 'Simulation error',
        impactCalculationFailed: 'Impact calculation failed',
        seismicCalculationFailed: 'Seismic calculation failed',
        // Results translations
        basicInfo: 'Basic Information',
        tntEquivalent: 'TNT Equivalent',
        megaton: 'Megaton',
        craterDiameter: 'Crater Diameter',
        craterDepth: 'Crater Depth',
        earthquakeMagnitude: 'Earthquake Magnitude',
        feltDistance: 'Felt Distance',
        damageZones: 'Damage Zones',
        totalDestruction: 'Total Destruction',
        heavyDamage: 'Heavy Damage',
        moderateDamage: 'Moderate Damage',
        lightDamage: 'Light Damage',
        humanImpact: 'Human Impact',
        oceanImpact: 'Ocean impact',
        landImpact: 'Land impact',
        affectedPopulation: 'Affected Population',
        estimatedCasualties: 'Estimated Casualties',
        people: 'people',
        regionDensity: 'Region Density',
        tsunamiRisk: 'Tsunami Risk',
        impactLocation: 'Impact Location',
        coordinates: 'Coordinates',
        detailedInfo: 'Detailed Information',
        atmosphericEntry: 'Atmospheric Entry',
        ablationType: 'Ablation Type',
        initialDiameter: 'Initial Diameter',
        finalDiameter: 'Final Diameter',
        initialVelocity: 'Initial Velocity',
        finalVelocity: 'Final Velocity',
        initialMass: 'Initial Mass',
        finalMass: 'Final Mass',
        massLost: 'Mass Lost in Atmosphere',
        velocityLost: 'Velocity Lost',
        airburstAltitude: 'Airburst Altitude',
        additionalPhysical: 'Additional Physical Parameters',
        massReachingGround: 'Mass Reaching Ground',
        kineticEnergy: 'Kinetic Energy',
        ton: 'ton',
        noTsunamiRisk: 'No tsunami risk (land impact).',
        asteroidName: 'Asteroid Name'
    },
    tr: {
        error: 'Hata',
        asteroidLoaded: 'Asteroid yüklendi',
        asteroidLoadFailed: 'Asteroid verisi yüklenemedi',
        unknownError: 'Bilinmeyen hata',
        connectionError: 'Bağlantı hatası',
        manualInputInfo: 'Manuel giriş için slider\'ları kullanın',
        simulationCompleted: 'Simülasyon tamamlandı!',
        simulationError: 'Simülasyon hatası',
        impactCalculationFailed: 'Çarpma hesaplaması başarısız',
        seismicCalculationFailed: 'Sismik hesaplama başarısız',
        // Results translations
        basicInfo: 'Temel Bilgiler',
        tntEquivalent: 'TNT Eşdeğeri',
        megaton: 'Megaton',
        craterDiameter: 'Krater Çapı',
        craterDepth: 'Krater Derinliği',
        earthquakeMagnitude: 'Deprem Büyüklüğü',
        feltDistance: 'Hissedilme Mesafesi',
        damageZones: 'Hasar Bölgeleri',
        totalDestruction: 'Tam Yıkım',
        heavyDamage: 'Ağır Hasar',
        moderateDamage: 'Orta Hasar',
        lightDamage: 'Hafif Hasar',
        humanImpact: 'İnsan Etkisi',
        oceanImpact: 'Okyanus çarpması',
        landImpact: 'Kara çarpması',
        affectedPopulation: 'Etkilenen Nüfus',
        estimatedCasualties: 'Tahmini Kayıplar',
        people: 'kişi',
        regionDensity: 'Bölge Yoğunluğu',
        tsunamiRisk: 'Tsunami Riski',
        impactLocation: 'Çarpma Yeri',
        coordinates: 'Koordinatlar',
        detailedInfo: 'Detaylı Bilgiler',
        atmosphericEntry: 'Atmosfere Giriş',
        ablationType: 'Ablasyon Tipi',
        initialDiameter: 'Başlangıç Çapı',
        finalDiameter: 'Son Çap',
        initialVelocity: 'Başlangıç Hızı',
        finalVelocity: 'Son Hız',
        initialMass: 'Başlangıç Kütlesi',
        finalMass: 'Son Kütle',
        massLost: 'Atmosferde Kaybedilen Kütle',
        velocityLost: 'Hız Kaybı',
        airburstAltitude: 'Hava Patlaması Yüksekliği',
        additionalPhysical: 'Ek Fiziksel Parametreler',
        massReachingGround: 'Yere Ulaşan Kütle',
        kineticEnergy: 'Kinetik Enerji',
        ton: 'ton',
        noTsunamiRisk: 'Tsunami riski yok (kara çarpması).',
        asteroidName: 'Asteroid Adı'
    }
};

function t(key) {
    return translations[appState.currentLanguage][key] || key;
}

// Bildirim fonksiyonları
function showSuccess(message) {
    console.log('✅ ' + message);
    // İsteğe bağlı: Toast bildirimi eklenebilir
}

function showError(message) {
    console.error('❌ ' + message);
    alert(t('error') + ': ' + message);
}

function showWarning(message) {
    console.warn('⚠️ ' + message);
}

function showInfo(message) {
    console.info('ℹ️ ' + message);
}

// ============================================================================
// RUMPF METODOLOJISI SONUÇLARINI GÖSTERME
// ============================================================================

function displayRumpfResults(results) {
    const resultsDiv = document.getElementById('resultsContent');
    
    const html = `
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(147, 51, 234, 0.1)); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0;">🔬 Rumpf Metodolojisi - Gelişmiş Risk Analizi</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                7 tehlike türü, grid-bazlı nüfus haritalaması
            </p>
        </div>
        
        <div class="result-item" style="background: rgba(234, 67, 53, 0.15); border-left: 4px solid #ea4335;">
            <strong>📍 Çarpma Tipi: ${results.impact_type}</strong>
        </div>
        
        <div class="result-item">
            <div class="result-label">Kinetik Enerji:</div>
            <div class="result-value">${results.kinetic_energy_mt.toFixed(2)} Megaton TNT</div>
        </div>
        
        <div class="result-item danger-message">
            <div class="result-label">⚠️ TOPLAM BEKLENEN KAYIPLAR:</div>
            <div class="result-value" style="font-size: 1.3rem; font-weight: 700;">
                ${formatNumber(results.total_casualties)} kişi
            </div>
        </div>
        
        <hr style="margin: 1rem 0;">
        
        <h4>📊 Tehlikeye Göre Kayıp Dağılımı</h4>
        
        ${generateHazardItem('Aşırı Basınç', results.casualties_by_hazard.overpressure, '#ea4335')}
        ${generateHazardItem('Rüzgar Patlaması', results.casualties_by_hazard.wind_blast, '#fbbc04')}
        ${generateHazardItem('Termal Radyasyon', results.casualties_by_hazard.thermal_radiation, '#ff6d00')}
        ${generateHazardItem('Sismik Sarsıntı', results.casualties_by_hazard.seismic, '#9c27b0')}
        ${generateHazardItem('Ejekta Püskürtüsü', results.casualties_by_hazard.ejecta, '#795548')}
        ${generateHazardItem('Kraterleşme', results.casualties_by_hazard.cratering, '#000000')}
        ${generateHazardItem('Tsunami', results.casualties_by_hazard.tsunami, '#1e88e5')}
        
        <hr style="margin: 1rem 0;">
        
        <h4>📋 Detaylı Parametreler</h4>
        
        <div class="result-item">
            <div class="result-label">Krater Çapı:</div>
            <div class="result-value">${(results.parameters.crater_diameter_m / 1000).toFixed(2)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Havada İnfilak İrtifası:</div>
            <div class="result-value">${results.parameters.airburst_altitude_km.toFixed(1)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Sismik Büyüklük:</div>
            <div class="result-value">${results.parameters.seismic_magnitude} Richter</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Grid Hücreleri Analiz Edildi:</div>
            <div class="result-value">${results.parameters.grid_cells_analyzed}</div>
        </div>
        
        <div style="background: rgba(52, 168, 83, 0.1); padding: 0.75rem; border-radius: 6px; margin-top: 1rem;">
            <small style="color: var(--text-secondary);">
                ✅ Korunaklı/Korunmasız nüfus modelleri kullanıldı<br>
                ✅ Enhanced Fujita (EF) ölçeği uygulandı<br>
                ✅ Ejekta yükü yapısal analizi yapıldı
            </small>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

function generateHazardItem(name, casualties, color) {
    if (casualties <= 0) return '';
    
    return `
        <div class="result-item" style="border-left: 3px solid ${color}; padding-left: 0.75rem;">
            <div class="result-label">${name}:</div>
            <div class="result-value">${formatNumber(casualties)} kişi</div>
        </div>
    `;
}

// ============================================================================
// ATMOSFERİK GİRİŞ SONUÇLARINI GÖSTERME
// ============================================================================

function displayAtmosphericResults(results) {
    const resultsDiv = document.getElementById('resultsContent');
    
    const html = `
        <div style="background: linear-gradient(135deg, rgba(255, 109, 0, 0.1), rgba(251, 188, 4, 0.1)); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <h4 style="margin: 0 0 0.5rem 0;">🌠 Atmosferik Giriş Simülasyonu</h4>
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin: 0;">
                Fizik tabanlı: Yavaşlama + Ablasyon + Işıma
            </p>
        </div>
        
        <div class="result-item" style="background: rgba(59, 130, 246, 0.15); border-left: 4px solid #3b82f6;">
            <strong>🪨 Malzeme: ${results.initial_conditions.material}</strong>
        </div>
        
        <h4>📥 Başlangıç Koşulları</h4>
        
        <div class="result-item">
            <div class="result-label">Çap:</div>
            <div class="result-value">${results.initial_conditions.diameter_m} m</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Kütle:</div>
            <div class="result-value">${formatNumber(results.initial_conditions.initial_mass_kg / 1000)} ton</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Giriş Hızı:</div>
            <div class="result-value">${(results.initial_conditions.velocity_ms / 1000).toFixed(1)} km/s</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Giriş Açısı:</div>
            <div class="result-value">${results.initial_conditions.entry_angle_deg}°</div>
        </div>
        
        <hr style="margin: 1rem 0;">
        
        <h4>💥 Anahtar Sonuçlar</h4>
        
        <div class="result-item warning-message">
            <div class="result-label">🎆 Hava Patlaması İrtifası:</div>
            <div class="result-value" style="font-size: 1.2rem;">${results.key_results.airburst_altitude_km.toFixed(1)} km</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">⚡ Toplam Enerji:</div>
            <div class="result-value">${results.key_results.tnt_equivalent_kilotons.toFixed(1)} kiloton TNT</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">💫 Maksimum Parlaklık:</div>
            <div class="result-value">${formatScientific(results.key_results.peak_luminosity_watts)} Watt</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">💨 Maks. Dinamik Basınç:</div>
            <div class="result-value">${results.key_results.max_dynamic_pressure_mpa.toFixed(2)} MPa</div>
        </div>
        
        <div class="result-item ${results.key_results.fragmented ? 'danger-message' : ''}">
            <div class="result-label">🧩 Parçalandı mı?:</div>
            <div class="result-value">${results.key_results.fragmented ? 'EVET (' + results.key_results.fragmentation_model + ')' : 'Hayır'}</div>
        </div>
        
        <hr style="margin: 1rem 0;">
        
        <h4>🎯 Son Durum</h4>
        
        <div class="result-item">
            <div class="result-label">Son Yükseklik:</div>
            <div class="result-value">${results.final_state.altitude_km.toFixed(1)} km ${results.final_state.altitude_km <= 0 ? '(Yere ulaştı!)' : ''}</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Son Hız:</div>
            <div class="result-value">${(results.final_state.velocity_ms / 1000).toFixed(1)} km/s</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Kalan Kütle:</div>
            <div class="result-value">${formatNumber(results.final_state.mass_kg / 1000)} ton</div>
        </div>
        
        <hr style="margin: 1rem 0;">
        
        <h4>🔬 Malzeme Özellikleri</h4>
        
        <div class="result-item">
            <div class="result-label">Yoğunluk:</div>
            <div class="result-value">${results.material_properties.density} kg/m³</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Mukavemet:</div>
            <div class="result-value">${results.material_properties.tensile_strength_mpa.toFixed(3)} MPa</div>
        </div>
        
        <div class="result-item">
            <div class="result-label">Ablasyon Isısı:</div>
            <div class="result-value">${results.material_properties.ablation_heat_mj_kg} MJ/kg</div>
        </div>
        
        <div style="background: rgba(251, 188, 4, 0.1); padding: 0.75rem; border-radius: 6px; margin-top: 1rem;">
            <small style="color: var(--text-secondary);">
                📈 Zaman serisi verileri mevcut: Yükseklik, Hız, Kütle, Işıma<br>
                🔬 Üç temel fizik denklemi entegre edildi<br>
                ✅ Parçalanma dinamikleri modellendi
            </small>
        </div>
    `;
    
    resultsDiv.innerHTML = html;
}

