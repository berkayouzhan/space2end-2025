/* ============================================================================
   ADIM 3.3: LEAFLET.JS İLE 2D ÇARPMA HARİTASI VE ETKİ ALANI
   ============================================================================ */

class ImpactMapVisualizer {
    constructor(containerId) {
        this.containerId = containerId;
        this.map = null;
        this.impactMarker = null;
        this.damageCircles = [];
        this.impactLocation = { lat: 28.5729, lng: -80.6490 }; // Varsayılan: NASA Kennedy Space Center, Florida
        
        this.init();
    }

    init() {
        // Element kontrolü
        const container = document.getElementById(this.containerId);
        if (!container) {
            console.error(`Harita container bulunamadı: ${this.containerId}`);
            return;
        }
        
        // Leaflet haritasını oluştur
        try {
            this.map = L.map(this.containerId, {
                center: [this.impactLocation.lat, this.impactLocation.lng],
                zoom: 8,
                zoomControl: true,
                scrollWheelZoom: true,
                doubleClickZoom: true,
                touchZoom: true,
                dragging: true
            });
        } catch (error) {
            console.error('Harita oluşturma hatası:', error);
            return;
        }

        // OpenStreetMap tile layer (İngilizce etiketlerle)
        // CartoDB Positron - Temiz, İngilizce etiketli, modern görünüm
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
            subdomains: 'abcd',
            maxZoom: 20
        }).addTo(this.map);

        // Alternatif: Karanlık tema için CartoDB Dark Matter
        // L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        //     attribution: '&copy; OpenStreetMap, &copy; CartoDB',
        //     maxZoom: 19
        // }).addTo(this.map);

        // Harita üzerine tıklama event'i
        this.map.on('click', (e) => {
            console.log('MAP CLICKED:', e.latlng);
            this.setImpactLocation(e.latlng.lat, e.latlng.lng);
        });
        
        // Harita yüklendiğinde
        this.map.on('load', () => {
            console.log('MAP tiles loaded');
        });

        // Başlangıç işaretçisini ekle
        this.updateImpactMarker();
        
        // Harita boyutunu düzelt (gecikme ile)
        setTimeout(() => {
            if (this.map) {
                this.map.invalidateSize();
                console.log('✅ Harita başlatıldı ve boyutlandı');
            }
        }, 250);
    }

    setImpactLocation(lat, lng) {
        this.impactLocation = { lat, lng };
        this.updateImpactMarker();
        
        // Kullanıcıya bilgi ver
        console.log(`TARGET UPDATED: ${lat.toFixed(4)}, ${lng.toFixed(4)}`);
        
        // Görsel feedback
        if (this.impactMarker) {
            this.impactMarker.openPopup();
        }
    }

    updateImpactMarker() {
        // Önceki işaretçiyi kaldır
        if (this.impactMarker) {
            this.map.removeLayer(this.impactMarker);
        }

        // Asteroid şeklinde SVG icon
        const svgIcon = `
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="56" height="56">
                <defs>
                    <radialGradient id="asteroidGrad" cx="40%" cy="40%" r="60%">
                        <stop offset="0%" style="stop-color:#8B7355;stop-opacity:1" />
                        <stop offset="50%" style="stop-color:#6B5344;stop-opacity:1" />
                        <stop offset="100%" style="stop-color:#4A3829;stop-opacity:1" />
                    </radialGradient>
                    <filter id="shadow">
                        <feDropShadow dx="2" dy="2" stdDeviation="3" flood-opacity="0.5"/>
                    </filter>
                </defs>
                
                <!-- Ana asteroid gövdesi (düzensiz şekil) -->
                <path d="M 32,8 L 42,12 L 50,18 L 54,28 L 52,38 L 46,48 L 36,54 L 24,52 L 14,46 L 10,36 L 12,24 L 18,14 L 28,10 Z" 
                      fill="url(#asteroidGrad)" 
                      stroke="#2A1F1A" 
                      stroke-width="2"
                      filter="url(#shadow)"/>
                
                <!-- Kraterler (detay) -->
                <circle cx="25" cy="20" r="4" fill="#5A4335" opacity="0.8"/>
                <circle cx="40" cy="25" r="3" fill="#5A4335" opacity="0.7"/>
                <circle cx="30" cy="35" r="5" fill="#5A4335" opacity="0.8"/>
                <circle cx="42" cy="40" r="3.5" fill="#5A4335" opacity="0.7"/>
                
                <!-- Işık yansıması -->
                <ellipse cx="28" cy="18" rx="6" ry="4" fill="#A89080" opacity="0.4"/>
                
                <!-- Ateş izi (kuyruk efekti) -->
                <path d="M 32,54 Q 30,58 28,62 Q 32,60 32,64 Q 34,60 36,62 Q 34,58 32,54" 
                      fill="#FF6B35" opacity="0.8"/>
                <path d="M 32,56 Q 31,59 30,61 Q 32,60 32,62 Q 33,60 34,61 Q 33,59 32,56" 
                      fill="#FFA500" opacity="0.9"/>
                <path d="M 32,58 L 31,60 L 32,61 L 33,60 Z" 
                      fill="#FFD700" opacity="1"/>
            </svg>
        `;
        
        const impactIcon = L.icon({
            iconUrl: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(svgIcon),
            iconSize: [56, 56],
            iconAnchor: [28, 28],
            popupAnchor: [0, -28]
        });

        this.impactMarker = L.marker([this.impactLocation.lat, this.impactLocation.lng], {
            icon: impactIcon,
            draggable: true
        }).addTo(this.map);

        // Marker sürüklendiğinde
        this.impactMarker.on('dragend', (e) => {
            const position = e.target.getLatLng();
            this.setImpactLocation(position.lat, position.lng);
        });

        // Popup ekle - Daha güzel ve temiz tasarım
        this.impactMarker.bindPopup(`
            <div style="text-align: center; padding: 12px 16px; font-family: 'Inter', 'Arial', sans-serif; min-width: 200px;">
                <div style="background: linear-gradient(135deg, #d32f2f 0%, #c62828 100%); color: white; padding: 8px 12px; border-radius: 6px; margin: -12px -16px 10px -16px; font-weight: bold; font-size: 13px; letter-spacing: 0.5px;">
                    🎯 TARGET
                </div>
                <div style="margin: 8px 0; padding: 8px; background: #f5f5f5; border-radius: 4px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                        <span style="color: #666; font-size: 11px; font-weight: 600;">LAT:</span>
                        <span style="color: #333; font-size: 11px; font-weight: bold;">${this.impactLocation.lat.toFixed(4)}°</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #666; font-size: 11px; font-weight: 600;">LNG:</span>
                        <span style="color: #333; font-size: 11px; font-weight: bold;">${this.impactLocation.lng.toFixed(4)}°</span>
                    </div>
                </div>
                <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid #e0e0e0;">
                    <small style="color: #999; font-size: 10px; font-style: italic;">💡 Drag marker or click map</small>
                </div>
            </div>
        `, {
            closeButton: true,
            autoClose: false,
            closeOnClick: false,
            className: 'custom-impact-popup'
        }).openPopup();
    }

    updateDamageZones(damageData) {
        // Önceki hasar dairelerini temizle
        this.clearDamageZones();

        if (!damageData || !damageData.damage_zones) {
            console.warn('Hasar verisi eksik');
            return;
        }
        
        if (!this.map) {
            console.warn('Harita henüz hazır değil');
            return;
        }

        const location = [this.impactLocation.lat, this.impactLocation.lng];

        // ANİMASYONLU ETKİ BÖLGELERİ - Hesaplamalar
        const craterRadiusKm = damageData.crater_diameter_km / 2;
        const craterDepthM = damageData.crater_depth_m;
        
        // Fireball radius (termal radyasyon) - yaklaşık TNT'ye göre
        const tntMt = damageData.tnt_equivalent_megatons || 1;
        const fireballRadiusKm = Math.pow(tntMt, 0.4) * 0.5; // Empirical formula
        
        // Shock wave radius (basınç dalgası) - yıkıcı dalga
        const shockWaveRadiusKm = Math.pow(tntMt, 0.33) * 2.5;
        
        // Wind blast radius (rüzgar patlaması) - aşırı rüzgarlar
        const windBlastRadiusKm = Math.pow(tntMt, 0.33) * 3.5;
        
        // Seismic effect radius (deprem etkisi)
        const seismicRadiusKm = damageData.damage_zones.light_damage_km * 1.5;

        // ETKİ KATMANLARI (dıştan içe sıralı)
        const effectLayers = [
            {
                name: 'Earthquake Effect',
                nameTr: 'Deprem Etkisi',
                icon: '🌍',
                radiusKm: seismicRadiusKm,
                color: '#9c27b0',
                fillOpacity: 0.05,
                weight: 2,
                dashArray: '10, 10',
                description: 'Seismic waves felt',
                descriptionTr: 'Sismik dalgalar hissedilir',
                casualties: damageData.population_impact?.earthquake_casualties || 0
            },
            {
                name: 'Wind Blast Zone',
                nameTr: 'Rüzgar Patlaması Bölgesi',
                icon: '💨',
                radiusKm: windBlastRadiusKm,
                color: '#607d8b',
                fillOpacity: 0.08,
                weight: 2,
                description: 'Hurricane-force winds, trees knocked down',
                descriptionTr: 'Kasırga şiddetinde rüzgar, ağaçlar devrilir',
                casualties: damageData.population_impact?.wind_casualties || 0
            },
            {
                name: 'Shock Wave Zone',
                nameTr: 'Şok Dalgası Bölgesi',
                icon: '💥',
                radiusKm: shockWaveRadiusKm,
                color: '#ff9800',
                fillOpacity: 0.12,
                weight: 2,
                description: 'Buildings collapse, ruptured eardrums',
                descriptionTr: 'Binalar çöker, kulak zarları patlar',
                casualties: damageData.population_impact?.shockwave_casualties || 0
            },
            {
                name: 'Fireball Zone',
                nameTr: 'Ateş Topu Bölgesi',
                icon: '🔥',
                radiusKm: fireballRadiusKm,
                color: '#ff5722',
                fillOpacity: 0.18,
                weight: 3,
                description: 'Intense thermal radiation, severe burns',
                descriptionTr: 'Yoğun termal radyasyon, ciddi yanıklar',
                casualties: damageData.population_impact?.thermal_casualties || 0
            },
            {
                name: 'Impact Crater',
                nameTr: 'Çarpma Krateri',
                icon: '💀',
                radiusKm: craterRadiusKm,
                color: '#000000',
                fillOpacity: 0.6,
                weight: 4,
                description: 'Total vaporization',
                descriptionTr: 'Tamamen buharlaşma',
                casualties: damageData.population_impact?.crater_casualties || 0
            }
        ];

        // ANİMASYONLU EKLEME - Her katman sırayla görünür
        effectLayers.forEach((layer, index) => {
            setTimeout(() => {
                this.addAnimatedEffectLayer(location, layer, damageData);
            }, index * 800); // Her katman 800ms arayla
        });

        // Haritayı en geniş alana zoom'la
        setTimeout(() => {
            const maxRadius = seismicRadiusKm * 1000; // metre
            const bounds = L.latLng(location).toBounds(maxRadius * 2.2);
            this.map.fitBounds(bounds, { padding: [50, 50] });
        }, effectLayers.length * 800);
    }

    addAnimatedEffectLayer(location, layer, damageData) {
        if (!this.map) return;

        // Daire oluştur
        const circle = L.circle(location, {
            color: layer.color,
            fillColor: layer.color,
            fillOpacity: 0, // Başlangıçta görünmez
            radius: 0, // Başlangıçta 0 boyut
            weight: layer.weight,
            dashArray: layer.dashArray || '',
            className: 'animated-effect-layer'
        }).addTo(this.map);

        // Popup içeriği (dile göre)
        const lang = window.appState?.currentLanguage || 'en';
        const name = lang === 'tr' ? layer.nameTr : layer.name;
        const desc = lang === 'tr' ? layer.descriptionTr : layer.description;
        
        let popupContent = `
            <div style="text-align: center; min-width: 200px; padding: 8px;">
                <div style="font-size: 2rem; margin-bottom: 8px;">${layer.icon}</div>
                <strong style="font-size: 1.1rem; color: ${layer.color};">${name}</strong><br>
                <div style="margin: 8px 0; padding: 8px; background: rgba(0,0,0,0.1); border-radius: 4px;">
                    <strong>${lang === 'tr' ? 'Yarıçap' : 'Radius'}:</strong> ${layer.radiusKm.toFixed(1)} km
                </div>
                <div style="font-size: 0.9rem; color: #666; margin-top: 6px;">
                    ${desc}
                </div>
        `;
        
        // Eğer casualty verisi varsa ekle
        if (layer.casualties > 0) {
            popupContent += `
                <div style="margin-top: 8px; padding: 6px; background: rgba(234, 67, 53, 0.1); border-radius: 4px; border-left: 3px solid #ea4335;">
                    <strong style="color: #ea4335;">⚠️ ${lang === 'tr' ? 'Tahmini Kayıp' : 'Est. Casualties'}:</strong><br>
                    <span style="font-size: 1.1rem; font-weight: bold;">${this.formatNumber(layer.casualties)} ${lang === 'tr' ? 'kişi' : 'people'}</span>
                </div>
            `;
        }
        
        popupContent += `</div>`;
        
        circle.bindPopup(popupContent);

        this.damageCircles.push(circle);

        // ANIMASYON: Scale up + Fade in
        const targetRadius = layer.radiusKm * 1000; // metre
        const targetOpacity = layer.fillOpacity;
        const duration = 600; // ms
        const steps = 30;
        const stepDuration = duration / steps;

        let currentStep = 0;
        const animate = () => {
            currentStep++;
            const progress = currentStep / steps;
            
            // Easing function (ease-out)
            const easedProgress = 1 - Math.pow(1 - progress, 3);
            
            const currentRadius = targetRadius * easedProgress;
            const currentOpacity = targetOpacity * easedProgress;
            
            circle.setRadius(currentRadius);
            circle.setStyle({ fillOpacity: currentOpacity });
            
            if (currentStep < steps) {
                requestAnimationFrame(animate);
            } else {
                // Animasyon bitti - pulse efekti ekle
                circle.openPopup();
                setTimeout(() => circle.closePopup(), 2000);
            }
        };
        
        requestAnimationFrame(animate);
    }

    formatNumber(num) {
        if (num >= 1e6) {
            return (num / 1e6).toFixed(2) + 'M';
        } else if (num >= 1e3) {
            return (num / 1e3).toFixed(1) + 'K';
        }
        return Math.round(num).toString();
    }

    clearDamageZones() {
        // Tüm hasar dairelerini kaldır
        if (this.map && this.damageCircles) {
            this.damageCircles.forEach(circle => {
                this.map.removeLayer(circle);
            });
        }
        this.damageCircles = [];
    }

    showDeflectionPath(originalPath, deflectedPath) {
        // Yörünge sapması görselleştirmesi
        // Orijinal yörünge (kırmızı)
        const originalLine = L.polyline(originalPath, {
            color: '#ff4444',
            weight: 3,
            opacity: 0.7,
            dashArray: '10, 10'
        }).addTo(this.map);

        // Saptırılmış yörünge (yeşil)
        const deflectedLine = L.polyline(deflectedPath, {
            color: '#34a853',
            weight: 3,
            opacity: 0.7
        }).addTo(this.map);

        this.damageCircles.push(originalLine, deflectedLine);

        // Legend ekle
        const legend = L.control({ position: 'bottomright' });
        legend.onAdd = function() {
            const div = L.DomUtil.create('div', 'legend');
            div.style.background = 'rgba(0, 0, 0, 0.7)';
            div.style.padding = '10px';
            div.style.borderRadius = '5px';
            div.style.color = 'white';
            div.innerHTML = `
                <div><span style="color: #ff4444;">━━━</span> Orijinal Yörünge</div>
                <div><span style="color: #34a853;">━━━</span> Saptırılmış Yörünge</div>
            `;
            return div;
        };
        legend.addTo(this.map);
    }

    getImpactLocation() {
        return this.impactLocation;
    }

    destroy() {
        if (this.map) {
            this.map.remove();
        }
    }
}

