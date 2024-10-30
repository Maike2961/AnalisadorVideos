from pytubefix import YouTube
from groq import Groq
from dotenv import load_dotenv
import ffmpeg
import os

load_dotenv()

groq_client = Groq(api_key=os.getenv('API_KEY'))


def Download(link):
    print("Downloading...")
    ytObj = YouTube(link)
    try:
        audio_path = f"Audios/{ytObj.title}.mp3"
        os.makedirs("Audios", exist_ok=True)
        stream_url = ytObj.streams[0].url
        audio, _ = (
            ffmpeg
            .input(stream_url)
            .output("pipe:", format='mp3',  
                    acodec='libmp3lame', 
                    ar='22050',  
                    ac=1, 
                    loglevel="error")  
            .run(capture_stdout=True)
        )
        with open(audio_path, 'wb') as f:
            f.write(audio)
            
        print("Download Concluido")
        
        return audio_path
    except Exception as e:
        print(e)
        return None

def transcribe_audio(audioFile):
    print("Transfigurando audio para texto...")
    try:
        with open(audioFile, 'rb') as audio:
            transcript = groq_client.audio.transcriptions.create(
            file=(audioFile, audio.read()),
            model="whisper-large-v3", 
            temperature=0.0
            )
        return transcript
    except Exception as e:
        print(e)
        return None
    
def resume_text(text):
    print("Resumindo o texto...")
    try:
        response = groq_client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Voce é uma amigável assistente que faz resumo de texto"},
                {
                    "role": "user", "content": f"Por favor, faça um resumo desse texto: \n\n {text}",
                },
            ],
            model="llama3-8b-8192",
            temperature=0,
        )
        summary = response.choices[0].message.content
        return summary
        
    except Exception as e:
        print(e)
        return None


if "__main__" == __name__:
    link = input("Digite o link para Download: ")
    
    audio_path = Download(link)
    if not audio_path:
        print("Erro ao baixar o áudio.")
    
    transcript = transcribe_audio(audio_path)
    if not transcript:
        print("Erro na transcrição do áudio com Groq.")
    
    summary = resume_text(transcript)
    
    if summary:
        open("summary.md", 'w', encoding='utf-8').write(summary)
        print("Concluido...")
        
    
    
        
