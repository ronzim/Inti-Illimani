import os
import sys
import json
from github import Github, Auth
from google import genai

def main():
    # 1. Recupera Variabili
    github_token = os.environ.get("GITHUB_TOKEN")
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    repo_name = os.environ.get("GITHUB_REPOSITORY")
    pr_number_str = os.environ.get("PR_NUMBER")

    if not all([github_token, gemini_api_key, repo_name, pr_number_str]):
        print("Errore: Variabili d'ambiente mancanti. Controlla il workflow YAML.")
        sys.exit(1)
        
    pr_number = int(pr_number_str)

    # 2. Inizializza GitHub (Risolto il DeprecationWarning)
    auth = Auth.Token(github_token)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    
    client = genai.Client(api_key=gemini_api_key)

    # 3. Estrai le modifiche (Diff)
    print("Recupero le modifiche della PR...")
    diff_text = ""
    for file in pr.get_files():
        if file.filename.endswith(("package-lock.json", "yarn.lock", "poetry.lock")):
            continue
        if file.patch:
            diff_text += f"--- File: {file.filename} ---\n{file.patch}\n\n"

    if not diff_text.strip():
        print("Nessuna modifica rilevante da analizzare.")
        sys.exit(0)

    # 4. Nuovo Prompt per forzare una risposta in formato JSON
    prompt = f"""
Agisci come un Senior Software Engineer e fai una code review della seguente Pull Request.

Restituisci la tua risposta ESCLUSIVAMENTE in un formato JSON valido con questa esatta struttura, senza aggiungere testo fuori dal JSON:
{{
  "summary": "Un riassunto generale della PR, spiegando le modifiche principali.",
  "inline_comments": [
    {{
      "path": "percorso/del/file.estensione",
      "line": numero_di_riga_intero,
      "comment": "Il tuo suggerimento o feedback per questa specifica riga."
    }}
  ]
}}

Regole per il JSON:
1. 'summary': scrivi una panoramica utile per chi legge la PR.
2. 'inline_comments': commenti SOLO per bug, sicurezza, o miglioramenti. Lascia vuoto [] se il codice è perfetto.
3. 'line': cerca di dedurre il numero di riga effettivo in cui si trova la modifica (usa i numeri del diff).
4. Sii sintetico e professionale nei commenti.

Ecco il codice (diff):
{diff_text}
"""

    # 5. Chiama Gemini e fa il parsing del JSON
    print("Analisi del codice con Gemini in corso...")
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        
        # Pulizia della risposta (a volte Gemini avvolge il JSON nei backtick del markdown)
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3]
        elif raw_text.startswith("```"):
            raw_text = raw_text[3:-3]
            
        data = json.loads(raw_text.strip())
    except Exception as e:
        print(f"Errore API Gemini o parsing JSON fallito: {e}")
        # Stampiamo la risposta raw per capire perché il parsing JSON è fallito
        print(f"Risposta ricevuta:\n{response.text}")
        sys.exit(1)

    summary = data.get("summary", "Nessun riassunto generato.")
    inline_comments = data.get("inline_comments", [])
    
    # Per commentare riga per riga, ci serve l'ID dell'ultimo commit della PR
    commits = list(pr.get_commits())
    last_commit = commits[-1]
    
    failed_inline_comments = []
    
    # 6. Tentiamo di pubblicare i commenti INLINE (nel codice)
    print(f"Trovati {len(inline_comments)} commenti inline. Tento la pubblicazione...")
    for comment in inline_comments:
        try:
            path = comment.get("path")
            line = comment.get("line")
            body = comment.get("comment")
            
            if not all([path, line, body]):
                continue
                
            pr.create_review_comment(
                body=f"🤖 **Gemini AI:** {body}",
                commit_id=last_commit,
                path=path,
                line=int(line),
                side="RIGHT" # Indica le modifiche nel nuovo file
            )
            print(f"  -> Successo: Commento aggiunto su {path} riga {line}")
        except Exception as e:
            # L'API di GitHub restituisce errore se la riga indicata non è parte del diff.
            print(f"  -> Fallito: Impossibile aggiungere su {path}:{line}. Lo sposto nel riassunto. ({e})")
            failed_inline_comments.append(comment)

    # 7. Pubblichiamo il RIASSUNTO GENERALE (nella conversazione)
    main_review_body = f"🤖 **Gemini AI Review Summary**\n\n{summary}\n"
    
    # Se alcuni commenti inline sono falliti, li accodiamo qui per non perderli
    if failed_inline_comments:
        main_review_body += "\n---\n### ⚠️ Feedback Aggiuntivi (Generali o file non mappabili):\n"
        for fc in failed_inline_comments:
            main_review_body += f"- **File:** `{fc.get('path')}` (Circa riga {fc.get('line')}): {fc.get('comment')}\n"

    print("Pubblicazione del riassunto generale sulla PR...")
    try:
        # Usiamo 'create_review' invece di un semplice commento, così GitHub lo evidenzia
        # in modo chiaro come "Review" e manda notifiche migliori.
        pr.create_review(
            body=main_review_body,
            event="COMMENT" 
        )
        print("Workflow completato con successo!")
    except Exception as e:
        print(f"Errore durante la pubblicazione del riassunto principale: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()