// Global instance
let impactMap = null;
let usgsTopoMap = null;
let usgsImageryMap = null;

// Sayfa yüklendiğinde harita görselleştiriciyi başlat
document.addEventListener('DOMContentLoaded', () => {
    // Leaflet yüklenene kadar bekle
    let attempts = 0;
    const maxAttempts = 50; // 5 saniye timeout
    
    const initMap = setInterval(() => {
        attempts++;
        
        if (typeof L !== 'undefined') {
            try {
                // Container'ın hazır olduğunu kontrol et
                const container = document.getElementById('impactMap');
                if (container && container.offsetWidth > 0) {
                    impactMap = new ImpactMapVisualizer('impactMap');
                    console.log('✅ Harita başarıyla yüklendi');
                    clearInterval(initMap);
                } else if (attempts >= maxAttempts) {
                    console.warn('Harita container hazır değil');
                    clearInterval(initMap);
                }
            } catch (error) {
                console.error('Harita başlatma hatası:', error);
                // Hata olsa bile impactMap'i null olarak bırak
                impactMap = null;
                clearInterval(initMap);
            }
        } else if (attempts >= maxAttempts) {
            console.warn('Leaflet.js yüklenemedi, harita devre dışı');
            impactMap = null;
            clearInterval(initMap);
        }
    }, 100);
    
    // USGS Topografik Harita başlat
    const initUSGSMap = setInterval(() => {
        if (typeof L !== 'undefined') {
            try {
                const usgsContainer = document.getElementById('usgsTopoMap');
                if (usgsContainer && usgsContainer.offsetWidth > 0) {
                    initializeUSGSTopoMap();
                    console.log('✅ USGS Topografik Harita başarıyla yüklendi');
                    clearInterval(initUSGSMap);
                }
            } catch (error) {
                console.error('USGS Harita başlatma hatası:', error);
                clearInterval(initUSGSMap);
            }
        }
    }, 100);
    
    // USGS Imagery Topo Harita başlat
    const initUSGSImageryMap = setInterval(() => {
        if (typeof L !== 'undefined') {
            try {
                const imageryContainer = document.getElementById('usgsImageryMap');
                if (imageryContainer && imageryContainer.offsetWidth > 0) {
                    initializeUSGSImageryMap();
                    console.log('✅ USGS Imagery Topo Harita başarıyla yüklendi');
                    clearInterval(initUSGSImageryMap);
                }
            } catch (error) {
                console.error('USGS Imagery Harita başlatma hatası:', error);
                clearInterval(initUSGSImageryMap);
            }
        }
    }, 100);
});

