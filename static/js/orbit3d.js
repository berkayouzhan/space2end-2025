/* ============================================================================
   ADIM 3.2: THREE.JS İLE 3D YÖRÜNGE SİMÜLASYONU
   ============================================================================ */

class Orbit3DVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.earth = null;
        this.asteroid = null;
        this.orbitLine = null;
        this.animationId = null;
        
        this.init();
    }

    init() {
        // Element kontrolü
        if (!this.container) {
            console.error('3D container bulunamadı');
            return;
        }
        
        // Scene oluştur
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0x000510);

        // Kamera ayarları
        const width = this.container.clientWidth || 800;
        const height = this.container.clientHeight || 400;
        this.camera = new THREE.PerspectiveCamera(60, width / height, 0.1, 10000);
        this.camera.position.set(0, 50, 100);

        // Renderer oluştur
        this.renderer = new THREE.WebGLRenderer({ antialias: true });
        this.renderer.setSize(width, height);
        this.container.appendChild(this.renderer.domElement);

        // Orbit Controls (kamera kontrolü için)
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.minDistance = 20;
        this.controls.maxDistance = 500;

        // Işıklandırma
        const ambientLight = new THREE.AmbientLight(0x404040, 2);
        this.scene.add(ambientLight);

        const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
        directionalLight.position.set(100, 100, 50);
        this.scene.add(directionalLight);

        // Dünya'yı oluştur
        this.createEarth();

        // Yıldızlar ekle
        this.createStars();

        // Animasyonu başlat
        this.animate();

        // Window resize handler
        window.addEventListener('resize', () => this.onWindowResize());
        
        console.log('✅ 3D sahne başlatıldı');
    }

    createEarth() {
        // Dünya geometrisi
        const geometry = new THREE.SphereGeometry(6.371, 64, 64); // 6.371 = Dünya yarıçapı (1000 km = 1 birim)
        
        // Dünya materyali - gerçekçi mavi-yeşil görünüm
        const material = new THREE.MeshPhongMaterial({
            color: 0x4a90e2,  // Okyanus mavisi
            emissive: 0x0a3d62,  // Derin mavi ışıma
            specular: 0x111111,  // Parlama
            shininess: 15,
            flatShading: false
        });
        
        this.earth = new THREE.Mesh(geometry, material);
        this.scene.add(this.earth);
        
        // Kara kütleleri ekle (basitleştirilmiş)
        this.addContinents();

        // Atmosfer efekti (glow)
        const atmosphereGeometry = new THREE.SphereGeometry(6.6, 64, 64);
        const atmosphereMaterial = new THREE.MeshBasicMaterial({
            color: 0x4488ff,
            transparent: true,
            opacity: 0.2,
            side: THREE.BackSide
        });
        const atmosphere = new THREE.Mesh(atmosphereGeometry, atmosphereMaterial);
        this.scene.add(atmosphere);

        // Eksen (debugging için)
        const axesHelper = new THREE.AxesHelper(15);
        this.scene.add(axesHelper);
    }

    addContinents() {
        // Kara kütlelerini yeşil renkli basit noktalar olarak ekle
        // (Bu basitleştirilmiş bir versiyondur - gerçek texture yerine)
        
        const continentGeometry = new THREE.SphereGeometry(6.373, 64, 64);
        const continentMaterial = new THREE.MeshPhongMaterial({
            color: 0x2d5016,  // Koyu yeşil
            transparent: true,
            opacity: 0.7,
            emissive: 0x1a3010
        });
        
        // Kara kütlelerini temsil eden ikinci bir katman
        const continents = new THREE.Mesh(continentGeometry, continentMaterial);
        this.earth.add(continents);
        
        // Not: Gerçek bir uygulamada NASA'nın Dünya texture map'i kullanılmalı
    }

    createStars() {
        // Arka planda yıldızlar
        const starGeometry = new THREE.BufferGeometry();
        const starMaterial = new THREE.PointsMaterial({
            color: 0xffffff,
            size: 0.7,
            transparent: true
        });

        const starVertices = [];
        for (let i = 0; i < 10000; i++) {
            const x = (Math.random() - 0.5) * 2000;
            const y = (Math.random() - 0.5) * 2000;
            const z = (Math.random() - 0.5) * 2000;
            starVertices.push(x, y, z);
        }

        starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
        const stars = new THREE.Points(starGeometry, starMaterial);
        this.scene.add(stars);
    }

    updateOrbit(asteroidData) {
        // Önceki asteroid ve yörüngeyi temizle
        if (this.asteroid) {
            this.scene.remove(this.asteroid);
        }
        if (this.orbitLine) {
            this.scene.remove(this.orbitLine);
        }

        // Asteroid oluştur
        const asteroidRadius = asteroidData.diameter_m / 1000 / 2; // km'ye çevir ve yarıçap
        const asteroidGeometry = new THREE.SphereGeometry(Math.max(0.5, asteroidRadius), 32, 32);
        const asteroidMaterial = new THREE.MeshPhongMaterial({
            color: 0xff4444,
            emissive: 0x440000,
            shininess: 5
        });
        
        this.asteroid = new THREE.Mesh(asteroidGeometry, asteroidMaterial);
        this.scene.add(this.asteroid);

        // Yörünge çizgisi oluştur (eliptik yörünge)
        this.createOrbitPath(asteroidData);
    }

    createOrbitPath(asteroidData) {
        // Basitleştirilmiş eliptik yörünge
        // Semi-major axis: Dünya'dan uzaklığa göre hesaplanır
        const earthRadius = 6.371;
        const missDistance = asteroidData.miss_distance_km || 500000;
        const semiMajorAxis = missDistance / 1000 + earthRadius; // Dünya merkezinden uzaklık
        
        // Eccentricity (eksantriklik) - tehlikeli asteroidler için daha yüksek
        const eccentricity = asteroidData.is_hazardous ? 0.7 : 0.5;
        const semiMinorAxis = semiMajorAxis * Math.sqrt(1 - eccentricity * eccentricity);

        // Eliptik yörünge noktalarını oluştur
        const points = [];
        const segments = 128;
        
        for (let i = 0; i <= segments; i++) {
            const angle = (i / segments) * Math.PI * 2;
            const x = semiMajorAxis * Math.cos(angle);
            const y = semiMinorAxis * Math.sin(angle);
            const z = 0;
            points.push(new THREE.Vector3(x, y, z));
        }

        const orbitGeometry = new THREE.BufferGeometry().setFromPoints(points);
        const orbitMaterial = new THREE.LineBasicMaterial({
            color: 0xffffff,
            transparent: true,
            opacity: 0.6
        });
        
        this.orbitLine = new THREE.Line(orbitGeometry, orbitMaterial);
        
        // Yörüngeyi約間45 derece eğ
        this.orbitLine.rotation.x = Math.PI / 4;
        this.scene.add(this.orbitLine);

        // Asteroidi yörünge üzerine yerleştir
        this.asteroid.position.set(semiMajorAxis, 0, 0);
        this.asteroid.rotation.x = Math.PI / 4;
    }

    updateAsteroidPosition(angle) {
        // Asteroidi yörünge üzerinde hareket ettir
        if (this.asteroid && this.orbitLine) {
            const points = this.orbitLine.geometry.attributes.position.array;
            const index = Math.floor((angle / (Math.PI * 2)) * (points.length / 3)) * 3;
            
            if (index < points.length) {
                this.asteroid.position.set(
                    points[index],
                    points[index + 1],
                    points[index + 2]
                );
            }
        }
    }

    highlightImpactTrajectory(impactAngle = 45) {
        // Çarpma траектоrisini vurgula
        if (!this.asteroid) return;

        // Dünya'ya doğru çarpma çizgisi
        const asteroidPos = this.asteroid.position.clone();
        const earthCenter = new THREE.Vector3(0, 0, 0);
        
        const trajectoryPoints = [asteroidPos, earthCenter];
        const trajectoryGeometry = new THREE.BufferGeometry().setFromPoints(trajectoryPoints);
        const trajectoryMaterial = new THREE.LineBasicMaterial({
            color: 0xff0000,
            linewidth: 3
        });
        
        const trajectoryLine = new THREE.Line(trajectoryGeometry, trajectoryMaterial);
        this.scene.add(trajectoryLine);

        // 2 saniye sonra çizgiyi kaldır
        setTimeout(() => {
            this.scene.remove(trajectoryLine);
        }, 2000);
    }

    animate() {
        this.animationId = requestAnimationFrame(() => this.animate());
        
        // Dünya'yı döndür
        if (this.earth) {
            this.earth.rotation.y += 0.001;
        }

        // Asteroidi yörünge üzerinde hareket ettir
        if (this.asteroid && this.orbitLine) {
            const time = Date.now() * 0.0001;
            this.updateAsteroidPosition(time);
        }

        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }

    onWindowResize() {
        const width = this.container.clientWidth;
        const height = this.container.clientHeight;
        
        this.camera.aspect = width / height;
        this.camera.updateProjectionMatrix();
        
        this.renderer.setSize(width, height);
    }

    destroy() {
        if (this.animationId) {
            cancelAnimationFrame(this.animationId);
        }
        if (this.renderer) {
            this.renderer.dispose();
        }
    }
}

// Global instance
let orbit3D = null;

// Sayfa yüklendiğinde 3D görselleştiriciyi başlat
document.addEventListener('DOMContentLoaded', () => {
    try {
        if (typeof THREE !== 'undefined') {
            orbit3D = new Orbit3DVisualizer('orbit3d');
            console.log('✅ 3D görselleştirme başarıyla yüklendi');
        } else {
            console.warn('Three.js yüklenemedi, 3D görselleştirme devre dışı');
        }
    } catch (error) {
        console.error('3D görselleştirme başlatma hatası:', error);
    }
});

