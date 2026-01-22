import os
import shutil
import subprocess
import re

def run_cmd(cmd):
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    return result

def clean_and_fix_files():
    print("\n🛠️  Naprawiam strukturę plików dla Vercel...")
    os.makedirs("src", exist_ok=True)

    # 1. Naprawa App.tsx - usuwanie nieistniejących importów
    if os.path.exists("App.tsx"):
        with open("App.tsx", "r", encoding="utf-8") as f:
            lines = f.readlines()
        # Usuwamy linie z importami z folderu components, jeśli go nie ma
        if not os.path.exists("components"):
            lines = [line for line in lines if './components/' not in line]
        
        with open("src/App.tsx", "w", encoding="utf-8") as f:
            f.writelines(lines)

    # 2. Przenoszenie kluczowych plików
    for f in ["index.tsx", "types.ts"]:
        if os.path.exists(f):
            shutil.copy2(f, os.path.join("src", f))

    # 3. Naprawa index.html
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            html = f.read()
        html = re.sub(r'<script type="importmap">.*?</script>', '', html, flags=re.DOTALL)
        html = html.replace('src="/index.tsx"', 'src="/src/index.tsx"')
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(html)

    # 4. Pusty CSS, żeby Vercel nie zgłaszał błędu
    if not os.path.exists("index.css"):
        with open("index.css", "w") as f: f.write("/* build fix */")

def handle_git_logic():
    # Pobieramy nazwę aktualnego folderu jako domyślną nazwę repo
    default_name = os.path.basename(os.getcwd())
    
    print(f"\n--- KONFIGURACJA GITHUB ---")
    repo_name = input(f"Podaj nazwę repozytorium (domyślnie: {default_name}): ").strip() or default_name
    
    # Sprawdzamy czy repo już istnieje na Twoim GitHubie
    check_repo = run_cmd(f"gh repo view {repo_name}")
    
    if check_repo.returncode == 0:
        print(f"⚠️  Repozytorium '{repo_name}' już istnieje na GitHub.")
        choice = input("Co chcesz zrobić? [1] Nadpisać (Force Push) | [2] Podać nową nazwę: ")
        
        if choice == "2":
            repo_name = input("Podaj NOWĄ nazwę repozytorium: ").strip()
            return handle_git_logic() # Rekurencja, żeby sprawdzić nową nazwę
    else:
        print(f"✨ Tworzę nowe repozytorium: {repo_name}")

    # Logika Gita
    if not os.path.exists(".git"):
        run_cmd("git init")
        run_cmd("git branch -M main")

    # Próba stworzenia repo (jeśli nie istnieje)
    run_cmd(f"gh repo create {repo_name} --public --source=. --remote=origin")
    
    run_cmd("git add .")
    run_cmd('git commit -m "Automatyczna aktualizacja struktury i kodu"')
    
    print(f"📤 Wysyłam kod do https://github.com/twoj-login/{repo_name}...")
    push_result = run_cmd("git push -u origin main --force")
    
    if push_result.returncode == 0:
        print(f"✅ SUKCES! Kod jest na GitHubie.")
    else:
        print(f"❌ Błąd wysyłki: {push_result.stderr}")

if __name__ == "__main__":
    clean_and_fix_files()
    handle_git_logic()
    print("\n🚀 Proces zakończony. Sprawdź swój panel Vercel!")
