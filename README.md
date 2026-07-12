# nimnote — สมุดความรู้ไทย แบบเชื่อมโยงมีประเภท

> ปรัชญา: การสะสมความรู้ให้มากที่สุด → ได้ทักษะใหม่
> คนส่วนใหญ่วิ่งแข่ง "ปลายทาง" (แชทฉลาดๆ) — แต่โอกาสที่แท้จริงคือ **ฐานรากที่ทุกปลายทางต้องพิง**

## ปัญหาที่มองเห็น (จากวิจัย 2026)
1. คนเบื่อตั้งค่า/overkill (Notion), เบื่อ plugin churn (Obsidian) → อยาก **"พิมพ์เลย"**
2. ภาษาไทยพร้อมในเครื่องมือส่วนใหญ่ → ช่องว่างที่ไม่มีใครทำตลาดไทย
3. ลิงก์ส่วนใหญ่ไร้ความหมาย (Obsidian graph) → Capacities/Tana มี typed relations แต่ **ต้องจ่าย/cloud**

## วิธีแก้ที่เรียบง่าย (nimnote)
- ✅ **พิมพ์เลย** เปิดหน้าเว็บขึ้นมาพิมพ์ได้ทันที ไม่มี onboarding
- ✅ **ตัดคำไทยเกรด PyThaiNLP** (dictionary longest-match + bigram fallback) — ไม่ใช่ bigram งูกๆ
- ✅ **ลิงก์มีประเภท** (support/contradict/related/derived) + ขยายบริบทผ่านกราฟ
- ✅ **ของคุณ 100%** เก็บในเครื่อง (localStorage) ฟรี ไม่ขึ้นคลาวด์ ทำงานบน GitHub Pages ได้

## ทดสอบ
```bash
node test_tokenizer.js   # ทองคำ ต้องตัดเป็นคำเดียว
node test_link.js         # linked memory + graph expand
```

## License
MIT
