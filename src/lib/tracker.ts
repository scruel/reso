/* lib/tracker.ts */
import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';

const TRACK_URL = '/api/client-log';
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
  fetch(TRACK_URL, {
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
  queue.push({
    type,
    ts: Date.now(),
    userId: getUserId(),
    url: location.href,
    ua: navigator.userAgent,
    payload,
  });
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