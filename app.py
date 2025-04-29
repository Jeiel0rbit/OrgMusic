import os
import sys
from mutagen import File
from mutagen.id3 import ID3NoHeaderError

def sanitize_filename(filename):
    invalid_chars = '\\/:*?"<>|'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    filename = filename.replace(' ', '_')
    return filename.strip()

def rename_mp3_files(directory):
    if not os.path.isdir(directory):
        print(f"Erro: O caminho '{directory}' não é um diretório válido.")
        return

    print(f"Iniciando renomeação dos arquivos MP3 em '{directory}'...")
    failed_files = []

    for root, _, files in os.walk(directory):
        for filename in files:
            if filename.lower().endswith('.mp3'):
                old_path = os.path.join(root, filename)
                artist = None
                title = None

                try:
                    audio = File(old_path)

                    # Tenta obter as tags comuns de Artista e Título
                    artist = audio.get('artist', audio.get('TPE1'))
                    title = audio.get('title', audio.get('TIT2'))

                    # Garante que o resultado é uma string (mutagen pode retornar listas)
                    if isinstance(artist, list): artist = artist[0] if artist else None
                    if isinstance(title, list): title = title[0] if title else None

                    # Verifica se as tags foram encontradas e não estão vazias
                    if not artist or not str(artist).strip() or not title or not str(title).strip():
                         print(f"Aviso: Tags Artista/Título ausentes ou vazias para '{filename}'. Pulando renomeação deste arquivo.")
                         failed_files.append(old_path)
                         continue # Pula para o próximo arquivo

                    sanitized_artist = sanitize_filename(str(artist))
                    sanitized_title = sanitize_filename(str(title))

                    # Garante que os nomes não ficaram vazios após sanitização
                    if not sanitized_artist: sanitized_artist = "Unknown_Artist"
                    if not sanitized_title: sanitized_title = "Unknown_Title"


                    new_filename = f"{sanitized_artist}-{sanitized_title}.mp3"
                    new_path = os.path.join(root, new_filename)

                    if os.path.normcase(old_path) == os.path.normcase(new_path):
                        print(f"Pulando '{filename}': Nome já está no formato correto.")
                        continue

                    if os.path.exists(new_path):
                         print(f"Pulando '{filename}': Já existe um arquivo com o nome de destino '{new_filename}'.")
                         continue

                    os.rename(old_path, new_path)
                    print(f"Renomeado '{filename}' para '{new_filename}'")

                except ID3NoHeaderError:
                    print(f"Aviso: Não foi possível ler as tags ID3 (sem cabeçalho válido) para '{filename}'. Pulando renomeação.")
                    failed_files.append(old_path)
                except Exception as e:
                    print(f"Erro inesperado ao processar '{filename}': {e}. Pulando renomeação.")
                    failed_files.append(old_path)

    print("\nProcesso de renomeação concluído.")
    if failed_files:
        print("\nOs seguintes arquivos não puderam ser renomeados porque as tags Artista/Título estão ausentes ou houve um erro:")
        for f in failed_files:
            print(f"- {f}")
        print("\nPor favor, use um editor de tags (como Mp3tag, Picard, etc.) para adicionar ou corrigir as tags desses arquivos e execute o script novamente.")


if __name__ == "__main__":
    target_directory = input("Por favor, digite o caminho para a pasta (ex: E:\\Music) ou a letra da unidade do pendrive: ")

    if len(target_directory) == 1 and target_directory.isalpha():
         drive_path = f"{target_directory.upper()}:\\"
         if os.path.isdir(drive_path):
             target_directory = drive_path
         else:
             print(f"Erro: A unidade '{drive_path}' não foi encontrada ou não é acessível.")
             sys.exit(1)
    elif not os.path.isdir(target_directory):
         print(f"Erro: O caminho '{target_directory}' não é um diretório válido.")
         sys.exit(1)


    rename_mp3_files(target_directory)
