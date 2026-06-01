# ContextCraft — Proje Raporu

**Ders:** BLG106 İnternet Programcılığı  
**Öğrenci:** Efe Recep KARABUDAK  
**Tarih:** 1 Haziran 2026

---

## 1. Projenin Amacı

ContextCraft, yazılımcıların kendi projelerini web arayüzüne yükleyip LlamaIndex ile indeksledikten sonra kısa bir istek (örneğin “login ekranı yap”) yazarak **detaylandırılmış bir prompt** ve **yalnızca gerekli dosya listesini** aldığı bir Flask web platformudur. Sistem bir sohbet uygulaması değildir; kullanıcı burada AI ile konuşmaz. Amaç, Claude veya ChatGPT gibi dış araçlara tüm projeyi yapıştırmak yerine token israfını önlemek ve modele yalnızca işe yarayan bağlamı vermektir. Böylece hem maliyet düşer hem de modelin dikkati dağılmaz.

---

## 2. Mimari Özet

Uygulama **application factory** ve **blueprint** yapısıyla organize edilmiştir: `main` (anasayfa), `auth` (kayıt/giriş), `core` (proje yönetimi). Veritabanında üç model vardır: `User`, `Project`, `PromptLog`. Kullanıcı–proje ilişkisi bire-çok; proje–prompt geçmişi de bire-çoktur.

Ana akış şöyledir:

```
Kayıt/Giriş → Proje oluştur + dosya yükle → İndeksle (LlamaIndex)
    → Prompt yaz → Retrieve + DeepSeek → Detaylı prompt + dosya listesi
    → Kullanıcı metni Claude/ChatGPT'ye yapıştırır
```

**Klasör yapısı (özet):**


| Katman      | Dosya / klasör                       | Görev                            |
| ----------- | ------------------------------------ | -------------------------------- |
| Web         | `app/core/routes.py`                 | Proje CRUD, indeksleme, optimize |
| Auth        | `app/auth/`                          | Flask-Login, hash'li şifre       |
| İndeks      | `app/services/llamaindex_service.py` | Hibrit retrieve (vektör + BM25)  |
| Prompt      | `app/services/prompt_optimizer.py`   | DeepSeek orkestrasyonu           |
| API         | `app/services/openrouter.py`         | OpenRouter istemcisi             |
| Kalıcı veri | `uploads/`, `storage/`               | Dosyalar ve indeks               |


Tüm AI istekleri **OpenRouter API** üzerinden gider; yerel model indirilmez. Production ortamında `docker compose up` ile Gunicorn + PostgreSQL çalıştırılır.

---

## 3. Vibe Coding Deneyimim

Bu projede geleneksel “satır satır kod yazma” yerine **niyet bildir → planı oku → onayla → küçük adımda kodla → test et → commit at** döngüsünü uyguladım. Cursor Composer/Agent modunda çalıştım. En verimli olduğum anlar, fazları (Faz 4 dosya yükleme, Faz 5 indeksleme, Faz 6 prompt motoru, Faz 9 UI) ayrı oturumlara böldüğüm zamanlardı.

Zorlandığım noktalar: (1) Ajanın bazen onaysız teknoloji eklemeye çalışması (HuggingFace embedding, sadece ZIP yükleme), (2) kütüphane sürüm uyumsuzlukları (Werkzeug scrypt, LlamaIndex sürümü), (3) API anahtarı ve model slug formatlarının birbiriyle çelişmesi. Bu sorunları yalnızca plan aşamasında sorgulayarak ve canlı test ederek çözdüm. “AI yazdı, bitti” demek mümkün değildi; her adımda kodu okumak ve tarayıcıda denemek şarttı.

Özellikle Faz 5–6’da indeksleme ve prompt motoru birbirine bağlı olduğu için küçük bir `.env` hatası tüm akışı durduruyordu. Bu yüzden her oturum sonunda `docs/ai-gunlugu.md` dosyasına ne denediğimi, neyin işe yaradığını yazdım; bir sonraki oturumda bağlam kaybını önledi.

---

## 4. Cursor'da En Faydalı Bulduğum İki Özellik

