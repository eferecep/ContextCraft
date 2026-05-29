## Oturum 1 - 22 Mayıs 2026 15:00-15:30

### Hedef

Projenin temel iskeletini, Application Factory ve Blueprint mimarisine uygun olarak kurmak.

### Kullandığım Mod ve Model

Mod: Plan (Cursor Composer)
Model: Claude 3.5 Sonnet
Görünüm: Manager / Composer Modu

### Verdiğim Promptlar

1. **İskelet Kurulum Promptu:**

> Bağlam: Meslek Yüksek Okulu öğrencisiyim, İnternet Programcılığı dersi için Flask 3.x ile bir web uygulaması geliştireceğim. Konum: Yazılımcılar için projelerini yükleyip LlamaIndex ile bağlamı optimize ederek token israfını önleyen bir asistan platformu.
> Hedef: Application factory pattern kullanan, blueprint'lere (main, auth, core) ayrılmış, temiz bir proje iskeleti kur.
> Kısıtlar: Flask 3.x sürümünü kullan. Gerekli paketler: flask, flask-sqlalchemy, flask-migrate, flask-login, flask-wtf, python-dotenv, llama-index, werkzeug. .env dosyasını .gitignore'a ekle. Plan modunda ilerle.

### Ajanın Önerdiği Plan

Ajan bana `app/__init__.py` içinde factory pattern kullanan ve rotaları blueprintlere bölen bir klasör ağacı sundu.

Oturum 1 Planı

### Plan'da Sorguladıklarım ve Onayladıklarım

Cursor'ın Composer özelliğini plan modunda kullanarak proje iskeletini istedim. Ajanın sunduğu planda `extensions.py` dosyası ile eklentilerin ayrılması ve `app/__init__.py` içindeki `create_app()` fonksiyonunun temiz tutulması mimari açıdan doğruydu. Ayrıca `.env` dosyasının `.gitignore` içinde açıkça belirtildiğini doğruladım, bu sayede güvenlik cezasından kurtulmuş oldum. Planı olduğu gibi onayladım.

### Üretilen Kodda Düzelttiklerim

- İlk kurulum olduğu için koda manuel müdahale etmedim, tasarlanan klasör ve dosya yapısı kusursuzdu.

### Karşılaştığım Hatalar ve Çözümler

- Hata: Herhangi bir hata ile karşılaşmadım.
- Çözüm: Uygulanamaz.

### Bu Oturumdan Öğrendiğim

Büyük projelerde yapay zekaya doğrudan "bana proje yaz" demek yerine, sadece klasör iskeleti istemenin ve blueprint'leri baştan planlamanın projenin temelini ne kadar sağlam attığını gördüm. `.gitignore` gibi dosyaların başlangıçta ayarlanması sonradan yaşanacak sızıntıları önlüyor.

### Sonraki Oturum İçin Notlar

Veritabanı modellerini (User ve Project) SQLAlchemy 2.x stiliyle kurgulamaya başlayacağım.  

## Oturum 2 - 25 Mayıs 2026  18.45

### Hedef

Projenin "Faz 4" aşamasına geçerek, çoklu dosya yükleme altyapısını kurmak ve "ProjectForm" hazırlıklarına başlamak. [cite_start]Süreci tamamen küçük adımlara bölerek ilerletmek[cite: 91].  

### Kullandığım Mod ve Model

Mod: Plan (Cursor Composer)  
Model: [Kullandığın Modeli Yaz, örn: Claude 3.5 Sonnet]  
Görünüm: Manager / Composer Modu  

### Verdiğim Promptlar

1. "Faz 4 ü adım adım planlayarak yapmaya başla her adımı benden onay almadan yapma."
2. "Sadece zip koyma zorunluluğu olmasın normal dosya da yüklensin. proje 16 mb den büyük olabilir. Hocanın dökümanın kurallarının dışına çıkmadığına emin ol. bu değişikleri yaptıktan sonra 4.1'i kodla."

### Ajanın Önerdiği Plan

[cite_start]Ajan, karmaşık bir görevi 6 ayrı adıma bölen çok iyi bir plan sundu ve herhangi bir kod yazmadan önce planını paylaştı[cite: 74]. Ancak Adım 4.1 için sunduğu detaylarda, projenin sadece `.zip` dosyası kabul etmesini ve 16 MB ile sınırlanmasını önerdi.   

[cite_start]*[Buraya Ajanın Adım 4.1 planını sunduğu ekran görüntüsünü ekle: docs/img/oturum-N-faz4-plan.png]* [cite: 79]  

### Plan'da Sorguladıklarım ve Onayladıklarım

[cite_start]Plan modunda ajanın sunduğu varsayılan sınırlandırmaları (sadece zip ve 16 MB sınırı) hemen fark ettim ve onaylamadım[cite: 101, 106]. [cite_start]Projenin dinamiklerine göre normal dosyaların da (py, html, js vb.) tek tek yüklenebilmesi gerektiğini ve dosya boyutu sınırının daha esnek olması gerektiğini belirterek planı revize etmesini emrettim[cite: 127, 128]. [cite_start]Ayrıca ajana, hocanın dokümanındaki geliştirme kurallarına sadık kalması kısıtını tekrar hatırlattım[cite: 128].  

### Üretilen Kodda Düzelttiklerim

- Ajan verdiğim yönlendirme sonrası kodları üretti. `werkzeug.utils.secure_filename` kullanımını ve path traversal (../) engelleme mantığını inceledim; doğru kurulduğu için manuel bir müdahale yapmadım.  
- [cite_start]`.env.example` dosyasına opsiyonel olarak `MAX_CONTENT_LENGTH` eklendiğini teyit ettim[cite: 57].

