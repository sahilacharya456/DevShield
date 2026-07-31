import { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Points, PointMaterial } from '@react-three/drei';
import * as THREE from 'three';

function ParticleSphere({ numParticles = 2000 }) {
  const ref = useRef<THREE.Points>(null);

  // Generate random points in a sphere
  const positions = new Float32Array(numParticles * 3);
  for (let i = 0; i < numParticles; i++) {
    const radius = 2.5 + Math.random() * 0.5;
    const theta = Math.random() * 2 * Math.PI;
    const phi = Math.acos(Math.random() * 2 - 1);
    
    positions[i * 3] = radius * Math.sin(phi) * Math.cos(theta);
    positions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta);
    positions[i * 3 + 2] = radius * Math.cos(phi);
  }

  useFrame((state, delta) => {
    if (ref.current) {
      ref.current.rotation.y += delta * 0.2;
      ref.current.rotation.x += delta * 0.1;
      
      // Add pulsing effect to scale
      const scale = 1 + Math.sin(state.clock.elapsedTime * 2) * 0.05;
      ref.current.scale.set(scale, scale, scale);
    }
  });

  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#8B5CF6"
        size={0.04}
        sizeAttenuation={true}
        depthWrite={false}
        blending={THREE.AdditiveBlending}
      />
    </Points>
  );
}

export default function NeuralCore() {
  return (
    <div className="w-full h-full absolute inset-0 cursor-crosshair pointer-events-none mix-blend-screen opacity-60">
      <Canvas camera={{ position: [0, 0, 8], fov: 45 }}>
        <ParticleSphere />
      </Canvas>
    </div>
  );
}
