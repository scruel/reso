import { NextRequest, NextResponse } from 'next/server';

// Mock product list
const products = [
  {
    id: 1,
    title: 'Apple iPhone 15 Pro Max',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=1',
    price: '429.90'
  },
  {
    id: 2,
    title: 'Keychron K8 Mechanical Keyboard',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=2',
    price: '29.90'
  },
  {
    id: 3,
    title: 'Sony WH-1000XM5',
    pic_url: 'https://source.unsplash.com/random/400x400?sig=3',
    price: '89.90'
  }
];

export async function GET(request: NextRequest) {
  return NextResponse.json({
    data: products,
    total: products.length
  });
}
