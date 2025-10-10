# 🌍 Asteroid Impact Visualizer

**NASA Space Apps Challenge 2025 - Impactor-2025 Challenge**

end2end.earth

Asteroid çarpma simülasyonu ve görselleştirme aracı. Kullanıcılar asteroid parametrelerini ayarlayabilir, gerçek NASA verileriyle çarpma etkilerini analiz edebilir ve gelişmiş fizik modelleriyle risk değerlendirmesi yapabilir.

---

## 🎯 Proje Özellikleri

### ✨ Ana Özellikler
- **Veri Kaynağı Seçimi**: 🌐 Canlı NASA API verileri veya 💾 Önyüklenmiş veritabanı
- **NASA NEO API Entegrasyonu**: Gerçek asteroid verileri
- **30+ Asteroid Veritabanı**: Güneş sistemi asteroitleri, kuyruklu yıldızlar ve tarihi çarpmalar
- **NASA Eyes Solar System**: İnteraktif 3D güneş sistemi görselleştirmesi
- **2D Çarpma Haritası**: Leaflet.js ile gerçek dünya haritası üzerinde etki gösterimi
- **3D Krater Görselleştirmesi**: Plotly.js ile topografik krater modeli ve kesit görünümü
- **USGS Haritaları**: Topografik ve uydu görüntülü harita katmanları
- **Fizik Hesaplamaları**: 
  - Kinetik enerji hesaplama
  - Krater boyutu tahmini
  - Sismik etki analizi
  - Atmosferik giriş ve ablasyon
- **🆕 Rumpf Metodolojisi**: Gelişmiş risk değerlendirmesi (7 tehlike türü)
  - Aşırı Basınç, Rüzgar, Termal Radyasyon, Sismik, Ejekta, Kraterleşme, Tsunami
  - Grid-bazlı nüfus haritalaması
  - Korunaklı/Korunmasız nüfus hassasiyet modelleri
- **🔥 Atmosferik Giriş Simülasyonu**: Fizik tabanlı, yüksek sadakat modeli
  - Üç temel denklem: Yavaşlama, Ablasyon, Işıma
  - 3 Malzeme tipi: Taşlı, Demir, Kometsi
  - 2 Parçalanma modeli: Pancake ve Discrete
  - Çelyabinsk 2013 doğrulaması
- **📐 Formüller ve Teknik Bilgiler Sayfası**: Tüm hesaplamaların detaylı açıklamaları
- **🌊 Tsunami Risk Analizi**: Okyanus çarpmalarında tsunami yüksekliği ve menzil tahmini
- **👥 Gelişmiş Nüfus Etkisi**: GeoNames API ile gerçek nüfus yoğunluğu verileri

### 🛠️ Teknoloji Yığını
- **Backend**: Python 3.8+, Flask
- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Görselleştirme**: Three.js, Leaflet.js
- **API**: NASA NeoWs API

---

## 📁 Proje Yapısı

```
nasa/
│
├── app.py                          # Flask backend uygulaması (2,541 satır - optimize edildi!)
├── requirements.txt                # Python bağımlılıkları
├── README.md                       # Bu dosya
│
├── data/                          # 🆕 Veri modülleri (ayrı dosyalar)
│   ├── __init__.py               # Modül tanımlayıcı
│   ├── asteroid_data.py          # 30+ asteroid ve kuyruklu yıldız verisi
│   └── city_data.py              # 55+ büyük şehir nüfus veritabanı
│
├── templates/
│   ├── index.html                  # Ana HTML sayfası
│   └── formulas.html              # 🆕 Formüller ve Teknik Bilgiler sayfası
│
└── static/
    ├── css/
    │   └── style.css              # Stil dosyası
    │
    └── js/
        ├── app.js                  # Ana JavaScript mantığı (veri kaynağı seçimi ile)
        ├── orbit3d.js             # Three.js 3D yörünge simülasyonu
        └── impactMap.js           # Leaflet.js harita görselleştirmesi
```

---

## 🚀 Kurulum ve Çalıştırma

### 1️⃣ Proje Klasörüne Gidin
```bash
cd nasa
```

### 2️⃣ Python Sanal Ortamı Oluşturun ve Aktif Edin

**Windows için:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux için:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Gerekli Python Kütüphanelerini Yükleyin
```bash
pip install -r requirements.txt
```

### 4️⃣ API Keys Alın (Opsiyonel ama Önerilen)

