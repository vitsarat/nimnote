const CHUNK_SIZE=900,OVERLAP=120;
const isThai=ch=>{const c=ch.codePointAt(0);return c>=0x0E00&&c<=0x0E7F;};
function _tokenize(text){
  const lower=(text||"").toLowerCase();
  const toks=lower.match(/[a-z0-9\u0E00-\u0E7F]+/g)||[];
  const out=[];
  for(const t of toks){ if(t.length<=1)continue; out.push(t);
    if([...t].some(isThai)&&t.length>=2){ for(let i=0;i<t.length-1;i++)out.push(t.slice(i,i+2)); } }
  return out;
}
function chunkText(text){text=(text||"").trim();if(!text)return[];const ch=[];let s=0,i=0;while(s<text.length){let e=Math.min(s+CHUNK_SIZE,text.length);ch.push({cid:"x",idx:i++,text:text.slice(s,e)});if(e===text.length)break;s=e-OVERLAP;}return ch;}
function retrieve(nb,query,topK=5){const chunks=[];for(const s of(nb.sources||[]))for(const c of(s.chunks||[]))chunks.push([s,c]);if(!chunks.length)return[];const n=chunks.length;const df={};for(const[_,c]of chunks)for(const t of new Set(_tokenize(c.text)))df[t]=(df[t]||0)+1;const qterms=_tokenize(query);const scored=[];for(const[s,c]of chunks){const tf={};for(const t of _tokenize(c.text))tf[t]=(tf[t]||0)+1;let sc=0;for(const qt of qterms){if(qt in tf){const idf=Math.log((n+1)/(df[qt]+1))+1;sc+=tf[qt]*idf;}}if(sc>0)scored.push([sc,s,c]);}scored.sort((a,b)=>b[0]-a[0]);return scored.slice(0,topK).map(([sc,s,c])=>({source:s.title,score:sc}));}

const tk=_tokenize("โลหะมีค่า"); console.log("TH tokenize:",tk);
const nb={sources:[{title:"Doc1",content:"Gold recovers from PCB at 200-300 g/t.",chunks:chunkText("Gold recovers from PCB at 200-300 g/t.")},{title:"Doc2",content:"Silver is also present.",chunks:chunkText("Silver is also present.")}]};
console.log("EN 'gold':",retrieve(nb,"gold").map(r=>r.source+":"+r.score.toFixed(2)));
const nb2={sources:[{title:"ไทย1",content:"ทองคำ recovered จาก PCB ที่ 200-300 กรัมต่อตัน",chunks:chunkText("ทองคำ recovered จาก PCB ที่ 200-300 กรัมต่อตัน")},{title:"ไทย2",content:"เงินก็มีในแผงวงจร",chunks:chunkText("เงินก็มีในแผงวงจร")}]};
console.log("TH 'โลหะมีค่า':",retrieve(nb2,"โลหะมีค่า").map(r=>r.source+":"+r.score.toFixed(2)));
console.log("ALL JS CORE OK");
