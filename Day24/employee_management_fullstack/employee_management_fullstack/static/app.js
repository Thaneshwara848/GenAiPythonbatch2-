const $ = id => document.getElementById(id);
let employees = [], editingId = null;
const money = n => '₹' + Number(n).toLocaleString('en-IN', {maximumFractionDigits: 0});
async function api(path, options = {}) {
  let response;
  try { response = await fetch(path, {...options, headers: {'Content-Type': 'application/json', ...(options.headers || {})}}); }
  catch { throw new Error('Cannot reach the server. Check that FastAPI is running.'); }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = data.detail;
    throw new Error(typeof detail === 'string' ? detail : Array.isArray(detail) ? detail.map(x => x.msg).join(', ') : `Request failed (${response.status})`);
  }
  return data;
}
function cell(text, className) { const td = document.createElement('td'); if (className) td.className = className; td.textContent = text; return td; }
function render() {
  const term = $('search').value.trim().toLowerCase();
  const visible = employees.filter(e => [e.name,e.email,e.department,e.designation].some(v => String(v).toLowerCase().includes(term)));
  $('total').textContent = employees.length;
  $('active').textContent = employees.filter(e => e.status === 'Active').length;
  $('departments').textContent = new Set(employees.map(e => e.department.toLowerCase())).size;
  $('payroll').textContent = money(employees.reduce((sum,e) => sum+Number(e.salary), 0));
  $('count').textContent = `${visible.length} employee${visible.length===1?'':'s'}`;
  $('tbody').replaceChildren();
  for(const e of visible) {
    const tr = document.createElement('tr');
    const person = document.createElement('td'); const wrap = document.createElement('div'); wrap.className = 'person';
    const avatar = document.createElement('span'); avatar.className = 'avatar'; avatar.textContent = e.name.slice(0,1).toUpperCase();
    const info = document.createElement('div'); const title = document.createElement('strong'); title.textContent = e.name;
    const mail = document.createElement('small'); mail.textContent = e.email; info.append(title,mail); wrap.append(avatar,info); person.append(wrap); tr.append(person);
    tr.append(cell(e.department),cell(e.designation),cell(e.age),cell(money(e.salary)));
    const status = document.createElement('td'); const pill = document.createElement('span'); pill.className = 'pill'+(e.status==='Inactive'?' off':''); pill.textContent=e.status; status.append(pill); tr.append(status);
    const actions=document.createElement('td'); const edit=document.createElement('button'); edit.className='action'; edit.textContent='Edit'; edit.onclick=()=>openModal(e);
    const del=document.createElement('button'); del.className='action delete'; del.textContent='Delete'; del.onclick=()=>removeEmployee(e); actions.append(edit,del); tr.append(actions); $('tbody').append(tr);
  }
  $('feedback').textContent = visible.length ? 'Showing '+visible.length+' of '+employees.length+' employees' : 'No employees found. Add your first employee.';
}
async function load() { try { employees = await api('/api/employees'); render(); } catch(err) {$('feedback').textContent=err.message;} }
function openModal(e=null) {
  editingId=e?.id??null; $('employeeForm').reset(); $('modalTitle').textContent = e?'Edit Employee':'Add Employee';
  if(e) for(const k of ['name','age','email','department','designation','salary','status']) $('employeeForm').elements.namedItem(k).value=e[k];
  $('modal').classList.remove('hidden');
}
function closeModal(){$('modal').classList.add('hidden');}
async function removeEmployee(e){if(!confirm(`Delete ${e.name}? This cannot be undone.`))return;try{await api('/api/employees/'+e.id,{method:'DELETE'});await load();}catch(err){alert(err.message);}}
$('employeeForm').addEventListener('submit',async ev=>{ev.preventDefault();const btn=$('saveBtn');btn.disabled=true;const raw=Object.fromEntries(new FormData(ev.target));const body={...raw,age:Number(raw.age),salary:Number(raw.salary)};
  try{await api(editingId===null?'/api/employees':'/api/employees/'+editingId,{method:editingId===null?'POST':'PUT',body:JSON.stringify(body)});closeModal();await load();}catch(err){alert(err.message);}finally{btn.disabled=false;}});
$('addBtn').onclick=()=>openModal();$('closeModal').onclick=closeModal;$('cancel').onclick=closeModal;$('modal').onclick=e=>{if(e.target===$('modal'))closeModal();};$('search').addEventListener('input',render);
$('chatToggle').onclick=()=>{$('chatWidget').classList.toggle('hidden');if(!$('chatWidget').classList.contains('hidden'))$('chatText').focus();};
$('chatClose').onclick=()=>$('chatWidget').classList.add('hidden');
function appendMessage(text,side){const msg=document.createElement('div');msg.className='message '+side;msg.textContent=text;$('chatMessages').append(msg);$('chatMessages').scrollTop=$('chatMessages').scrollHeight;return msg;}
$('chatForm').addEventListener('submit',async ev=>{ev.preventDefault();const text=$('chatText').value.trim();if(!text)return;$('chatText').value='';appendMessage(text,'user');const pending=appendMessage('Thinking...','bot');const btn=$('chatForm').querySelector('button');btn.disabled=true;
  try{const result=await api('/api/chat',{method:'POST',body:JSON.stringify({message:text})});pending.textContent=result.reply;}catch(err){pending.textContent='Unable to reply: '+err.message;}finally{btn.disabled=false;$('chatMessages').scrollTop=$('chatMessages').scrollHeight;}});
load();
