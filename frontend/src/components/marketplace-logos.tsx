// Composants de logos pour les marketplaces
export const MarketplaceLogo = ({ name, className = "w-12 h-12" }: { name: string; className?: string }) => {
  const logos: Record<string, JSX.Element> = {
    amazon: (
      <svg viewBox="0 0 100 100" className={className} fill="currentColor">
        <path d="M70 65c-8 6-20 9-30 9-14 0-27-5-37-14-.8-.7-.1-1.7.8-1.1 10 6 23 9 36 9 9 0 18-2 27-5 1.3-.6 2.4.9 1.2 2z"/>
        <path d="M73 62c-1-1.3-7-.6-10-.3-.8.1-.9-.6-.2-1.1 5-3.5 13-2.5 13.8-1.3.9 1.2-.2 9.7-5.1 13.8-.7.6-1.5.3-1.1-.5.9-2.3 3-7.4 1.6-9.6z"/>
        <path d="M40 25v-3c0-.5.4-.9.9-.9h16c.5 0 .9.4.9.9v2.6c0 .5-.4 1.2-1.1 2.3l-8.3 11.8c3.1-.1 6.3.4 9 2 .6.4.8.9.9 1.4v3.2c0 .5-.6 1.1-1.2.8-4.8-2.5-11.2-2.8-16.5.1-.6.3-1.2-.3-1.2-.8v-3c0-.6 0-1.6.6-2.5l9.6-13.8H40.9c-.5 0-.9-.4-.9-.9z"/>
      </svg>
    ),
    ebay: (
      <svg viewBox="0 0 100 100" className={className}>
        <defs>
          <linearGradient id="ebay-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#e53238" />
            <stop offset="25%" stopColor="#0064d2" />
            <stop offset="50%" stopColor="#f5af02" />
            <stop offset="75%" stopColor="#86b817" />
          </linearGradient>
        </defs>
        <text x="50" y="65" fontFamily="Arial, sans-serif" fontSize="40" fontWeight="bold" textAnchor="middle" fill="url(#ebay-gradient)">eBay</text>
      </svg>
    ),
    etsy: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#F1641E"/>
        <text x="50" y="60" fontFamily="Georgia, serif" fontSize="28" fontWeight="bold" textAnchor="middle" fill="white">Etsy</text>
      </svg>
    ),
    bol: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#0000A4"/>
        <text x="50" y="65" fontFamily="Arial, sans-serif" fontSize="35" fontWeight="bold" textAnchor="middle" fill="white">bol</text>
      </svg>
    ),
    allegro: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#FF5A00"/>
        <path d="M35 40 L50 60 L65 40" stroke="white" strokeWidth="6" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      </svg>
    ),
    kaufland: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#DC0028"/>
        <text x="50" y="58" fontFamily="Arial, sans-serif" fontSize="22" fontWeight="bold" textAnchor="middle" fill="white">Kaufland</text>
      </svg>
    ),
    onbuy: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#7B48D9"/>
        <text x="50" y="62" fontFamily="Arial, sans-serif" fontSize="24" fontWeight="bold" textAnchor="middle" fill="white">OnBuy</text>
      </svg>
    ),
    wish: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#2FB7EC"/>
        <path d="M50 30 L55 45 L70 45 L58 54 L63 69 L50 60 L37 69 L42 54 L30 45 L45 45 Z" fill="white"/>
      </svg>
    ),
    joom: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#00B4CC"/>
        <text x="50" y="62" fontFamily="Arial, sans-serif" fontSize="28" fontWeight="bold" textAnchor="middle" fill="white">Joom</text>
      </svg>
    ),
    zalando: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#FF6900"/>
        <text x="50" y="58" fontFamily="Arial, sans-serif" fontSize="18" fontWeight="bold" textAnchor="middle" fill="white">ZALANDO</text>
      </svg>
    ),
    aboutyou: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#000000"/>
        <text x="50" y="52" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" textAnchor="middle" fill="white">ABOUT</text>
        <text x="50" y="68" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" textAnchor="middle" fill="white">YOU</text>
      </svg>
    ),
    otto: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#D40E14"/>
        <text x="50" y="65" fontFamily="Arial, sans-serif" fontSize="35" fontWeight="bold" textAnchor="middle" fill="white">OTTO</text>
      </svg>
    ),
    cdiscount: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#00A0DF"/>
        <text x="50" y="58" fontFamily="Arial, sans-serif" fontSize="18" fontWeight="bold" textAnchor="middle" fill="white">Cdiscount</text>
      </svg>
    ),
    fnac: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#F0B30A"/>
        <text x="50" y="58" fontFamily="Arial, sans-serif" fontSize="24" fontWeight="bold" textAnchor="middle" fill="#000">FNAC</text>
      </svg>
    ),
    vinted: (
      <svg viewBox="0 0 100 100" className={className}>
        <circle cx="50" cy="50" r="40" fill="#09B1BA"/>
        <text x="50" y="62" fontFamily="Arial, sans-serif" fontSize="22" fontWeight="bold" textAnchor="middle" fill="white">Vinted</text>
      </svg>
    ),
    stockx: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#00B65A"/>
        <text x="50" y="62" fontFamily="Arial, sans-serif" fontSize="24" fontWeight="bold" textAnchor="middle" fill="white">StockX</text>
      </svg>
    ),
    shopify: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#96BF48"/>
        <path d="M50 30 L60 40 L60 70 L50 75 L40 70 L40 40 Z" fill="white"/>
        <path d="M50 30 L50 75 M40 40 L60 40" stroke="#96BF48" strokeWidth="2"/>
      </svg>
    ),
    laredoute: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#E4002B"/>
        <text x="50" y="52" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" textAnchor="middle" fill="white">La</text>
        <text x="50" y="68" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="bold" textAnchor="middle" fill="white">Redoute</text>
      </svg>
    ),
    galerieslafayette: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#000000"/>
        <text x="50" y="45" fontFamily="Georgia, serif" fontSize="14" fontWeight="bold" textAnchor="middle" fill="white">Galeries</text>
        <text x="50" y="65" fontFamily="Georgia, serif" fontSize="14" fontWeight="bold" textAnchor="middle" fill="white">Lafayette</text>
      </svg>
    ),
    asos: (
      <svg viewBox="0 0 100 100" className={className}>
        <rect width="100" height="100" rx="10" fill="#000000"/>
        <text x="50" y="65" fontFamily="Arial, sans-serif" fontSize="35" fontWeight="bold" textAnchor="middle" fill="white">ASOS</text>
      </svg>
    ),
  };

  return logos[name] || <div className={className} />;
};

