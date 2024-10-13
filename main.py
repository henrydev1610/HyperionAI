import os
import streamlit as st
from dotenv import load_dotenv
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()


groq_api_key = os.environ.get('GROQ_API_KEY')

if not groq_api_key:
    st.error("A variável de ambiente 'GROQ_API_KEY' não está definida.")
    st.stop()

def main():
    st.title('Hyperion AI chat-bot 🤖')
    st.sidebar.title("Selecione uma LLM")     
    
    model = st.sidebar.selectbox(
        'Escolha um modelo',
        ['Mixtral-8x7b-32768', 'llama3-8b-8192']
    )
    
    conversation_memory_length = st.sidebar.slider('Tamanho da Resposta:', 1, 10, value=5)
    
    memory = ConversationBufferMemory(k=conversation_memory_length)
    
    # Caixa de texto para a pergunta do usuário
    user_question = st.text_area('Faça uma pergunta...')
    
    # Botão para enviar a pergunta
    if st.button('Pesquisar'):
        if user_question.strip() == "":
            st.warning("Por favor, insira uma pergunta antes de pesquisar.")
        else:
            # Inicializa o histórico do chat na sessão
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            else:
                for message in st.session_state.chat_history:
                    memory.save_context({'input': message['human']}, {'output': message['AI']})
            
            # Inicializa o ChatGroq com a API key e o modelo selecionado
            groq_chat = ChatGroq(
                groq_api_key=groq_api_key,
                model_name=model
            )
            
            # Definir o template do prompt
            prompt_template = PromptTemplate(
                input_variables=["history", "input"],
                template="""
                Você é um assistente de inteligência artificial que responde em Português Brasileiro.
                Histórico de Conversa:
                {history}
                Pergunta do Usuário:
                {input}
                Resposta em Português Brasileiro:
                """
                            )
            
            # Configura a cadeia de conversação com a LLM, a memória e o prompt personalizado
            conversation = ConversationChain(
                llm=groq_chat,
                memory=memory,
                prompt=prompt_template 
            )
            
            try:
                # Gera a resposta da LLM
                response = conversation.run(user_question)
                
                # Verifica se a resposta é uma string ou um dicionário
                if isinstance(response, dict) and 'response' in response:
                    resposta_texto = response['response']
                else:
                    resposta_texto = response  # Assume que response é uma string
                
                # Adiciona a mensagem ao histórico
                message = {'human': user_question, 'AI': resposta_texto}
                st.session_state.chat_history.append(message)
                
                # Exibe a resposta do chatbot
                st.write('**Hyperion AI:**', resposta_texto)
            except Exception as e:
                st.error(f"Ocorreu um erro ao processar a sua pergunta: {e}")

if __name__ == '__main__':
    main()
