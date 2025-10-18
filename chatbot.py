#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chatbot de IA em Python
Desenvolvido com interface moderna e funcionalidades avançadas
"""

import os
import json
import datetime
from typing import List, Dict, Any
import openai
from flask import Flask, render_template, request, jsonify
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatbotIA:
    def __init__(self, api_key: str = None):
        """
        Inicializa o chatbot com configurações básicas
        """
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if self.api_key:
            openai.api_key = self.api_key
        
        self.conversation_history = []
        self.max_history = 10
        self.system_prompt = """
        Você é um assistente de IA útil e amigável. 
        Responda de forma clara, concisa e educada.
        Sempre tente ser útil e fornecer informações precisas.
        """
        
    def add_to_history(self, role: str, content: str):
        """Adiciona mensagem ao histórico da conversa"""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        # Mantém apenas as últimas mensagens
        if len(self.conversation_history) > self.max_history * 2:
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
    
    def get_response(self, user_message: str) -> str:
        """
        Gera resposta usando OpenAI GPT
        """
        try:
            self.add_to_history("user", user_message)
            
            # Prepara mensagens para a API
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Adiciona histórico recente
            for msg in self.conversation_history[-6:]:  # Últimas 6 mensagens
                if msg["role"] in ["user", "assistant"]:
                    messages.append({
                        "role": msg["role"],
                        "content": msg["content"]
                    })
            
            # Chama a API OpenAI
            if self.api_key:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    max_tokens=500,
                    temperature=0.7
                )
                
                ai_response = response.choices[0].message.content.strip()
            else:
                # Resposta padrão quando não há API key
                ai_response = self.get_fallback_response(user_message)
            
            self.add_to_history("assistant", ai_response)
            return ai_response
            
        except Exception as e:
            logger.error(f"Erro ao gerar resposta: {e}")
            return "Desculpe, ocorreu um erro ao processar sua mensagem. Tente novamente."
    
    def get_fallback_response(self, user_message: str) -> str:
        """
        Respostas básicas quando não há conexão com IA
        """
        user_message_lower = user_message.lower()
        
        responses = {
            "oi": "Olá! Como posso ajudá-lo hoje?",
            "olá": "Oi! Em que posso ser útil?",
            "como vai": "Estou bem, obrigado! E você?",
            "tchau": "Até logo! Foi um prazer conversar com você.",
            "obrigado": "De nada! Fico feliz em ajudar.",
            "ajuda": "Estou aqui para ajudar! Faça uma pergunta ou conte o que precisa.",
        }
        
        for key, response in responses.items():
            if key in user_message_lower:
                return response
        
        return "Interessante! Conte-me mais sobre isso. (Nota: Configure sua API key para respostas mais inteligentes)"
    
    def clear_history(self):
        """Limpa o histórico da conversa"""
        self.conversation_history = []
    
    def save_conversation(self, filename: str = None):
        """Salva a conversa em arquivo JSON"""
        if not filename:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversa_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.conversation_history, f, ensure_ascii=False, indent=2)
            return f"Conversa salva em {filename}"
        except Exception as e:
            return f"Erro ao salvar conversa: {e}"

# Aplicação Flask para interface web
app = Flask(__name__)
chatbot = ChatbotIA()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message.strip():
            return jsonify({'error': 'Mensagem vazia'}), 400
        
        response = chatbot.get_response(user_message)
        
        return jsonify({
            'response': response,
            'timestamp': datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro no endpoint /chat: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@app.route('/history')
def get_history():
    return jsonify(chatbot.conversation_history)

@app.route('/clear', methods=['POST'])
def clear_history():
    chatbot.clear_history()
    return jsonify({'message': 'Histórico limpo com sucesso'})

if __name__ == '__main__':
    print("🤖 Iniciando Chatbot de IA...")
    print("📝 Configure sua OPENAI_API_KEY para funcionalidade completa")
    print("🌐 Acesse: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)