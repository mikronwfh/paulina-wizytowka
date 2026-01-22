import os
import shutil
import subprocess
import re

def run(cmd):
    print(f"-> Wykonuję: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.returncode != 0:
        print(f"   Informacja: {result.stderr.strip()}")
    return result.returncode == 0

def clean_and_prepare():
    print("🧹 Porządkuję pliki...")
    
    # Tworzymy folder src, jeśli nie istnieje
    if not os.path.exists("src"):
        os.makedirs("src")

    # Pliki do przeniesienia do src (standard Vite)
    files_to_move = ["App.tsx", "index.tsx", "types.ts"]
    for f in files_to_move:
        if os.path.exists(f):
            # Jeśli plik już jest w src, nadpisujemy go najnowszą wersją
            shutil.move(f, os.path.join("src", f))

    # Naprawa index.html
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            content = f.read()

        # 1. Usuwamy blok <script type="importmap">...</script>
        content = re.sub(r'<script type="importmap">.*?</script>', '', content, flags=re.DOTALL)
        
        # 2. Naprawiamy ścieżkę do skryptu (Vercel musi widzieć /src/index.tsx)
        content = content.replace('src="/index.tsx"', 'src="/src/index.tsx"')
        
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(content)
        print("✅ index.html naprawiony.")

def push_to_git(repo_name):
    print(f"🚀 Wysyłam projekt do repozytorium: {repo_name}")
    
    if not os.path.exists(".git"):
        run("git init")
        run("git branch -M main")

    # Sprawdzamy czy repo na GH istnieje, jeśli nie - tworzymy
    run(f"gh repo create {repo_name} --public --source=. --remote=origin")
    
    run("git add .")
    run('git commit -m "Automatyczna aktualizacja z AI Studio"')
    run("git push -u origin main --force")

if __name__ == "__main__":
    # Możesz tu wpisać na sztywno nazwę swojego repo, żeby nie pytał co chwilę
    repo = "paulina-wizytowka" 
    
    clean_and_prepare()
    push_to_git(repo)
    
    print("\n✨ WSZYSTKO GOTOWE!")
    print(f"Twoja strona na Vercel powinna się teraz sama przebudować.")