### Karşılaştığım Hatalar ve Çözümler

- [cite_start]**Hata:** Ajan, yükleme altyapısını tasarlarken inisiyatif alıp konsepti sadece `.zip` formatına indirgeyerek varsayılan, kısıtlayıcı bir mimari dayatmaya çalıştı[cite: 103].  
- [cite_start]**Çözüm:** Ajanın "onay bekleme" aşamasında araya girip, hedeflerime uygun olmayan bu kısıtları net kısıtlamalar ve yönlendirmeler içeren bir prompt ile düzelttirdim[cite: 106, 128].

### Bu Oturumdan Öğrendiğim

[cite_start]"Tüm sistemi kur" demek yerine, sadece tek bir fazı bile 6 küçük adıma böldürerek ilerlemenin ne kadar hayati olduğunu gördüm[cite: 93, 94, 96]. [cite_start]Ajanı onay mekanizmasıyla frenlemeseydim, projeye tüm dosyaları .zip yapmayı zorunlu kılan yanlış bir iş mantığı yerleşecekti[cite: 88, 120]. [cite_start]Kötü mimariyi kod yazılmadan planda yakalayıp düzeltmek, sonradan kodu refaktör etmekten çok daha güvenli[cite: 100].  

### Sonraki Oturum İçin Notlar

[cite_start]Adım 4.2'deki `ProjectForm` yapısı (çoklu dosya yükleme - MultipleFileField) Flask-WTF üzerinden inşa edilecek ve test edilecek[cite: 97, 193]. [cite_start]CSRF token korumasının aktif olup olmadığına özellikle dikkat edilecek[cite: 205].  
  
## Oturum 3 - 25 Mayıs 2026 19:00-19:45

### Hedef

Sistem akışında LlamaIndex'in tam olarak nerede ve nasıl çalışacağını netleştirmek; ajanın başıma buyruk kararlar almasını engelleyerek API anahtarları için güvenli (.env tabanlı) bir altyapı kurmak.

### Kullandığım Mod ve Model

Mod: Plan (Cursor Composer)

Model: Claude 3.5 Sonnet

Görünüm: Manager / Composer Modu

### Verdiğim Promptlar

1. "llamaindex aşaması nerede gerçekleşiyor tam olarak sistem akışında göremedim ? ayrıca bana sormadan ai koyma bir daha. Api key kısmı oluştur benim doldurmamı beklesin ve api key kısmını git huba yüklenmeyecek şekilde ayarla."

### Ajanın Önerdiği Plan

Ajan hatasını kabul etti ve sistem akışını netleştiren 3 aşamalı yeni bir plan sundu. Faz 4'te dosya yükleme, Faz 5'te LlamaIndex ile indeksleme ve Faz 6'da DeepSeek ile retrieve (getirme) işlemlerinin yapılacağını haritalandırdı. Ayrıca `.env` ve `.env.example` dosyalarını oluşturarak API yönetimi planını sundu.

*[Buraya Ajanın Faz 4-5-6 mimarisini açıkladığı tablonun veya açıklamanın ekran görüntüsünü ekle: docs/img/oturum-3-mimari-akis.png]*

### Plan'da Sorguladıklarım

Ajanın bir önceki aşamada bana sormadan ve onayımı almadan inisiyatif kullanarak plana HuggingFace embedding'ini dahil etmesini sert bir şekilde sorguladım. Projenin mimarı benim ve benim onayım olmadan sisteme yeni bir teknoloji veya AI modeli dahil edilemez. Ayrıca API anahtarlarının doğrudan koda gömülme riskine karşı baştan önlem alarak `.env` mimarisini zorunlu koştum.

### Üretilen Kodda Düzelttiklerim

Ajan `.env.example` şablonunu oluşturdu ve `LLAMAINDEX_API_KEY`, `OPENROUTER_API_KEY` gibi değerleri boş bıraktı. Oluşturulan `.env` dosyasının `.gitignore` içinde yer aldığını ve GitHub'a yüklenmeyeceğini teyit ettim. `config.py` içinde de bu değerlerin ortam değişkenlerinden (environment variables) okunduğunu doğruladım.

### Karşılaştığım Hatalar ve Çözümler

- **Hata:** Ajanın otonom davranarak projeye benden habersiz AI modeli/embedding (HuggingFace) entegre etmeye çalışması ve mimari akışı (hangi teknolojinin nerede kullanılacağını) belirsiz bırakması.

- **Çözüm:** Ajana sert bir kısıtlama promptu girerek onaysız AI kullanımını yasakladım. API key altyapısını güvenli hale getirmesini ve sistemin genel akış şemasını (Faz 4-5-6 ilişkisi) bana açıklamasını emrettim.

### Bu Oturumdan Öğrendiğim

Yapay zeka asistanlarının süreci hızlandırmak adına bazen "gereğinden fazla" inisiyatif alabildiğini gördüm. Eğer koda müdahale edip API güvenliğini baştan sağlamasaydım, anahtarlarım GitHub'a sızabilirdi (ki bu projede doğrudan eksi puan sebebi). Ayrıca, LlamaIndex'in sadece indeksleme ve vektör arama kısmında, DeepSeek'in ise yalnızca bulunan metinleri işleme kısmında çalıştığını tam olarak idrak ettim. Ajanı yönetmek, ona sınır çizmektir.

### Sonraki Oturum İçin Notlar

API anahtarlarımı `.env` dosyasına yerleştireceğim. Hangi embedding modelini (OpenRouter vb.) kullanacağıma karar verip, Faz 5'in (LlamaIndex indeksleme ve storage altyapısı) ilk adımı olan Adım 5.1'e onay vereceğim.