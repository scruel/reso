import { Thread } from '@/types/product';

export const mockThreads: Thread[] = [
  {
    id: '1',
    good: {
      id: 1,
      title: 'Apple iPhone 15 Pro Max 256GB',
      pic_url: 'https://source.unsplash.com/random/400x400?sig=1',
      brand: 'Apple',
      category: '手機',
      categoryColor: '#3B82F6',
      price: '429.90'
    },
    dchain: {
      tbn_url: 'https://source.unsplash.com/600x300?phone,workflow&sig=flow1',
      user_nick: 'TechReviewer Alex',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=alex'
    }
  },
  {
    id: '2',
    good: {
      id: 2,
      title: 'Keychron K8 機械鍵盤',
      pic_url: 'https://source.unsplash.com/random/400x400?sig=2',
      brand: 'Keychron',
      category: '配件',
      categoryColor: '#10B981',
      price: '29.90'
    },
    // 沒有 dchain - 此產品不顯示流程圖
  },
  {
    id: '3',
    good: {
      id: 3,
      title: 'Sony WH-1000XM5',
      pic_url: 'https://source.unsplash.com/random/400x400?sig=3',
      brand: 'Sony',
      category: '耳機',
      categoryColor: '#8B5CF6',
      price: '89.90'
    },
    dchain: {
      tbn_url: 'https://source.unsplash.com/600x300?headphones,review&sig=flow2',
      user_nick: 'AudioExpert Sarah',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=sarah'
    }
  },
  {
    id: '4',
    good: {
      id: 4,
      title: 'Samsung Galaxy S24 Ultra 1TB',
      pic_url: 'https://images.samsung.com/is/image/samsung/p6pim/ph/sm-s928bzgcphl/gallery/ph-galaxy-s24-ultra-s928-sm-s928bzgcphl-thumb-539711237',
      brand: 'Samsung',
      category: '電子產品',
      categoryColor: '#3B82F6',
      price: '330.67'
    },
    // 沒有 dchain
  },
  {
    id: '5',
    good: {
      id: 5,
      title: 'Sony WH-1000XM5 無線降噪耳機',
      pic_url: 'https://m.media-amazon.com/images/I/61KPF+Zxj-L._AC_SL1500_.jpg',
      brand: 'Sony',
      category: '電子產品',
      categoryColor: '#8B5CF6',
      price: '123.07'
    },
    dchain: {
      tbn_url: 'https://source.unsplash.com/600x300?audio,review&sig=flow5',
      user_nick: 'AudioTech Mike',
      user_pic_url: 'https://source.unsplash.com/100x100?avatar&sig=mike'
    }
  }
];
