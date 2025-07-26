/* lib/tracker.ts */
import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';
import { getApiUrl } from './api';

const TRACK_URL = getApiUrl('/api/client-log');
const SESSION_KEY = 'reso_session';
const FLUSH_IDLE = 5_000; // 5 秒闲置即发送

// 生成或读取 UUID
export const getUserId = () => {
  let id = Cookies.get(SESSION_KEY);
  if (!id) {
    id = uuidv4();
    Cookies.set(SESSION_KEY, id, { expires: 365, sameSite: 'Lax' });
  }
  return id;
};

const queue: any[] = [];
let flushTimer: NodeJS.Timeout;

const send = async () => {
  if (!queue.length) return;
  fetch(getApiUrl('/api/client-log'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(queue.splice(0)),
  }).catch(() => {/* silent */});
};

const scheduleFlush = () => {
  clearTimeout(flushTimer);
  flushTimer = setTimeout(send, FLUSH_IDLE);
};

export const log = (type: string, payload?: any) => {
  const userId = getUserId();
  let message = '';
  
  switch(type) {
    case 'pageview':
      message = `用戶 ${userId} 瀏覽了頁面`;
      break;
    case 'scroll':
      message = `用戶 ${userId} 滾動到 ${payload?.depth || 0}% 位置`;
      break;
    case 'click':
      message = `用戶 ${userId} 點擊了商品 ${payload?.productId || '未知'}`;
      break;
    case 'hover':
      message = `用戶 ${userId} 懸停在商品 ${payload?.productId || '未知'} 上`;
      break;
    case 'search':
      message = `用戶 ${userId} 搜索了 "${payload?.query || '空搜索'}"`;
      break;
    default:
      message = `用戶 ${userId} 執行了 ${type} 操作`;
  }
  
  // 在console中打印用戶操作
  console.log(`📊 ${message}`);
  
  queue.push({ message });
  scheduleFlush();
};

/* 统一初始化 */
export const initTracker = () => {
  // PV
  log('pageview');

  // 滚动深度
  let maxDepth = 0;
  const handleScroll = () => {
    const depth = Math.round(
      ((window.scrollY + window.innerHeight) / document.documentElement.scrollHeight) * 100
    );
    if (depth > maxDepth) {
      maxDepth = depth;
      log('scroll', { depth });
    }
  };
  window.addEventListener('scroll', handleScroll, { passive: true });

  // 点击 / 悬停
  document.addEventListener('click', (e) => {
    const target = e.target as HTMLElement;
    const card = target.closest('[data-product-id]');
    if (card) {
      log('click', { productId: card.getAttribute('data-product-id') });
    }
  });

  document.addEventListener('mouseover', (e) => {
    const card = (e.target as HTMLElement).closest('[data-product-id]');
    if (card && !card.matches('[data-hover-sent]')) {
      card.setAttribute('data-hover-sent', '1');
      log('hover', { productId: card.getAttribute('data-product-id') });
    }
  });

  // search
  document.addEventListener('search-log', ((e: CustomEvent<string>) => {
    log('search', { query: e.detail });
  }) as EventListener);

  // 页面卸载/刷新前补发
  window.addEventListener('beforeunload', send);
};