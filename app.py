from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

import lyricsgenius

app = Flask(__name__)
CORS(app)

# Remplacez 'votre_token_d_acces' par votre jeton d'accès Genius
genius = lyricsgenius.Genius('XjeLxMdBUlCOuaTW7D697D89-UeQBU43ZP2K2jVkVf2Ae2cBobsEzwS_lDwkuCsB')

@app.route('/api/lyrics', methods=['GET'])
def get_lyrics():
    artist = request.args.get('artist')
    song = request.args.get('song')

    if not artist or not song:
        return jsonify({'error': 'Les paramètres "artist" et "song" sont requis.'}), 400

    try:
        song_data = genius.search_song(song, artist)
        if song_data:
            lyrics_lines = song_data.lyrics.split('\n')
            response = {
                'artist': song_data.artist,
                'song': song_data.title,
                'lyrics': lyrics_lines,
                'albumImage': song_data.song_art_image_url
            }
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Chanson non trouvée.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import lyricsgenius
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Remplacez 'votre_token_d_acces' par votre jeton d'accès Genius
genius = lyricsgenius.Genius('XjeLxMdBUlCOuaTW7D697D89-UeQBU43ZP2K2jVkVf2Ae2cBobsEzwS_lDwkuCsB')

@app.route('/api/lyrics', methods=['GET'])
def get_lyrics():
    artist = request.args.get('artist')
    song = request.args.get('song')

    if not artist or not song:
        return jsonify({'error': 'Les paramètres "artist" et "song" sont requis.'}), 400

    try:
        song_data = genius.search_song(song, artist)
        if song_data:
            lyrics_lines = song_data.lyrics.split('\n')
            response = {
                'artist': song_data.artist,
                'song': song_data.title,
                'lyrics': lyrics_lines,
                'albumImage': song_data.song_art_image_url
            }
            return jsonify(response), 200
        else:
            return jsonify({'error': 'Chanson non trouvée.'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_image(background_url, artist_name, song_title, selected_lyrics):
    try:
        # Télécharger l'image de fond
        response = requests.get(background_url)
        background = Image.open(BytesIO(response.content)).convert("RGB")

        # Définir les dimensions de l'image finale
        width, height = background.size
        bar_height = 100
    
        # Calcul dynamique de la hauteur de la boîte des paroles
        try:
            font = ImageFont.truetype("arial.ttf", 30)
        except IOError:
            font = ImageFont.load_default()

        line_spacing = 10
        wrapped_lyrics = []
        max_line_width = width - 80

        for line in selected_lyrics:
            words = line.split()  # Découpe la ligne en mots
            new_line = ""

            for word in words:
                # Teste si le mot ajouté dépasse la largeur max
                test_line = new_line + " " + word if new_line else word
                if font.getlength(test_line) <= max_line_width:
                    new_line = test_line  # Ajoute le mot
                else:
                    wrapped_lyrics.append(new_line)  # Ajoute la ligne complète
                    new_line = word  # Commence une nouvelle ligne

            if new_line:
                wrapped_lyrics.append(new_line)  # Ajoute la dernière ligne
        

        lyric_box_height = (font.getbbox('A')[1] + line_spacing) * len(wrapped_lyrics) + 20
        total_height = height  # Garde la hauteur initiale de l'image de fond

        # Utiliser l'image de fond directement
        final_image = background.copy()
        draw = ImageDraw.Draw(final_image)

        # Ajouter les paroles avec des rectangles blancs transparents
        padding_x = 50
        padding_y = 2
        text_y_position = total_height - bar_height - len(wrapped_lyrics)* 36 - 60
        for line in wrapped_lyrics:
            text_width, text_height = draw.textlength(line, font=font), 36
            draw.rectangle(
                [
                    (padding_x, text_y_position - padding_y),
                    (padding_x + text_width + 6, text_y_position + text_height + padding_y)
                ],
                fill="white"
            )
            draw.text((padding_x + 4, text_y_position), line, fill="black", font=font)
            text_y_position += text_height + padding_y * 2 + line_spacing

        # Ajouter la barre noire avec le nom de l'artiste et de la chanson (aligné à gauche)
        draw.rectangle([(0, height - bar_height - 2), (width, height)], fill="white")

        # Ajouter la barre noire avec le nom de l'artiste et de la chanson (aligné à gauche)
        draw.rectangle([(0, height - bar_height), (width, height)], fill="black")
        text = f"{artist_name} - {song_title}"
        draw.text((50, height - bar_height + (bar_height - font.getbbox(text)[1]) / 2), text, fill="white", font=font)

        # Sauvegarder l'image temporairement
        output_path = "generated_image.jpg"
        final_image.save(output_path, "JPEG")

        return output_path

    except Exception as e:
        print(f"Erreur lors de la génération de l'image : {e}")
        return None

@app.route('/generate_image', methods=['POST'])
def generate_image_endpoint():
    data = request.get_json()
    artist = data.get('artist')
    song = data.get('song')
    lyrics = data.get('lyrics')
    album_image = data.get('albumImage')

    if not all([artist, song, lyrics, album_image]):
        return jsonify({'error': 'Données manquantes.'}), 400

    image_path = generate_image(album_image, artist, song, lyrics)

    if image_path:
        return send_file(image_path, mimetype='image/jpeg', as_attachment=True, download_name='generated_image.jpg')
    else:
        return jsonify({'error': "Erreur lors de la génération de l'image."}), 500

if __name__ == "__main__":
    from os import environ
    app.run(host="0.0.0.0", port=int(environ.get("PORT", 5000)))

