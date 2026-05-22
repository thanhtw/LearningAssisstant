/**
 * SVG face component with mood-based animations
 * Uses direct DOM manipulation for smooth updates without re-renders
 */

import React, { useEffect, useRef } from 'react';
import { Mood, getMoodConfig } from './emotions';
import './Avatar.css';

interface AvatarProps {
  mood?: Mood;
  size?: number;
}

export const Avatar: React.FC<AvatarProps> = ({ mood = 'neutral', size = 120 }) => {
  const svgRef = useRef<SVGSVGElement>(null);
  const animationFrameRef = useRef<number>();
  const blinkIntervalRef = useRef<ReturnType<typeof setInterval>>();
  const animationStartTimeRef = useRef<number>();
  const currentValuesRef = useRef({
    eyeRy: 7,
    cheekOpacity: 0.15,
  });

  /**
   * Tween a value from current to target over 300ms using requestAnimationFrame
   */
  const tweenValue = (
    currentValue: number,
    targetValue: number,
    duration: number,
    onUpdate: (value: number) => void
  ) => {
    const startTime = performance.now();

    const animate = (currentTime: number) => {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1);

      // Easing function: ease-in-out
      const easeProgress = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;
      const value = currentValue + (targetValue - currentValue) * easeProgress;

      onUpdate(value);

      if (progress < 1) {
        animationFrameRef.current = requestAnimationFrame(animate);
      }
    };

    animationFrameRef.current = requestAnimationFrame(animate);
  };

  /**
   * Blink animation - briefly closes eyes (eyeRy to 1)
   */
  const blinkEyes = () => {
    const targetEyeRy = 1;
    const blinkDuration = 150;

    tweenValue(currentValuesRef.current.eyeRy, targetEyeRy, blinkDuration, (value) => {
      currentValuesRef.current.eyeRy = value;
      const eyeLeft = document.getElementById('eye-left');
      const eyeRight = document.getElementById('eye-right');
      if (eyeLeft) eyeLeft.setAttribute('ry', value.toString());
      if (eyeRight) eyeRight.setAttribute('ry', value.toString());
    });

    // Restore eyes after blink
    setTimeout(() => {
      const config = getMoodConfig(mood);
      tweenValue(targetEyeRy, config.eyeRy, blinkDuration, (value) => {
        currentValuesRef.current.eyeRy = value;
        const eyeLeft = document.getElementById('eye-left');
        const eyeRight = document.getElementById('eye-right');
        if (eyeLeft) eyeLeft.setAttribute('ry', value.toString());
        if (eyeRight) eyeRight.setAttribute('ry', value.toString());
      });
    }, blinkDuration);
  };

  /**
   * Update SVG elements based on mood changes
   */
  const updateMoodAttributes = () => {
    const config = getMoodConfig(mood);

    // Update mouth path
    const mouth = document.getElementById('mouth');
    if (mouth) {
      mouth.setAttribute('d', config.mouthPath);
    }

    // Tween eyeRy
    tweenValue(currentValuesRef.current.eyeRy, config.eyeRy, 300, (value) => {
      currentValuesRef.current.eyeRy = value;
      const eyeLeft = document.getElementById('eye-left');
      const eyeRight = document.getElementById('eye-right');
      if (eyeLeft) eyeLeft.setAttribute('ry', value.toString());
      if (eyeRight) eyeRight.setAttribute('ry', value.toString());
    });

    // Tween cheek opacity
    tweenValue(currentValuesRef.current.cheekOpacity, config.cheekOpacity, 300, (value) => {
      currentValuesRef.current.cheekOpacity = value;
      const cheekLeft = document.getElementById('cheek-left');
      const cheekRight = document.getElementById('cheek-right');
      if (cheekLeft) cheekLeft.setAttribute('opacity', value.toString());
      if (cheekRight) cheekRight.setAttribute('opacity', value.toString());
    });

    // Update brow positions and rotations
    const browLeft = document.getElementById('brow-left');
    const browRight = document.getElementById('brow-right');

    if (browLeft) {
      // Apply transform with y offset and rotation
      browLeft.setAttribute(
        'transform',
        `translate(0 ${config.browYOffset}) rotate(${config.browRotation} 40 35)`
      );
    }

    if (browRight) {
      browRight.setAttribute(
        'transform',
        `translate(0 ${config.browYOffset}) rotate(${-config.browRotation} 80 35)`
      );
    }
  };

  /**
   * Initialize blink interval (3-5 seconds)
   */
  const initializeBlinking = () => {
    if (blinkIntervalRef.current) {
      clearInterval(blinkIntervalRef.current);
    }

    const blinkInterval = Math.random() * 2000 + 3000; // 3-5 seconds
    blinkIntervalRef.current = setInterval(() => {
      blinkEyes();
    }, blinkInterval);
  };

  /**
   * Handle mood changes with useEffect
   */
  useEffect(() => {
    if (svgRef.current) {
      updateMoodAttributes();
    }
  }, [mood]);

  /**
   * Setup and cleanup
   */
  useEffect(() => {
    initializeBlinking();

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (blinkIntervalRef.current) {
        clearInterval(blinkIntervalRef.current);
      }
    };
  }, []);

  const config = getMoodConfig(mood);

  return (
    <svg
      ref={svgRef}
      width={size}
      height={size}
      viewBox="0 0 120 120"
      className="avatar-svg"
      style={{ filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))' }}
    >
      {/* Hair */}
      <path
        id="hair"
        d="M 30 40 Q 60 20 90 40 Q 85 30 60 25 Q 35 30 30 40"
        fill="#8B7355"
        stroke="none"
      />

      {/* Face Background */}
      <circle
        id="face-bg"
        cx="60"
        cy="60"
        r="50"
        fill={config.color}
        stroke="#333"
        strokeWidth="1.5"
      />

      {/* Left Eye */}
      <ellipse
        id="eye-left"
        cx="40"
        cy="45"
        rx="6"
        ry={config.eyeRy}
        fill="white"
        stroke="#333"
        strokeWidth="0.8"
      />

      {/* Right Eye */}
      <ellipse
        id="eye-right"
        cx="80"
        cy="45"
        rx="6"
        ry={config.eyeRy}
        fill="white"
        stroke="#333"
        strokeWidth="0.8"
      />

      {/* Left Pupil */}
      <circle
        id="pupil-left"
        cx="40"
        cy="45"
        r="3"
        fill="black"
      />
      <circle cx="41" cy="43" r="1" fill="white" opacity="0.7" />

      {/* Right Pupil */}
      <circle
        id="pupil-right"
        cx="80"
        cy="45"
        r="3"
        fill="black"
      />
      <circle cx="81" cy="43" r="1" fill="white" opacity="0.7" />

      {/* Left Eyebrow */}
      <path
        id="brow-left"
        d="M 32 35 Q 40 32 48 35"
        stroke="#333"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        transform={`translate(0 ${config.browYOffset}) rotate(${config.browRotation} 40 35)`}
      />

      {/* Right Eyebrow */}
      <path
        id="brow-right"
        d="M 72 35 Q 80 32 88 35"
        stroke="#333"
        strokeWidth="2"
        fill="none"
        strokeLinecap="round"
        transform={`translate(0 ${config.browYOffset}) rotate(${-config.browRotation} 80 35)`}
      />

      {/* Mouth */}
      <path
        id="mouth"
        d={config.mouthPath}
        stroke="#333"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />

      {/* Left Cheek */}
      <ellipse
        id="cheek-left"
        cx="25"
        cy="55"
        rx="8"
        ry="6"
        fill="#FF6B9D"
        opacity={config.cheekOpacity}
      />

      {/* Right Cheek */}
      <ellipse
        id="cheek-right"
        cx="95"
        cy="55"
        rx="8"
        ry="6"
        fill="#FF6B9D"
        opacity={config.cheekOpacity}
      />
    </svg>
  );
};

export default Avatar;
