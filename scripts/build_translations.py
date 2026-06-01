#!/usr/bin/env python3
"""messages.pot birleştirme, EN çevirileri ve pybabel compile."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "app" / "templates"
POT_FILE = ROOT / "messages.pot"
TRANSLATIONS = ROOT / "translations"

JINJA_PATTERN = re.compile(
    r"_\(\s*['\"]((?:\\.|[^'\"\\])*)['\"]"
)

EN_TRANSLATIONS = {
    "Kullanıcı Adı": "Username",
    "Kullanıcı adı zorunludur.": "Username is required.",
    "E-posta": "Email",
    "E-posta zorunludur.": "Email is required.",
    "Geçerli bir e-posta girin.": "Enter a valid email address.",
    "Şifre": "Password",
    "Şifre zorunludur.": "Password is required.",
    "Şifre en az 6 karakter olmalıdır.": "Password must be at least 6 characters.",
    "Şifre Tekrar": "Confirm Password",
    "Şifre tekrarı zorunludur.": "Password confirmation is required.",
    "Şifreler eşleşmiyor.": "Passwords do not match.",
    "Kayıt Ol": "Sign Up",
    "Bu e-posta adresi zaten kayıtlı.": "This email is already registered.",
    "Bu kullanıcı adı zaten alınmış.": "This username is already taken.",
    "Beni hatırla": "Remember me",
    "Giriş Yap": "Log In",
    "Hakkımda": "About Me",
    "Bio en fazla 256 karakter olabilir.": "Bio can be at most 256 characters.",
    "Profili Kaydet": "Save Profile",
    "Avatar": "Avatar",
    "Avatar dosyası seçmelisiniz.": "You must select an avatar file.",
    "Geçersiz format. İzin verilen: png, jpg, jpeg, gif, webp.": "Invalid format. Allowed: png, jpg, jpeg, gif, webp.",
    "Avatar Yükle": "Upload Avatar",
    "Avatar dosyası en fazla 2 MB olabilir.": "Avatar file can be at most 2 MB.",
    "Kayıt başarılı! Giriş yapabilirsiniz.": "Registration successful! You can log in.",
    "E-posta veya şifre hatalı.": "Incorrect email or password.",
    "Hoş geldiniz, %(username)s!": "Welcome, %(username)s!",
    "Başarıyla çıkış yaptınız.": "You have logged out successfully.",
    "Profiliniz güncellendi.": "Your profile has been updated.",
    "Avatar yüklendi.": "Avatar uploaded.",
    "Avatar kaldırıldı.": "Avatar removed.",
    "Proje Adı": "Project Name",
    "Proje adı zorunludur.": "Project name is required.",
    "Proje adı en fazla 128 karakter olabilir.": "Project name can be at most 128 characters.",
    "Açıklama": "Description",
    "Açıklama en fazla 512 karakter olabilir.": "Description can be at most 512 characters.",
    "Proje Dosyaları": "Project Files",
    "Proje Oluştur": "Create Project",
    "En az bir dosya yüklemelisiniz.": "You must upload at least one file.",
    "Boş dosya yüklenemez.": "Empty files cannot be uploaded.",
    "İzin verilmeyen dosya türü: %(filename)s": "File type not allowed: %(filename)s",
    "Prompt": "Prompt",
    "Prompt metni zorunludur.": "Prompt text is required.",
    "Prompt 3 ile 2000 karakter arasında olmalıdır.": "Prompt must be between 3 and 2000 characters.",
    "Prompt Oluştur": "Generate Prompt",
    "'%(name)s' projesi başarıyla oluşturuldu.": "Project '%(name)s' was created successfully.",
    "Dosyalar kaydedilirken bir hata oluştu.": "An error occurred while saving files.",
    "Prompt oluşturmak için önce projeyi indeksleyin.": "Index the project before generating a prompt.",
    "Prompt başarıyla oluşturuldu.": "Prompt generated successfully.",
    "Prompt oluşturma hatası: %(error)s": "Prompt generation error: %(error)s",
    "İndekslenecek dosya bulunamadı.": "No files found to index.",
    "İndeksleme zaten devam ediyor.": "Indexing is already in progress.",
    "'%(name)s' indekslendi (%(count)s parça).": "'%(name)s' indexed (%(count)s chunks).",
    "İndeksleme hatası: %(error)s": "Indexing error: %(error)s",
    "'%(name)s' projesi silindi.": "Project '%(name)s' was deleted.",
    "Geçersiz avatar formatı. İzin verilen: png, jpg, jpeg, gif, webp.": "Invalid avatar format. Allowed: png, jpg, jpeg, gif, webp.",
    "Geçersiz dosya yolu: %(path)s": "Invalid file path: %(path)s",
    "Menüyü aç/kapat": "Toggle menu",
    "Projelerim": "My Projects",
    "%(username)s avatar": "%(username)s avatar",
    "Profil": "Profile",
    "Çıkış": "Log Out",
    "Giriş": "Log In",
    "Kapat": "Close",
    "Anasayfa": "Home",
    "Yazılım projelerinizi yükleyin, LlamaIndex ile bağlamı optimize edin ve token israfını önleyin.": "Upload your software projects, optimize context with LlamaIndex, and reduce token waste.",
    "Merhaba, %(username)s!": "Hello, %(username)s!",
    "Projelerime Git": "Go to My Projects",
    "Proje Yükle": "Upload Project",
    "Python, HTML, JS veya ZIP dosyalarınızı yükleyin. ContextCraft projenizi analiz etmeye hazır hale getirir.": "Upload your Python, HTML, JS, or ZIP files. ContextCraft prepares your project for analysis.",
    "İndeksle": "Index",
    "LlamaIndex hibrit arama ile kod parçalarını indeksler. Vektör + BM25 ile en alakalı dosyalar bulunur.": "LlamaIndex indexes code chunks with hybrid search. Vector + BM25 finds the most relevant files.",
    "Kısa isteğinizi yazın; sistem detaylandırılmış prompt ve yalnızca gerekli dosyaları üretir. Claude'a yapıştırın.": "Write a short request; the system produces a detailed prompt and only the necessary files. Paste into Claude.",
    "Hesabınız yok mu?": "Don't have an account?",
    "Kayıt olun": "Sign up",
    "Zaten hesabınız var mı?": "Already have an account?",
    "Giriş yapın": "Log in",
    "Profilim": "My Profile",
    "Hesap bilgilerinizi ve avatarınızı yönetin": "Manage your account details and avatar",
    "Üyelik:": "Member since:",
    "Proje sayısı:": "Project count:",
    "Kendinizi kısaca tanıtın…": "Introduce yourself briefly…",
    "Profil fotoğrafınız navbar'da görünür.": "Your profile photo appears in the navbar.",
    "png, jpg, jpeg, gif veya webp — en fazla 2 MB": "png, jpg, jpeg, gif, or webp — max 2 MB",
    "Avatarı Kaldır": "Remove Avatar",
    "Profil fotoğrafınız kaldırılacak. Devam etmek istiyor musunuz?": "Your profile photo will be removed. Do you want to continue?",
    "İptal": "Cancel",
    "Kaldır": "Remove",
    "Yeni Proje": "New Project",
    "Toplam %(total)s proje": "Total %(total)s projects",
    "Sayfa %(page)s / %(pages)s": "Page %(page)s / %(pages)s",
    "Açıklama yok": "No description",
    "Detaya Git": "View Details",
    "Proje sayfaları": "Project pages",
    "Önceki": "Previous",
    "Sonraki": "Next",
    "Henüz projeniz yok.": "You don't have any projects yet.",
    "İlk Projenizi Oluşturun": "Create Your First Project",
    "Yeni Proje Oluştur": "Create New Project",
    "Birden fazla dosya seçebilirsiniz (.py, .html, .js, .css, .zip vb.)": "You can select multiple files (.py, .html, .js, .css, .zip, etc.)",
    "Oluşturulma": "Created",
    "Dosya sayısı": "File count",
    "Yüklenen Dosyalar": "Uploaded Files",
    "Bu projede henüz dosya bulunmuyor.": "This project has no files yet.",
    "Kısa bir istek yazın; sistem bunu detaylandırılmış prompt ve gerekli dosya listesine çevirir.": "Write a short request; the system turns it into a detailed prompt and a required file list.",
    "Örn: Login ekranı kodla": "e.g. Build a login screen",
    "%(retrieved)s kod parçası incelendi · %(total)s dosyadan %(required)s tanesi yeterli": "%(retrieved)s code chunks reviewed · %(required)s of %(total)s files are sufficient",
    "Detaylandırılmış Prompt": "Detailed Prompt",
    "Bu metni Claude veya ChatGPT'ye yapıştırın.": "Paste this text into Claude or ChatGPT.",
    "Kopyala": "Copy",
    "Kopyalandı!": "Copied!",
    "Gerekli Dosyalar": "Required Files",
    "Dosya önerisi üretilemedi.": "No file suggestions were generated.",
    "Açıklama üretilemedi.": "No explanation was generated.",
    "Prompt Geçmişi": "Prompt History",
    "Proje listesi": "Project list",
    "Yeniden İndeksle": "Re-index",
    "Bu projeyi silmek istediğinize emin misiniz?": "Are you sure you want to delete this project?",
    "Projeyi Sil": "Delete Project",
    "Sunucu Hatası": "Server Error",
    "Bir şeyler ters gitti": "Something went wrong",
    "Sunucuda beklenmeyen bir hata oluştu. Lütfen bir süre sonra tekrar deneyin.": "An unexpected server error occurred. Please try again later.",
    "Sayfa Bulunamadı": "Page Not Found",
    "Sayfa bulunamadı": "Page not found",
    "Aradığınız sayfa mevcut değil, taşınmış veya silinmiş olabilir.": "The page you are looking for does not exist, may have moved, or was deleted.",
}


def extract_jinja_strings() -> set[str]:
    strings: set[str] = set()
    for path in TEMPLATES.rglob("*.html"):
        content = path.read_text(encoding="utf-8")
        for match in JINJA_PATTERN.finditer(content):
            value = match.group(1).replace("\\'", "'").replace('\\"', '"')
            strings.add(value)
    return strings


def read_pot_msgids(pot_path: Path) -> set[str]:
    msgids: set[str] = set()
    for line in pot_path.read_text(encoding="utf-8").splitlines():
        if line.startswith('msgid "') and line != 'msgid ""':
            msgids.add(line[7:-1])
    return msgids


def append_missing_to_pot(pot_path: Path, strings: set[str]) -> None:
    existing = read_pot_msgids(pot_path)
    missing = sorted(strings - existing)
    if not missing:
        return
    with pot_path.open("a", encoding="utf-8") as handle:
        for message in missing:
            handle.write(f"\n#: app/templates\nmsgid \"{message}\"\nmsgstr \"\"\n")


def read_po_string(lines: list[str], idx: int, kind: str) -> tuple[str, int]:
    header = lines[idx]
    prefix = f"{kind} "
    if not header.startswith(prefix):
        raise ValueError(f"Expected {kind} at line {idx + 1}")
    rest = header[len(prefix):]
    if rest == '""':
        idx += 1
        parts: list[str] = []
        while idx < len(lines) and lines[idx].startswith('"') and lines[idx].endswith('"'):
            parts.append(lines[idx][1:-1])
            idx += 1
        return "".join(parts), idx
    if rest.startswith('"') and rest.endswith('"'):
        return rest[1:-1], idx + 1
    raise ValueError(f"Malformed {kind} at line {idx + 1}")


def write_po_string(kind: str, text: str) -> list[str]:
    escaped = text.replace("\\", "\\\\").replace('"', '\\"')
    if len(escaped) <= 77:
        return [f'{kind} "{escaped}"']
    lines = [f'{kind} ""']
    for start in range(0, len(escaped), 77):
        lines.append(f'"{escaped[start:start + 77]}"')
    return lines


def apply_en_translations(po_path: Path) -> None:
    lines = po_path.read_text(encoding="utf-8").splitlines()
    out: list[str] = []
    i = 0
    while i < len(lines):
        if lines[i].startswith("msgid"):
            msgid_start = i
            msgid, after_msgid = read_po_string(lines, i, "msgid")
            if after_msgid < len(lines) and lines[after_msgid].startswith("msgstr"):
                _, after_msgstr = read_po_string(lines, after_msgid, "msgstr")
                if msgid and msgid in EN_TRANSLATIONS:
                    out.extend(lines[msgid_start:after_msgid])
                    out.extend(write_po_string("msgstr", EN_TRANSLATIONS[msgid]))
                    i = after_msgstr
                    continue
                out.extend(lines[msgid_start:after_msgstr])
                i = after_msgstr
                continue
        out.append(lines[i])
        i += 1
    po_path.write_text("\n".join(out) + "\n", encoding="utf-8")


def run_pybabel(args: list[str]) -> None:
    subprocess.run(["pybabel", *args], cwd=ROOT, check=True)


def main() -> int:
    run_pybabel([
        "extract",
        "-F", "babel_py.cfg",
        "-k", "_l",
        "-k", "_",
        "-o", "messages.pot",
        ".",
        "--ignore=venv",
        "--ignore=scripts",
    ])

    jinja_strings = extract_jinja_strings()
    append_missing_to_pot(POT_FILE, jinja_strings)

    for locale in ("tr", "en"):
        po_path = TRANSLATIONS / locale / "LC_MESSAGES" / "messages.po"
        if not po_path.exists():
            run_pybabel(["init", "-i", "messages.pot", "-d", "translations", "-l", locale])
    run_pybabel(["update", "-i", "messages.pot", "-d", "translations"])

    apply_en_translations(TRANSLATIONS / "en" / "LC_MESSAGES" / "messages.po")
    run_pybabel(["compile", "-d", "translations"])
    print("Translations built successfully.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
