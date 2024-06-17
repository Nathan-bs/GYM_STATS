from abc import ABC, abstractmethod
import openai

#Strategy (Padrão de Projeto Comportamental)
class QuestionStrategy(ABC):
    @abstractmethod
    def create_question(self):
        pass

#Implementação com Strategy para questões mais básicas
class BasicMuscleQuestionStrategy(QuestionStrategy):
    def create_question(self):
        question = "Qual é o principal músculo utilizado no exercício de supino?"
        options = ["Peitoral", "Bíceps", "Tríceps", "Deltoide"]
        correct_answer = "Peitoral"
        return question, options, correct_answer

#Implementação com Strategy para questões avançadas
class AdvancedMuscleQuestionStrategy(QuestionStrategy):
    def create_question(self):
        question = "Qual é a principal ação do músculo latíssimo do dorso?"
        options = ["Flexão", "Extensão", "Adução", "Rotação"]
        correct_answer = "Adução"
        return question, options, correct_answer

# Implementação da Estratégia de Perguntas com API do OpenAI
class OpenAIMuscleQuestionStrategy(QuestionStrategy):
    def create_question(self):
        prompt = "Crie uma pergunta média/difícil sobre musculação com 4 opções de respostas e indique a resposta correta no formato 'pergunta|opção1|opção2|opção3|opção4|resposta_correta'."
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um gerador de perguntas de múltipla escolha."},
                {"role": "user", "content": prompt}
            ]
        )
        content = response.choices[0].message["content"]
        
        parts = content.split('|')
        if len(parts) != 6:
            raise ValueError("A resposta da API não está no formato esperado.")
        
        question = parts[0]
        options = parts[1:5]
        correct_answer = parts[5]
        return question, options, correct_answer

#Factory Method (Padrão de Projeto Criacional)
class QuestionFactory(ABC):
    @abstractmethod
    def create_question(self):
        pass

class MuscleQuestionFactory(QuestionFactory):
    def __init__(self, strategy: QuestionStrategy):
        self._strategy = strategy

    def create_question(self):
        return self._strategy.create_question()
