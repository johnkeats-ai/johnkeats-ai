import * as THREE from 'three';

class KeatsOrb {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.setup();
        this.createOrb();
        this.animate();
        
        window.addEventListener('resize', () => this.onResize());
    }

    setup() {
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.z = 5;

        this.renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.container.appendChild(this.renderer.domElement);
    }

    createOrb() {
        // Core sphere
        const geometry = new THREE.IcosahedronGeometry(1.5, 32);
        
        // Custom shader material for the "breathing" effect
        this.material = new THREE.ShaderMaterial({
            uniforms: {
                time: { value: 0 },
                color: { value: new THREE.Color(0xD4A574) }, // Amber
                intensity: { value: 1.0 }
            },
            vertexShader: `
                varying vec3 vNormal;
                varying vec2 vUv;
                uniform float time;
                
                void main() {
                    vNormal = normalize(normalMatrix * normal);
                    vUv = uv;
                    
                    // Gentle displacement based on time (breathing)
                    float distortion = sin(position.x * 2.0 + time * 0.5) * 0.1 +
                                     cos(position.y * 2.0 + time * 0.4) * 0.1;
                    vec3 newPosition = position + normal * distortion;
                    
                    gl_Position = projectionMatrix * modelViewMatrix * vec4(newPosition, 1.0);
                }
            `,
            fragmentShader: `
                varying vec3 vNormal;
                uniform vec3 color;
                uniform float intensity;
                
                void main() {
                    // Fresnel-like glow
                    float glow = pow(0.7 - dot(vNormal, vec3(0, 0, 1.0)), 3.0);
                    vec3 finalColor = color + (vec3(1.0) * glow * 0.5);
                    gl_FragColor = vec4(finalColor, glow * intensity);
                }
            `,
            transparent: true,
            side: THREE.BackSide,
            blending: THREE.AdditiveBlending
        });

        this.orb = new THREE.Mesh(geometry, this.material);
        this.scene.add(this.orb);

        // Sub-pulses for depth
        const pulseGeometry = new THREE.IcosahedronGeometry(1.4, 16);
        const pulseMaterial = new THREE.MeshBasicMaterial({
            color: 0xD4A574,
            transparent: true,
            opacity: 0.1,
            wireframe: true
        });
        this.pulse = new THREE.Mesh(pulseGeometry, pulseMaterial);
        this.scene.add(this.pulse);
    }

    onResize() {
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }

    setState(state, value = 0) {
        // States: SILENCE, KEATS_SPEAKING, USER_SPEAKING
        switch(state) {
            case 'KEATS_SPEAKING':
                this.material.uniforms.color.value.setHex(0xD4B08C);
                this.targetIntensity = 1.2 + value * 0.5;
                this.pulseRate = 1.5;
                break;
            case 'USER_SPEAKING':
                this.material.uniforms.color.value.setHex(0xA5C9D4); // Blue-ish
                this.targetIntensity = 0.8 + value * 0.3;
                this.pulseRate = 0.8;
                break;
            case 'SILENCE':
            default:
                this.material.uniforms.color.value.setHex(0xD4A574);
                this.targetIntensity = 0.5;
                this.pulseRate = 0.4;
                break;
        }
    }

    animate() {
        requestAnimationFrame(() => this.animate());
        
        const time = performance.now() * 0.001;
        this.material.uniforms.time.value = time;
        
        // Smooth intensity transition
        if (this.targetIntensity) {
            this.material.uniforms.intensity.value += (this.targetIntensity - this.material.uniforms.intensity.value) * 0.1;
        }

        this.orb.rotation.y += 0.002;
        this.orb.rotation.x += 0.001;
        
        const pulseScale = 1.0 + Math.sin(time * this.pulseRate || 0.4) * 0.05;
        this.orb.scale.set(pulseScale, pulseScale, pulseScale);
        this.pulse.scale.set(pulseScale * 1.1, pulseScale * 1.1, pulseScale * 1.1);
        this.pulse.rotation.y -= 0.003;

        this.renderer.render(this.scene, this.camera);
    }
}

export default KeatsOrb;
