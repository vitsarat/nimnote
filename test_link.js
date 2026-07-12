// mirror of linked-memory + expand logic from new index.html
function retrieveTest(nb,query,topK=5){
  const chunks=[];for(const s of(nb.sources||[]))for(const c of(s.chunks||[]))chunks.push([s,c]);
  if(!chunks.length)return[];const n=chunks.length,df={};
  for(const[_,c]of chunks)for(const t of new Set(_tokenize(c.text)))df[t]=(df[t]||0)+1;
  const qterms=_tokenize(query),scored=[];
  for(const[s,c]of chunks){const tf={};for(const t of _tokenize(c.text))tf[t]=(tf[t]||0)+1;let sc=0;
    for(const qt of qterms){if(qt in tf){const idf=Math.log((n+1)/(df[qt]+1))+1;sc+=tf[qt]*idf;}}if(sc>0)scored.push([sc,s,c]);}
  scored.sort((a,b)=>b[0]-a[0]);return scored.slice(0,topK).map(([sc,s,c])=>({source:s.title,cid:c.cid}));
}
function expand(nb,seeds){
  const out=[];const seen=new Set(seeds.map(s=>s.cid));
  for(const seed of seeds)for(const l of(nb.links||[])){let other=null;
    if(l.source===seed.cid)other=l.target;else if(l.target===seed.cid)other=l.source;
    if(other&&!seen.has(other)){seen.add(other);
      const src=nb.sources.find(x=>x.cid===other)||nb.notes.find(x=>x.cid===other);
      if(src)out.push({via:'link',relation:l.relation,node:src});}}
  return out;
}
function _tokenize(text){const lower=(text||"").toLowerCase();const toks=lower.match(/[a-z0-9\u0E00-\u0E7F]+/g)||[];const out=[];for(const t of toks){if(t.length<=1)continue;out.push(t);if([...t].some(ch=>{const c=ch.codePointAt(0);return c>=0x0E00&&c<=0x0E7F;})&&t.length>=2){for(let i=0;i<t.length-1;i++)out.push(t.slice(i,i+2));}}return out;}

// scenario: gold PCB doc linked "supports" to a refinery note
const nb={sources:[
  {title:"รายงานทองคำ PCB",cid:"S1",content:"ทองคำ recovered จาก PCB โทรศัพท์ที่ 200-300 กรัมต่อตัน โลหะมีค่าสูงสุด",chunks:[{cid:"S1",text:"ทองคำ recovered จาก PCB โทรศัพท์ที่ 200-300 กรัมต่อตัน โลหะมีค่าสูงสุด"}]},
  {title:"บันทึกโรงงานรีไฟน์",cid:"S2",content:"โรงงานรับรีไฟน์ PCB โทรศัพท์ อัตรากู้คืน 95%",chunks:[{cid:"S2",text:"โรงงานรับรีไฟน์ PCB โทรศัพท์ อัตรากู้คืน 95%"}]}
],notes:[],links:[{id:"L1",source:"S1",relation:"supports",target:"S2"}]};

const hits=retrieveTest(nb,"โลหะมีค่า");
console.log("seed hit:",hits.map(h=>h.source));
const linked=expand(nb,hits);
console.log("expanded via link:",linked.map(l=>l.relation+" -> "+l.node.title));
console.log(linked.length===1 && linked[0].relation==="supports" ? "LINKED MEMORY OK" : "LINKED MEMORY FAIL");
