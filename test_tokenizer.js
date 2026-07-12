// PyThaiNLP-grade tokenizer (approximation): dictionary longest-match + bigram fallback
// Research finding: PyThaiNLP uses dictionary + ML. For offline static page we use
// embedded dictionary longest-match segmentation, falling back to char-bigram for OOV.
const THAI_DICT = new Set((
  // คำทั่วไป
  "และ ใน ที่ ไป จาก กับ ให้ ไม่ ได้ จะ ถ้า แต่ เพราะ ว่า ซึ่ง นี้ นั้น เรา คุณ เขา เธอ ก็ " +
  "ทองคำ โลหะ มีค่า แผงวงจร วงจร โทรศัพท์ มือถือ รีไฟน์ กู้คืน กระบวนการ " +
  "ขยะ อิเล็กทรอนิกส์ เครื่องจักร สกัด ถลุง แร่ หน้าตัก ตัน กรัม " +
  "ความรู้ สมุด บันทึก เอกสาร งานวิจัย ฐานราก ชั้น เชื่อมโยง ประเภท " +
  "คอปเปอร์ ทองแดง เงิน แพลทินัม พาลาเดียม ดีบุก ตะกั่ว " +
  "สูงสุด ปริมาณ ร้อยละ อัตรา ผลิตภัณฑ์ มูลค่า เศรษฐกิจ"
).split(" "));

const isThai = ch => { const c = ch.codePointAt(0); return c >= 0x0E00 && c <= 0x0E7F; };

function segmentThai(run){
  // longest-match from dictionary, fallback to bigram for OOV chars
  const out=[]; let i=0;
  while(i<run.length){
    let matched="", j=i+1;
    while(j<=run.length){
      const cand=run.slice(i,j);
      if(THAI_DICT.has(cand) && cand.length>matched.length) matched=cand;
      j++;
    }
    if(matched){ out.push(matched); i+=matched.length; }
    else {
      // bigram fallback for this single char
      if(i+1<run.length) out.push(run.slice(i,i+2));
      else out.push(run.slice(i,i+1));
      i++;
    }
  }
  return out;
}

function tokenize(text){
  const lower=(text||"").toLowerCase();
  const out=[];
  // split into latin runs vs thai runs by scanning
  let buf="", bufThai=false;
  const flush=()=>{
    if(!buf) return;
    if(bufThai) out.push(...segmentThai(buf));
    else { for(const w of buf.match(/[a-z0-9]+/g)||[]) if(w.length>1) out.push(w); }
    buf="";
  };
  for(const ch of lower){
    const t=isThai(ch);
    if((t&&!bufThai)||(!t&&bufThai)){ flush(); bufThai=t; }
    if(t||/[a-z0-9]/.test(ch)) buf+=ch;
    else { flush(); }
  }
  flush();
  return out;
}

// TESTS
console.log("1. ทองคำ recovered จาก PCB:", tokenize("ทองคำ recovered จาก PCB"));
console.log("2. โลหะมีค่า:", tokenize("โลหะมีค่า"));
const t3=tokenize("ทองคำ recovered จาก PCB ที่ 200-300 กรัมต่อตัน");
console.log("3. has ทองคำ?", t3.includes("ทองคำ"), "| has โลหะ?", t3.includes("โลหะ"), "| has พีซีบี?", t3.includes("pcb"));
console.log("TOKENIZER OK if ทองคำ segmented as one word (not ท อ ง ค ำ)");
