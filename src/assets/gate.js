const SITE_PASSWORD_HASH='eb8eeb360d0b59563076ac1bef062731b5854b967f4706805f897c2ffc865bd0';
const SITE_SALT='research-hub-salt';
const STORAGE_KEY='research_hub_access';

async function sha256(text){const data=new TextEncoder().encode(text);const hash=await crypto.subtle.digest('SHA-256',data);return Array.from(new Uint8Array(hash)).map(b=>b.toString(16).padStart(2,'0')).join('');}
async function verifyPassword(password){return await sha256(`${SITE_SALT}:${password}`)===SITE_PASSWORD_HASH;}
async function unlock(){const input=document.getElementById('site-password');const error=document.getElementById('gate-error');const ok=await verifyPassword(input.value.trim());if(ok){sessionStorage.setItem(STORAGE_KEY,'ok');document.getElementById('gate').classList.add('hidden');document.getElementById('app').classList.remove('hidden');error.textContent='';}else{error.textContent='סיסמה שגויה';}}
function gateReady(){document.getElementById('unlock-btn')?.addEventListener('click',unlock);document.getElementById('site-password')?.addEventListener('keydown',e=>{if(e.key==='Enter')unlock();});if(sessionStorage.getItem(STORAGE_KEY)==='ok'){document.getElementById('gate')?.classList.add('hidden');document.getElementById('app')?.classList.remove('hidden');}}
document.addEventListener('DOMContentLoaded',gateReady);