// ============================================================================
// USGS Topographic Map Initialization
// ============================================================================

function initializeUSGSTopoMap() {
    const container = document.getElementById('usgsTopoMap');
    if (!container) {
        console.error('USGS Topo Map container bulunamadı');
        return;
    }
    
    // USGS Topografik Harita oluştur
    usgsTopoMap = L.map('usgsTopoMap', {
        center: [39.0, -98.0], // ABD merkezi
        zoom: 3, // Daha geniş görünüm için zoom seviyesini düşürdük
        zoomControl: true,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        touchZoom: true,
        dragging: true
    });
    
    // USGS Topographic Map tile layer
    L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles courtesy of the <a href="https://usgs.gov/" target="_blank">U.S. Geological Survey</a>',
        maxZoom: 16,
        minZoom: 3
    }).addTo(usgsTopoMap);
    
    // Harita boyutunu düzelt (gecikme ile)
    setTimeout(() => {
        if (usgsTopoMap) {
            usgsTopoMap.invalidateSize();
        }
    }, 250);
    
    // Impact location marker'ını USGS haritasına da ekle (eğer varsa)
    if (impactMap && impactMap.impactLocation) {
        const location = impactMap.impactLocation;
        
        // USGS haritasına marker ekle
        const usgsMarker = L.marker([location.lat, location.lng], {
            draggable: false
        }).addTo(usgsTopoMap);
        
        usgsMarker.bindPopup(`
            <div style="text-align: center; padding: 10px;">
                <strong style="color: #d32f2f;">Impact Location</strong><br>
                <small>Lat: ${location.lat.toFixed(4)}°</small><br>
                <small>Lng: ${location.lng.toFixed(4)}°</small>
            </div>
        `);
    }
}

