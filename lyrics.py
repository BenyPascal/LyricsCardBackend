from lyricsgenius import Genius

token = "XjeLxMdBUlCOuaTW7D697D89-UeQBU43ZP2K2jVkVf2Ae2cBobsEzwS_lDwkuCsB"
genius = Genius(token)

# Recherchez la chanson par titre et artiste
chanson = genius.search_song("Scopolamine", "Femtogo")
def lyrics(artiste, titre):
    chanson = genius.search_song(titre, artiste)
    if chanson:
        # Récupérer les informations souhaitées
        informations_chanson = {
            "titre": chanson.title,
            "artiste": chanson.artist,
            "paroles": chanson.lyrics,
            "image_url": chanson.song_art_image_url
        }

        # Afficher le résultat en format JSON
        import json
        print(json.dumps(informations_chanson, indent=4, ensure_ascii=False))
    else:
        print("Chanson non trouvée.")


