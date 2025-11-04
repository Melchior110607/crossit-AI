// SVG Logos pour les marketplaces non disponibles dans react-icons
import React from 'react';

interface SVGIconProps {
  className?: string;
  color?: string;
}

// bol.com (Bleu)
export const BolIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#0000FF' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="100" cy="100" r="90" fill={color} />
    <text x="100" y="130" fontSize="90" fontWeight="bold" textAnchor="middle" fill="white">bol</text>
  </svg>
);

// Allegro (Orange)
export const AllegroIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#FF5A00' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="30" fill={color} />
    <circle cx="70" cy="70" r="25" fill="white" />
    <circle cx="130" cy="130" r="25" fill="white" />
    <path d="M70 100 L130 100 L130 70" stroke="white" strokeWidth="15" fill="none" />
  </svg>
);

// Kaufland (Rouge)
export const KauflandIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#DD0000' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <text x="100" y="125" fontSize="70" fontWeight="bold" textAnchor="middle" fill="white">K</text>
  </svg>
);

// OnBuy (Violet)
export const OnBuyIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#7C3AED' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <circle cx="100" cy="100" r="90" fill={color} />
    <rect x="70" y="70" width="60" height="60" rx="10" fill="white" />
    <circle cx="100" cy="100" r="15" fill={color} />
  </svg>
);

// Joom (Violet foncé)
export const JoomIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#7C3F9E' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="40" fill={color} />
    <text x="100" y="130" fontSize="80" fontWeight="bold" textAnchor="middle" fill="white">J</text>
  </svg>
);

// About You (Noir)
export const AboutYouIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#1F1F1F' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="0" fill={color} />
    <text x="100" y="125" fontSize="60" fontWeight="300" textAnchor="middle" fill="white">AY</text>
  </svg>
);

// Otto (Rouge foncé)
export const OttoIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#D50000' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <circle cx="100" cy="100" r="50" stroke="white" strokeWidth="15" fill="none" />
  </svg>
);

// Cdiscount (Bleu)
export const CdiscountIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#006CB7' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="30" fill={color} />
    <path d="M 130 70 Q 160 100 130 130 Q 100 160 70 130 Q 40 100 70 70 Q 100 40 130 70" fill="white" />
  </svg>
);

// Fnac Darty (Orange)
export const FnacDartyIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#F39200' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <text x="100" y="130" fontSize="70" fontWeight="bold" textAnchor="middle" fill="white">fnac</text>
  </svg>
);

// StockX (Vert)
export const StockXIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#06874A' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="30" fill={color} />
    <path d="M 50 50 L 150 150 M 150 50 L 50 150" stroke="white" strokeWidth="20" strokeLinecap="round" />
  </svg>
);

// La Redoute (Rouge)
export const LaRedouteIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#E6001E' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <text x="100" y="125" fontSize="60" fontWeight="300" textAnchor="middle" fill="white">LR</text>
  </svg>
);

// Galeries Lafayette (Noir)
export const GaleriesLafayetteIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#000000' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <text x="100" y="125" fontSize="55" fontWeight="300" textAnchor="middle" fill="white">GL</text>
  </svg>
);

// ASOS (Noir)
export const AsosIcon: React.FC<SVGIconProps> = ({ className = 'w-12 h-12', color = '#000000' }) => (
  <svg className={className} viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="200" height="200" rx="20" fill={color} />
    <text x="100" y="130" fontSize="65" fontWeight="bold" textAnchor="middle" fill="white">ASOS</text>
  </svg>
);

