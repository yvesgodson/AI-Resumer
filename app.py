from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/resume', methods=['POST'])
def resume():
    print("=== Début de la requête API ===")
    try:
        data = request.get_json()
        print(f"Données reçues: {data}")

        if not data:
            print("Erreur: Aucune donnée JSON reçue")
            return jsonify({'erreur': 'Aucune donnée reçue'}), 400

        texte = data.get('texte', '')
        print(f"Texte à résumer (longueur: {len(texte)}): {texte[:100]}...")

        if len(texte) < 100:
            print("Erreur: Texte trop court")
            return jsonify({'erreur': 'Le texte doit contenir au moins 100 caractères.'}), 400

        payload = {
            "model": "gemma3",
            "prompt": f"Résume ce texte : {texte}",
            "stream": False
        }

        print("Envoi de la requête à Ollama...")
        try:
            response = requests.post("http://localhost:11434/api/generate", json=payload, timeout=30)
            print(f"Statut de réponse Ollama: {response.status_code}")

            if response.status_code != 200:
                print(f"Erreur Ollama: {response.text}")
                return jsonify({'erreur': 'Erreur du service IA'}), 500

            result = response.json()
            print(f"Réponse Ollama: {result}")

            resume_text = result.get('response', 'Pas de résumé généré')
            print(f"Résumé généré: {resume_text}")

            return jsonify({'resume': resume_text})

        except requests.exceptions.RequestException as e:
            print(f"Erreur de connexion à Ollama: {e}")
            return jsonify({'erreur': 'Impossible de contacter le service IA. Vérifiez qu\'Ollama est démarré.'}), 500

    except Exception as e:
        print(f"Erreur générale: {e}")
        return jsonify({'erreur': 'Erreur serveur interne'}), 500

if __name__ == '__main__':
    app.run(debug=True)
