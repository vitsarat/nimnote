# nimnote — Research Notes (Project Status)

## สิ่งที่สร้าง
เครื่องมือวิจัยบนเครื่องตัวเอง (offline) ทำงานในสปิริตเดียวกับ `notebooklm-py`
แต่ไม่พึ่ง API ของ Google ที่ไม่เป็นทางการ

## ไฟล์ (D:\ROOM_NOOMNIM\nimnote\)
- pyproject.toml — แพ็กเกจ (entry: `nimnote`)
- nimnote/__init__.py, store.py, ingest.py, ground.py, artifacts.py, llm.py, cli.py, server.py
- examples/quickstart.py — สาธิตเรียกใช้
- tests/test_core.py — ทดสอบ (ผ่าน)
- README.md — คู่มือ EN+ตารางเปรียบเทียบ notebooklm-py

## ทดสอบผ่านแล้ว (ของจริง)
- ✅ pip install -e . สำเร็จ
- ✅ python tests/test_core.py → ALL TESTS PASSED (รวม Thai query)
- ✅ CLI: create notebook → add-text x2 → ask (EN + TH) → generate datatable
   - EN "gold" → เจอ Doc1 score 1.41
   - TH "โลหะมีค่า" → เจอ Doc1 score 11.24 (bigram fallback ทำงาน)
- ✅ quickstart: data table + mindmap + citation index ถูกต้อง

## ฟีเจอร์ที่มี
- ingest: text / file / url
- retrieve: TF-IDF + Thai bigram, citation-aware
- artifacts: datatable (CSV), citation index, mindmap (JSON), report/quiz/flashcards (ต้อง LLM)
- LLM optional: OpenAI-compatible env, offline fallback เขียน prompt ลงไฟล์
- REST server: POST /notebooks, /ask (stdio.localhost)
- store: JSON ใต้ NIMNOTE_HOME ข้ามเซสชัน

## ค้างอยู่
- Office 365 th-th ถอนไม่สุด (winget ช้า/timeout) — รันถอนใน background แล้ว
  ดูสถานะ: cat "$HOME/office_uninstall.log" หรือ winget list | grep "Microsoft 365 Apps"
