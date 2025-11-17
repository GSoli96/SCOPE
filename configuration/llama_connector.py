from ollama import chat, ChatResponse
from typing import Optional

class OllamaClient:
    """
    Classe per interagire con il modello LLM di Ollama.
    Other Models here: https://ollama.com/search
    """
    MODEL_NAME = 'llama3.2'  # Nome del modello di default

    def __init__(self, model_name: Optional[str] = None):
        """
        Inizializza il client Ollama.

        Args:
            model_name: (Opzionale) Il nome del modello da utilizzare. Se non fornito, usa MODEL_NAME di default.
        """
        self.model_name = model_name or self.MODEL_NAME #se viene passato un model_name lo usa, altrimenti usa quello di default.

    def get_response(self, prompt: str) -> Optional[ChatResponse]:
        """
        Invia un prompt al modello e restituisce la risposta.

        Args:
            prompt: Il prompt da inviare.

        Returns:
            Un oggetto ChatResponse contenente la risposta, o None in caso di errore.
        """
        try:
            response: ChatResponse = chat(model=self.model_name, messages=[
                {'role': 'user', 'content': prompt},
            ])
            return response
        except Exception as e: #gestione delle eccezioni più generica
            print(f"Errore durante la comunicazione con Ollama: {e}")
            return None

    def get_content_from_response(self, response: Optional[ChatResponse]) -> Optional[str]:
        """
        Estrae il contenuto testuale dalla risposta di Ollama.

        Args:
            response: L'oggetto ChatResponse.

        Returns:
            Il contenuto testuale della risposta, o None se la risposta è None o se non contiene un messaggio valido.
        """
        if response and response.message and response.message.content:
            return response.message.content
        return None

# if __name__ == '__main__':
#   # Esempio di utilizzo:
#   import os

#   percorso_html_input = os.getcwd() + 'Potential_target\\Giuseppe Polese\\googlelens\\page_3.html'  # Sostituisci con il percorso del tuo file HTML
#   client = OllamaClient(model_name="llama3.2")

#   google = GoogleLensFinder()
#   testo_estratto_esempio = google.extract_text_from_html_page(percorso_html_input)
#   print(testo_estratto_esempio)

#   if testo_estratto_esempio:
#     llm_response = client.get_response(f"Analyze the content of the following text. Give me all the information about the person: {testo_estratto_esempio}")
#     print(llm_response['message']['content'])