// USGS haritasını güncelleme fonksiyonu (impact location değiştiğinde)
function updateUSGSMapLocation(lat, lng) {
    if (usgsTopoMap) {
        // Haritayı yeni konuma odakla - daha geniş görünüm için zoom seviyesini düşürdük
        usgsTopoMap.setView([lat, lng], 6);
        
        // Tüm marker'ları temizle
        usgsTopoMap.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                usgsTopoMap.removeLayer(layer);
            }
        });
        
        // Yeni marker ekle
        const marker = L.marker([lat, lng]).addTo(usgsTopoMap);
        marker.bindPopup(`
            <div style="text-align: center; padding: 10px;">
                <strong style="color: #d32f2f;">Impact Location</strong><br>
                <small>Lat: ${lat.toFixed(4)}°</small><br>
                <small>Lng: ${lng.toFixed(4)}°</small>
            </div>
        `).openPopup();
    }
    
    // USGS Imagery Map'i de güncelle
    if (usgsImageryMap) {
        usgsImageryMap.setView([lat, lng], 6);
        
        // Tüm marker'ları temizle
        usgsImageryMap.eachLayer(layer => {
            if (layer instanceof L.Marker) {
                usgsImageryMap.removeLayer(layer);
            }
        });
        
        // Yeni marker ekle
        const marker = L.marker([lat, lng]).addTo(usgsImageryMap);
        marker.bindPopup(`
            <div style="text-align: center; padding: 10px;">
                <strong style="color: #d32f2f;">Impact Location</strong><br>
                <small>Lat: ${lat.toFixed(4)}°</small><br>
                <small>Lng: ${lng.toFixed(4)}°</small>
            </div>
        `).openPopup();
    }
}

