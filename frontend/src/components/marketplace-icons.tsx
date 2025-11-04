import { 
  SiAmazon, 
  SiEbay, 
  SiEtsy, 
  SiShopify,
  SiZalando,
  SiWish
} from 'react-icons/si';
import { TbBrandVinted } from 'react-icons/tb';
import { Store } from 'lucide-react';
import {
  BolIcon,
  AllegroIcon,
  KauflandIcon,
  OnBuyIcon,
  JoomIcon,
  AboutYouIcon,
  OttoIcon,
  CdiscountIcon,
  FnacDartyIcon,
  StockXIcon,
  LaRedouteIcon,
  GaleriesLafayetteIcon,
  AsosIcon
} from './marketplace-svg-icons';

interface MarketplaceIconProps {
  name: string;
  className?: string;
}

const marketplaceIcons: Record<string, { icon: React.ComponentType<any>; color: string }> = {
  // ✅ Icônes officielles disponibles dans react-icons
  amazon: { icon: SiAmazon, color: '#FF9900' },
  ebay: { icon: SiEbay, color: '#E53238' },
  etsy: { icon: SiEtsy, color: '#F1641E' },
  shopify: { icon: SiShopify, color: '#96BF48' },
  zalando: { icon: SiZalando, color: '#FF6900' },
  vinted: { icon: TbBrandVinted, color: '#09B1BA' },
  wish: { icon: SiWish, color: '#2FB7EC' },
  
  // ✅ SVG custom pour les marketplaces non disponibles dans react-icons
  bol: { icon: BolIcon, color: '#0000FF' },
  allegro: { icon: AllegroIcon, color: '#FF5A00' },
  kaufland: { icon: KauflandIcon, color: '#DD0000' },
  onbuy: { icon: OnBuyIcon, color: '#7C3AED' },
  joom: { icon: JoomIcon, color: '#7C3F9E' },
  aboutyou: { icon: AboutYouIcon, color: '#1F1F1F' },
  otto: { icon: OttoIcon, color: '#D50000' },
  cdiscount: { icon: CdiscountIcon, color: '#006CB7' },
  fnacdarty: { icon: FnacDartyIcon, color: '#F39200' },
  stockx: { icon: StockXIcon, color: '#06874A' },
  laredoute: { icon: LaRedouteIcon, color: '#E6001E' },
  galerieslafayette: { icon: GaleriesLafayetteIcon, color: '#000000' },
  asos: { icon: AsosIcon, color: '#000000' },
};

export function MarketplaceIcon({ name, className = 'w-12 h-12' }: MarketplaceIconProps) {
  const normalizedName = name.toLowerCase().replace(/[^a-z0-9]/g, '');
  const marketplace = marketplaceIcons[normalizedName] || { icon: Store, color: '#D4A574' };
  const Icon = marketplace.icon;

  // Vérifier si c'est un composant SVG custom (qui accepte className et color comme props)
  const isCustomSVG = [
    BolIcon, AllegroIcon, KauflandIcon, OnBuyIcon, JoomIcon, AboutYouIcon,
    OttoIcon, CdiscountIcon, FnacDartyIcon, StockXIcon, LaRedouteIcon, GaleriesLafayetteIcon, AsosIcon
  ].includes(Icon as any);

  if (isCustomSVG) {
    return <Icon className={className} color={marketplace.color} />;
  }

  // Pour les icônes de react-icons, utiliser style
  return (
    <Icon 
      className={className} 
      style={{ color: marketplace.color }} 
    />
  );
}

