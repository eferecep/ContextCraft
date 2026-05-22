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

![Oturum 1 Planı](img/oturum-1-plan.png)

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