// ============================================================================
// USGS Imagery Topo Map Initialization
// ============================================================================

function initializeUSGSImageryMap() {
    const container = document.getElementById('usgsImageryMap');
    if (!container) {
        console.error('USGS Imagery Map container bulunamadı');
        return;
    }
    
    // USGS Imagery Topo Harita oluştur
    usgsImageryMap = L.map('usgsImageryMap', {
        center: [39.0, -98.0], // ABD merkezi
        zoom: 3, // Daha geniş görünüm için zoom seviyesini düşürdük
        zoomControl: true,
        scrollWheelZoom: true,
        doubleClickZoom: true,
        touchZoom: true,
        dragging: true
    });
    
    // USGS Imagery Topo tile layer - Satellite imagery + topographic overlay
    L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryTopo/MapServer/tile/{z}/{y}/{x}', {
        attribution: 'Tiles courtesy of the <a href="https://usgs.gov/" target="_blank">U.S. Geological Survey</a>',
        maxZoom: 16,
        minZoom: 3
    }).addTo(usgsImageryMap);
    
    // Harita boyutunu düzelt (gecikme ile)
    setTimeout(() => {
        if (usgsImageryMap) {
            usgsImageryMap.invalidateSize();
        }
    }, 250);
    
    // Impact location marker'ını Imagery haritasına da ekle (eğer varsa)
    if (impactMap && impactMap.impactLocation) {
        const location = impactMap.impactLocation;
        
        // Imagery haritasına marker ekle
        const imageryMarker = L.marker([location.lat, location.lng], {
            draggable: false
        }).addTo(usgsImageryMap);
        
        imageryMarker.bindPopup(`
            <div style="text-align: center; padding: 10px;">
                <strong style="color: #d32f2f;">Impact Location</strong><br>
                <small>Lat: ${location.lat.toFixed(4)}°</small><br>
                <small>Lng: ${location.lng.toFixed(4)}°</small>
            </div>
        `);
    }
}