#### NASA API Key
- [NASA API Portal](https://api.nasa.gov/) adresinden ücretsiz API key alın

#### GeoNames Username (Gerçek Popülasyon Verileri İçin)
- [GeoNames Kayıt](http://www.geonames.org/login) sayfasından ücretsiz hesap oluşturun
- Hesabınızı aktifleştirin
- Username'inizi not alın

**Ortam değişkenleri olarak ekleyin:**

**Windows (PowerShell):**
```bash
$env:NASA_API_KEY="YOUR_NASA_API_KEY"
$env:GEONAMES_USERNAME="YOUR_GEONAMES_USERNAME"
```

**Mac/Linux:**
```bash
export NASA_API_KEY="YOUR_NASA_API_KEY"
export GEONAMES_USERNAME="YOUR_GEONAMES_USERNAME"
```

> **Not**: API key'ler olmadan da çalışır ama:
> - NASA API: `DEMO_KEY` kullanılır (oran sınırlaması var)
> - GeoNames: `demo` kullanılır (çok sınırlı, kendi hesabınızı oluşturun!)

### 5️⃣ Flask Uygulamasını Başlatın
```bash
python app.py
```

### 6️⃣ Tarayıcıda Açın
```
http://localhost:5000
```

---

## 📘 Kullanım Kılavuzu

### 🔬 Simülasyon Modu

1. **Veri Kaynağı Seçin**:
   - **🌐 Canlı Veriler (API)**: NASA NEO API'sinden gerçek zamanlı asteroid verileri
   - **💾 Veritabanı**: 30+ önyüklenmiş asteroid, kuyruklu yıldız ve tarihi çarpma verileri

2. **Asteroid Kaynağı Seçin**:
   - **🎯 Manuel Giriş**: Kendi parametrelerinizi ayarlayın
   - **🌞 Güneş Sistemi Asteroitleri**: Apophis, Bennu, Eros, Ceres vb.
   - **☄️ Kuyruklu Yıldızlar**: Halley, Hale-Bopp, Oumuamua vb.
   - **🦖 Chicxulub**: Dinozorları yok eden dev asteroid

3. **Parametreleri Ayarlayın**:
   - **Çap**: Asteroidin çapı (10-1000 metre, büyük asteroidler için otomatik genişler)
   - **Hız**: Çarpma hızı (10,000-100,000 km/h)
   - **Açı**: Çarpma açısı (15-90 derece)

4. **Çarpma Konumu Seçin**:
   - Harita üzerinde çarpma noktasını tıklayın veya kırmızı işaretçiyi sürükleyin
   - Konum otomatik olarak okyanus/kara tespiti yapılır

5. **"Simülasyonu Başlat" Düğmesine Tıklayın**

6. **Sonuçları İnceleyin**:
   - **Atmosferik Giriş**: Kütle ve hız kaybı, ablasyon türü
   - **Kinetik Enerji**: TNT eşdeğeri (Megaton)
   - **Krater Boyutu**: Çap ve derinlik (3D görselleştirme)
   - **Deprem Etkisi**: Richter büyüklüğü ve hissedilme mesafesi
   - **Hasar Bölgeleri**: 4 seviye hasar yarıçapları (harita üzerinde)
   - **Tsunami Riski**: Okyanus çarpmalarında tsunami yüksekliği ve menzili
   - **Nüfus Etkisi**: Etkilenen ve tahmini kayıp sayısı

---

## 🎓 Teknik Detaylar

### Backend API Endpoints

#### 1. `/api/get_asteroid_data`
**Method**: GET  
**Parametreler**:
- `asteroid_id` (opsiyonel): Belirli asteroid ID'si
- `random` (opsiyonel): `true` ise rastgele tehlikeli asteroid

**NASA NeoWs API'den Çekilen Veriler:**
- 🆔 **Asteroid ID & Name**: Benzersiz tanımlayıcı ve isim
- 📏 **Estimated Diameter**: Minimum ve maksimum çap (metre) - ortalama hesaplanır
- ⚡ **Relative Velocity**: Dünya'ya göre hız (km/h ve m/s)
- ⚠️ **Is Potentially Hazardous**: Tehlikeli asteroid mi?
- 🔆 **Absolute Magnitude**: Parlaklık (H değeri)
- 🔄 **Orbital Period**: Yörünge süresi (gün)
- 📍 **Miss Distance**: Dünya'dan en yakın geçiş mesafesi (km)
- 📅 **Close Approach Data**: Yakın geçiş tarihi ve detayları

**Dönen Veri**:
```json
{
  "success": true,
  "asteroid": {
    "id": "3542519",
    "name": "(2011 DV)",
    "diameter_m": 300.5,
    "velocity_ms": 6100,
    "velocity_kmh": 22000,
    "is_hazardous": true,
    "absolute_magnitude": 21.3,
    "orbital_period": 365.2,
    "miss_distance_km": 7500000
  }
}
```

#### 2. `/api/calculate_impact`
**Method**: POST  
**Body**:
```json
{
  "diameter_m": 150,
  "velocity_ms": 18000,
  "angle_deg": 45,
  "density": 3000
}
```

**Dönen Veri**:
```json
{
  "success": true,
  "impact_data": {
    "kinetic_energy_joules": ...,
    "tnt_equivalent_megatons": ...,
    "crater_diameter_km": ...,
    "damage_zones": {
      "total_destruction_km": ...,
      "heavy_damage_km": ...,
      "moderate_damage_km": ...,
      "light_damage_km": ...
    }
  }
}
```

#### 3. `/api/calculate_seismic_effect`
**Method**: POST  
**Body**:
```json
{
  "kinetic_energy_joules": 1e15
}
```

**Dönen Veri**:
```json
{
  "success": true,
  "seismic_data": {
    "magnitude_richter": 7.5,
    "magnitude_moment": 7.2,
    "description": "Yıkıcı deprem",
    "impact_level": "catastrophic"
  }
}
```

#### 4. 🆕 `/api/calculate_advanced_impact` (Rumpf Metodolojisi)
**Method**: POST  
**Açıklama**: Gelişmiş asteroid çarpma risk değerlendirmesi - 7 tehlike türü analizi

**Body**:
```json
{
  "diameter_m": 150,
  "density_kg_m3": 3100,
  "velocity_ms": 18000,
  "angle_deg": 45,
  "impact_lat": 41.0082,
  "impact_lng": 28.9784,
  "unsheltered_fraction": 0.13,
  "grid_resolution_km": 5,
  "return_markdown": true
}
```

**Dönen Veri**:
```json
{
  "success": true,
  "results": {
    "impact_type": "Surface Impact",
    "kinetic_energy_mt": 48.5,
    "total_casualties": 125000,
    "casualties_by_hazard": {
      "overpressure": 45000,
      "wind_blast": 38000,
      "thermal_radiation": 22000,
      "seismic": 8000,
      "ejecta": 12000,
      "cratering": 5000,
      "tsunami": 0
    },
    "parameters": {...}
  },
  "markdown": "# Asteroid Çarpma Risk Değerlendirmesi\n\n..."
}
```

**Detaylı Kullanım**: Bkz. `RUMPF_METHODOLOGY_GUIDE.md`

#### 5. 🔥 `/api/simulate_atmospheric_entry` (Gelişmiş Atmosferik Giriş)
**Method**: POST  
**Açıklama**: Fizik tabanlı atmosferik giriş simülasyonu - Ablasyon, parçalanma ve ışıma

**Body**:
```json
{
  "diameter_m": 20,
  "velocity_ms": 19000,
  "entry_angle_deg": 18,
  "material_type": "chondrite",
  "initial_altitude_m": 100000,
  "fragmentation_model": "pancake",
  "time_step": 0.01
}
```

**Dönen Veri**:
```json
{
  "success": true,
  "key_results": {
    "airburst_altitude_km": 11.0,
    "peak_luminosity_watts": 1.2e10,
    "tnt_equivalent_kilotons": 418,
    "fragmented": true,
    "fragmentation_model": "pancake"
  },
  "time_series": {
    "altitude": [...],
    "velocity": [...],
    "mass": [...],
    "luminosity": [...]
  }
}
```

#### 6. 🧪 `/api/simulate_chelyabinsk` (Çelyabinsk Doğrulama)
**Method**: GET  
**Açıklama**: 2013 Çelyabinsk süperbolidini simüle eder ve gözlemsel verilerle karşılaştırır

**Detaylı Kullanım**: Bkz. `ATMOSPHERIC_ENTRY_GUIDE.md`

---

## 📐 Fizik Formülleri

### Kinetik Enerji
```
E = ½ × m × v²
```
- `m`: Asteroid kütlesi (kg)
- `v`: Çarpma hızı (m/s)

### Krater Çapı (Collins et al. 2005 - Basitleştirilmiş)
```
D_crater ≈ 1.8 × D_asteroid × (v/12000)^0.44 × sin(θ)^0.33 × 13
```
- `D_asteroid`: Asteroid çapı (m)
- `v`: Hız (m/s)
- `θ`: Çarpma açısı (radyan)

### Richter Ölçeği
```
M = (log₁₀(E) - 4.8) / 1.5
```
- `E`: Enerji (Joule)

### Tsunami Yüksekliği (Basitleştirilmiş)
```
H₀ ≈ (E^0.25) × 3 × crater_factor
H(r) = H₀ / √r
```
- `H₀`: Başlangıç tsunami yüksekliği (m)
- `r`: Kıyıya mesafe (km)
- `crater_factor`: Krater boyutu faktörü

---

## 🔧 Geliştirme Notları

### Bağımlılıklar
- **Flask 3.0.0**: Web framework
- **Flask-CORS 4.0.0**: Cross-origin resource sharing
- **requests 2.31.0**: HTTP istekleri için
- **numpy 1.24.3**: Bilimsel hesaplamalar

### Tarayıcı Uyumluluğu
- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

### Performans
- 3D görselleştirme: WebGL gerektirir
- Harita: İnternet bağlantısı (tile'lar için)

---

## 🐛 Sorun Giderme

### NASA API Hata Veriyor
- API key'inizin geçerli olduğundan emin olun
- Oran sınırlamalarına dikkat edin (DEMO_KEY: saatte 30 istek)
- İnternet bağlantınızı kontrol edin

### 3D Görselleştirme Çalışmıyor
- WebGL destekleyen bir tarayıcı kullanın
- GPU sürücülerinizi güncelleyin
- Tarayıcı konsolunda hata mesajlarını kontrol edin

### Harita Görünmüyor
- İnternet bağlantınızı kontrol edin
- Leaflet.js'in yüklendiğinden emin olun (tarayıcı konsolu)

---

## 📚 Referanslar

### API ve Kütüphaneler
- [NASA NeoWs API](https://api.nasa.gov/)
- [NASA DART Mission](https://www.nasa.gov/planetarydefense/dart)
- [Three.js Documentation](https://threejs.org/docs/)
- [Leaflet.js Documentation](https://leafletjs.com/)
- [GeoNames API](http://www.geonames.org/)

### Bilimsel Yayınlar (Rumpf Metodolojisi)
- **Rumpf, C. M.** (2016). *Asteroid Impact Risk*. PhD Thesis, University of Southampton.
- **Rumpf, C. M., Lewis, H. G., & Atkinson, P. M.** (2017). *Population Vulnerability Models for Asteroid Impact Risk Assessment*. Meteoritics & Planetary Science, 52(6), 1082-1102.
- **Collins, G. S., Melosh, H. J., & Marcus, R. A.** (2005). *Earth Impact Effects Program: A Web-based computer program for calculating the regional environmental consequences of a meteoroid impact on Earth*. Meteoritics & Planetary Science, 40(6), 817-840.
- **Ward, S. N., & Asphaug, E.** (2000). *Asteroid impact tsunami: A probabilistic hazard assessment*. Icarus, 145(1), 64-78.

---

## 👥 Geliştirici

NASA Space Apps Challenge 2025 için geliştirildi.

### Lisans
Bu proje eğitim amaçlıdır ve NASA Space Apps Challenge kurallarına tabidir.

---

## 🌟 Yeni Özellikler (v2.0)

- [x] ✅ **Veri Kaynağı Seçimi**: Kullanıcılar canlı NASA API verileri veya önyüklenmiş veritabanı arasında seçim yapabilir
- [x] ✅ **30+ Asteroid Veritabanı**: Apophis, Bennu, Chicxulub ve daha fazlası
- [x] ✅ **Formüller Sayfası**: Tüm bilimsel hesaplamaların detaylı açıklamaları
- [x] ✅ **İki Dilli Destek**: İngilizce ve Türkçe
- [x] ✅ **Temiz Dosya Yapısı**: Gereksiz dokümantasyon dosyaları kaldırıldı
- [x] ✅ Popülasyon yoğunluğu analizi (Rumpf Metodolojisi ile eklendi)
- [x] ✅ Gelişmiş tehlike modelleri (7 farklı tehlike türü)
- [x] ✅ Grid-bazlı hassasiyet haritalaması

## 🚀 Gelecek Geliştirmeler

- [ ] Gerçek zamanlı asteroid takibi ve erken uyarı sistemi
- [ ] İklim etkileri simülasyonu (ejekta, küresel soğuma)
- [ ] Zaman içinde hasar yayılımı animasyonu
- [ ] Karşılaştırmalı simülasyon modu (birden fazla senaryo)
- [ ] PDF rapor oluşturma ve paylaşma
- [ ] Mobil uygulama desteği

---

**Asteroid çarpmalarını anlamak, geleceği korumak için ilk adımdır! 🌍🚀**

