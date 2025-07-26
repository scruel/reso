import { Thread } from '@/types/product';
import { phoneThreads } from './phone-threads';

// 使用手机相关数据用于MVP录制
export const mockThreads: Thread[] = phoneThreads;

// 原始多样化数据（备用）
export const originalMockThreads: Thread[] = [
  {
    id: '999',
    good: {
      id: 999,
      title: 'iPhone 15 Pro Max 1TB 钛金属',
      pic_url: 'https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=400&h=400&fit=crop&crop=center',
      brand: 'Apple',
      category: '智慧型手機',
      categoryColor: '#007AFF',
      price: '59900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: '科技達人小李',
      user_pic_url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=center'
    }
  },
  {
    id: '1000',
    good: {
      id: 1000,
      title: 'Keychron K8 機械鍵盤',
      pic_url: 'https://source.unsplash.com/400x400?keyboard,mechanical&sig=2',
      brand: 'Keychron',
      category: '配件',
      categoryColor: '#10B981',
      price: '2990'
    }
  },
  {
    id: '1001',
    good: {
      id: 1001,
      title: 'Sony WH-1000XM5 無線降噪耳機',
      pic_url: 'https://source.unsplash.com/400x400?headphones,sony&sig=3',
      brand: 'Sony',
      category: '耳機',
      categoryColor: '#8B5CF6',
      price: '8990'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'AudioExpert Sarah',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=sarah'
    }
  },
  {
    id: '1002',
    good: {
      id: 1002,
      title: 'Samsung Galaxy S24 Ultra 1TB',
      pic_url: 'https://source.unsplash.com/400x400?samsung,smartphone&sig=4',
      brand: 'Samsung',
      category: '手機',
      categoryColor: '#3B82F6',
      price: '33067'
    }
  },
  {
    id: '1003',
    good: {
      id: 1003,
      title: 'Dell XPS 13 Plus 觸控筆電',
      pic_url: 'https://source.unsplash.com/400x400?laptop,dell&sig=5',
      brand: 'Dell',
      category: '電腦',
      categoryColor: '#10B981',
      price: '45000'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'TechGuru Mike',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=mike'
    }
  },
  {
    id: '1004',
    good: {
      id: 1004,
      title: 'Nintendo Switch OLED 白色主機',
      pic_url: 'https://source.unsplash.com/400x400?nintendo,gaming&sig=6',
      brand: 'Nintendo',
      category: '遊戲',
      categoryColor: '#EF4444',
      price: '10500'
    }
  },
  {
    id: '1005',
    good: {
      id: 1005,
      title: 'iPad Pro 12.9吋 M2晶片',
      pic_url: 'https://source.unsplash.com/400x400?ipad,tablet&sig=7',
      brand: 'Apple',
      category: '平板',
      categoryColor: '#3B82F6',
      price: '35900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Creative Pro',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=creative'
    }
  },
  {
    id: '1006',
    good: {
      id: 1006,
      title: 'AirPods Pro 第二代',
      pic_url: 'https://source.unsplash.com/400x400?airpods,wireless&sig=8',
      brand: 'Apple',
      category: '耳機',
      categoryColor: '#8B5CF6',
      price: '7490'
    }
  },
  {
    id: '1007',
    good: {
      id: 1007,
      title: 'MacBook Air M2 13吋',
      pic_url: 'https://source.unsplash.com/400x400?macbook,laptop&sig=9',
      brand: 'Apple',
      category: '電腦',
      categoryColor: '#10B981',
      price: '37900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Apple Specialist',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=apple'
    }
  },
  {
    id: '1008',
    good: {
      id: 1008,
      title: 'Google Pixel 8 Pro',
      pic_url: 'https://source.unsplash.com/400x400?pixel,google&sig=10',
      brand: 'Google',
      category: '手機',
      categoryColor: '#3B82F6',
      price: '32900'
    }
  },
  {
    id: '1009',
    good: {
      id: 1009,
      title: 'Microsoft Surface Pro 9',
      pic_url: 'https://source.unsplash.com/400x400?surface,microsoft&sig=11',
      brand: 'Microsoft',
      category: '平板',
      categoryColor: '#3B82F6',
      price: '31900'
    }
  },
  {
    id: '1010',
    good: {
      id: 1010,
      title: 'Logitech MX Master 3S 滑鼠',
      pic_url: 'https://source.unsplash.com/400x400?mouse,logitech&sig=12',
      brand: 'Logitech',
      category: '配件',
      categoryColor: '#10B981',
      price: '3290'
    }
  },
  {
    id: '1011',
    good: {
      id: 1011,
      title: 'ASUS ROG Strix 電競筆電',
      pic_url: 'https://source.unsplash.com/400x400?gaming,laptop&sig=13',
      brand: 'ASUS',
      category: '電腦',
      categoryColor: '#10B981',
      price: '65000'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Gaming Expert',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=gaming'
    }
  },
  {
    id: '1012',
    good: {
      id: 1012,
      title: 'Canon EOS R5 無反相機',
      pic_url: 'https://source.unsplash.com/400x400?camera,canon&sig=14',
      brand: 'Canon',
      category: '相機',
      categoryColor: '#F59E0B',
      price: '115000'
    }
  },
  {
    id: '1013',
    good: {
      id: 1013,
      title: 'Bose QuietComfort 45',
      pic_url: 'https://source.unsplash.com/400x400?bose,headphones&sig=15',
      brand: 'Bose',
      category: '耳機',
      categoryColor: '#8B5CF6',
      price: '10900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Audio Reviewer',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=audio'
    }
  },
  {
    id: '1014',
    good: {
      id: 1014,
      title: 'Razer DeathAdder V3 電競滑鼠',
      pic_url: 'https://source.unsplash.com/400x400?razer,gaming&sig=16',
      brand: 'Razer',
      category: '配件',
      categoryColor: '#10B981',
      price: '2290'
    }
  },
  {
    id: '1015',
    good: {
      id: 1015,
      title: 'LG 27吋 4K 顯示器',
      pic_url: 'https://source.unsplash.com/400x400?monitor,4k&sig=17',
      brand: 'LG',
      category: '顯示器',
      categoryColor: '#6366F1',
      price: '12900'
    }
  },
  {
    id: '1016',
    good: {
      id: 1016,
      title: 'SteelSeries Apex Pro 機械鍵盤',
      pic_url: 'https://source.unsplash.com/400x400?steelseries,keyboard&sig=18',
      brand: 'SteelSeries',
      category: '配件',
      categoryColor: '#10B981',
      price: '6990'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Pro Gamer',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=progamer'
    }
  },
  {
    id: '1017',
    good: {
      id: 1017,
      title: 'Dyson V15 Detect 無線吸塵器',
      pic_url: 'https://source.unsplash.com/400x400?dyson,vacuum&sig=19',
      brand: 'Dyson',
      category: '家電',
      categoryColor: '#EC4899',
      price: '24900'
    }
  },
  {
    id: '1018',
    good: {
      id: 1018,
      title: 'Tesla Model Y 行車記錄器',
      pic_url: 'https://source.unsplash.com/400x400?dashcam,tesla&sig=20',
      brand: 'Tesla',
      category: '汽車配件',
      categoryColor: '#DC2626',
      price: '8900'
    }
  },
  {
    id: '1019',
    good: {
      id: 1019,
      title: 'Garmin Fenix 7 運動手錶',
      pic_url: 'https://source.unsplash.com/400x400?garmin,watch&sig=21',
      brand: 'Garmin',
      category: '穿戴裝置',
      categoryColor: '#059669',
      price: '19900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Fitness Coach',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=fitness'
    }
  },
  {
    id: '1020',
    good: {
      id: 1020,
      title: 'Herman Miller Aeron 人體工學椅',
      pic_url: 'https://source.unsplash.com/400x400?chair,office&sig=22',
      brand: 'Herman Miller',
      category: '家具',
      categoryColor: '#92400E',
      price: '45000'
    }
  },
  {
    id: '1021',
    good: {
      id: 1021,
      title: 'Philips Hue 智慧燈泡組',
      pic_url: 'https://source.unsplash.com/400x400?smart,lights&sig=23',
      brand: 'Philips',
      category: '智慧家電',
      categoryColor: '#7C3AED',
      price: '3290'
    }
  },
  {
    id: '1022',
    good: {
      id: 1022,
      title: 'Anker PowerBank 20000mAh',
      pic_url: 'https://source.unsplash.com/400x400?powerbank,anker&sig=24',
      brand: 'Anker',
      category: '配件',
      categoryColor: '#10B981',
      price: '1590'
    }
  },
  {
    id: '1023',
    good: {
      id: 1023,
      title: 'Corsair 32GB DDR5 記憶體',
      pic_url: 'https://source.unsplash.com/400x400?ram,memory&sig=25',
      brand: 'Corsair',
      category: '電腦配件',
      categoryColor: '#1F2937',
      price: '7900'
    }
  },
  {
    id: '1024',
    good: {
      id: 1024,
      title: 'Samsung 980 PRO 2TB SSD',
      pic_url: 'https://source.unsplash.com/400x400?ssd,storage&sig=26',
      brand: 'Samsung',
      category: '電腦配件',
      categoryColor: '#1F2937',
      price: '8900'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Tech Builder',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=techbuilder'
    }
  },
  {
    id: '1025',
    good: {
      id: 1025,
      title: 'NVIDIA RTX 4070 顯示卡',
      pic_url: 'https://source.unsplash.com/400x400?graphics,card&sig=27',
      brand: 'NVIDIA',
      category: '電腦配件',
      categoryColor: '#1F2937',
      price: '21900'
    }
  },
  {
    id: '1026',
    good: {
      id: 1026,
      title: 'Xiaomi 小米13 Ultra',
      pic_url: 'https://source.unsplash.com/400x400?xiaomi,phone&sig=28',
      brand: 'Xiaomi',
      category: '手機',
      categoryColor: '#3B82F6',
      price: '36999'
    }
  },
  {
    id: '1027',
    good: {
      id: 1027,
      title: 'JBL Charge 5 藍牙喇叭',
      pic_url: 'https://source.unsplash.com/400x400?jbl,speaker&sig=29',
      brand: 'JBL',
      category: '音響',
      categoryColor: '#F59E0B',
      price: '4990'
    },
    dchain: {
      tbn_url: '/images/phone-search-flowchart.png',
      user_nick: 'Music Lover',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=musiclover'
    }
  },
  {
    id: '1028',
    good: {
      id: 1028,
      title: 'GoPro HERO12 Black 運動攝影機',
      pic_url: 'https://source.unsplash.com/400x400?gopro,action&sig=30',
      brand: 'GoPro',
      category: '相機',
      categoryColor: '#F59E0B',
      price: '16900'
    }
  }
];
