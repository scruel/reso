import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';

const TRACK_URL = '/api/client-log';
let queue: any[] = [];
const SESSION_ID = Cookies.get('reso_uuid') || uuidv4();
Cookies.set('reso_uuid', SESSION_ID, { expires: 365 }); // 365 天

const flush = () => {
  if (!queue.length) return;
  fetch(TRACK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(queue),
  }).catch(() => {});
  queue = [];
};

export const log = (type: string, payload?: any) => {
  queue.push({
    type,
    ts: Date.now(),
    uuid: SESSION_ID,
    url: location.href,
    ua: navigator.userAgent,
    payload,
  });
  flush(); // 立即发送 / 可改防抖
};