**1) Plan modu ve adım adım onay:** Büyük bir görevi (“Faz 9 UI’ı yap”) tek seferde değil, 9.1 Bootstrap, 9.2 şablonlar, 9.3 model… şeklinde parçalara ayırdım. Her parça için önce plan gösterildi, onayladıktan sonra kod yazıldı. Bu, hocanın PDF’indeki “küçük adımlarla ilerle” ve “planı mutlaka oku” maddelerine doğrudan uyuyor.

**2) Proje bağlamı + terminal testi:** Cursor, `cursor.md` rehberini ve mevcut dosyaları okuyarak tutarlı kod üretti. Hata ayıklarken terminal çıktısını ve tarayıcı davranışını birlikte yorumlamak, özellikle indeksleme ve OpenRouter 401 hatalarında çok zaman kazandırdı.

*(Not: Ders dokümanında Antigravity örnek verilmiştir; ben geliştirmeyi Cursor IDE üzerinde yaptım. İş akışı aynıdır: plan, onay, test, belgeleme.)*

---

## 5. Yakalayıp Düzelttiğim Üç Kritik Hata

**1) macOS Python 3.9 + scrypt hash:** Kayıt sırasında Werkzeug 3 varsayılan `scrypt` algoritması LibreSSL ortamında çalışmadı. Ajanın ürettiği kodu test edince patladı. `User.set_password()` içinde `pbkdf2:sha256` kullanımına geçerek düzelttim.

**2) Embedding model adı uyumsuzluğu:** `.env` dosyasında `openai/text-embedding-3-small` yazılıyken LlamaIndex yalnızca `text-embedding-3-small` slug'ını kabul ediyordu; indeksleme hiç başlamıyordu. `_normalize_embedding_model()` ile prefix temizlendi.

**3) Prompt sonucunda tüm dosyaların seçilmesi:** “Login ekranı yap” gibi isteklerde retrieve aynı dosyadan çok parça döndürüyor, DeepSeek de gereksiz yere birçok dosyayı `required_files` olarak listeliyordu. Dosya çeşitliliği sınırı, anahtar kelime skorlaması ve `required_files` üst sınırı eklenerek yalnızca alakalı dosyalar (ör. `all_in_one_auth.py`) önerilir hale getirildi.

---

## 6. AI Olmadan Tahmini Süre

Flask iskeleti, auth, proje yükleme ve formlar için yaklaşık **1–1,5 hafta**; LlamaIndex indeksleme, hibrit retrieve ve OpenRouter entegrasyonu için **2 hafta**; prompt optimizasyonu ve arayüz için **1 hafta**; test, Docker ve teslim dokümantasyonu için **3–4 gün** ayırdım. Toplam **4–5 hafta** sürerdi.

AI ile oturumlar Mayıs boyunca yürüdü; planlama ve tekrarlayan CRUD kodları hızlandı. Buna rağmen mimari kararlar, API güvenliği, hata ayıklama ve testlerin büyük kısmı bende kaldı. AI süreyi yaklaşık **%40–50** kısalttı; kalite ve anlayış için manuel test ve sorgulama vazgeçilmezdi.

---

## 7. Sonraki Adım

Projeyi sürdürürsem şu geliştirmeleri önceliklendirirdim:

1. **Opsiyonel reranking** — `RERANK_ENABLED` şu an kapalı; açılırsa retrieve isabeti artabilir.
2. **Prompt geçmişi UI** — `PromptLog` veritabanına kaydediliyor; detay sayfasında geçmiş var, tam ekran görüntüleme eklenebilir.
3. **Canlı deploy** — Docker altyapısı hazır; buluta (Railway/Render) taşınabilir.
4. **ZIP içeriği otomatik açma** — Kısmen var; daha büyük monorepo projelerinde alt klasör desteği genişletilebilir.

ContextCraft, “AI ile kod yazmak” değil “AI ile **doğru bağlamı seçip** dış araçlara taşımak” fikrini somutlaştırıyor. Bu yönüyle dersin vibe coding hedefleriyle örtüşüyor. GitHub deposu public yapıldı; AI günlüğü ekran görüntüleriyle tamamlandı. Demo videosu README'ye eklenecektir.