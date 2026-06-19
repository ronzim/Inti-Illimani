import os
import sys
from github import Github
from google import genai

def main():
    # 1. Recupera le variabili d'ambiente passate dalla GitHub Action
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    repo_name = os.environ.get("GITHUB_REPOSITORY") # Es: "tuo-utente/tuo-repo"
    pr_number_str = os.environ.get("PR_NUMBER")

    # Verifica che tutte le variabili siano presenti
    if not all([github_token, gemini_api_key, repo_name, pr_number_str]):
        print("Errore: Variabili d'ambiente mancanti. Controlla il workflow YAML.")
        sys.exit(1)
        
    pr_number = int(pr_number_str)

    # 2. Inizializza i client di GitHub e Gemini
    gh = Github(github_token)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    client = genai.Client(api_key=gemini_api_key)

    # 3. Estrai le modifiche (Diff)
    print("Recupero le modifiche della PR...")
    diff_text = ""
    for file in pr.get_files():
        # Ignora file generati automaticamente o troppo pesanti che consumerebbero solo token
        if file.filename.endswith(("package-lock.json", "yarn.lock", "poetry.lock")):
            continue
        
        # file.patch contiene il diff effettivo (+ aggiunte, - rimozioni)
        if file.patch:
            diff_text += f"--- File: {file.filename} ---\n{file.patch}\n\n"

    if not diff_text.strip():
        print("Nessuna modifica testuale trovata (es. solo file binari o di lock). Esco.")
        sys.exit(0)

    # 4. Prepara il prompt per Gemini
    prompt = f"""
    Agisci come un Senior Software Engineer. Il tuo compito è fare una code review della seguente Pull Request.
    
    Istruzioni:
    1. Trova eventuali bug evidenti o vulnerabilità di sicurezza.
    2. Suggerisci miglioramenti per la clean architecture, la leggibilità o le performance.
    3. Se vedi buone pratiche, menzionale brevemente.
    4. Evita commenti pignoli o pedanti (nitpicking) su stile o formattazione, concentrati sulla logica.
    5. Sii conciso, professionale e formatta la risposta in Markdown in modo che sia facilmente leggibile su GitHub.
    
    Ecco le modifiche del codice (formato diff):
    {diff_text}
    """

    # 5. Invia il prompt a Gemini
    print("Analisi del codice con Gemini in corso...")
    try:
        # Usiamo gemini-2.5-flash perché è veloce, economico e perfetto per analisi di testo/codice
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        review_comment = response.text
    except Exception as e:
        print(f"Errore durante la chiamata alle API di Gemini: {e}")
        sys.exit(1)

    # 6. Pubblica il commento su GitHub
    print("Pubblicazione della review sulla PR...")
    try:
        # Aggiungiamo un'intestazione per far capire ai dev che è un commento generato dall'AI
        final_comment = f"🤖 **Gemini AI Review**\n\n{review_comment}"
        pr.create_issue_comment(final_comment)
        print("Review pubblicata con successo!")
    except Exception as e:
        print(f"Errore durante la pubblicazione del commento su GitHub: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()