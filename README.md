Gym Stats

Este projeto é uma aplicação web construída com Flask, visando o público amante de musculação, que permite aos usuários registrar e fazer login, postar imagens, avaliar postagens de outros usuários e responder a perguntas de múltipla escolha sobre musculação. A aplicação utiliza padrões de design Strategy e Factory Method para gerar perguntas sobre musculação, com diferentes níveis de complexidade, incluindo a integração com a API OpenAI para gerar perguntas mais avançadas.

Funcionalidades
  Autenticação de Usuário:  
    Registro de novos usuários.
    Login e logout de usuários existentes.

 Postagens:
   Upload de imagens.
    Visualização de postagens.
    Avaliação de postagens.

 Quiz de Musculação:
   Geração de perguntas sobre musculação com múltiplas estratégias (básica, avançada e utilizando a API OpenAI).
   Verificação de respostas corretas e navegação para uma página de plano de treino em caso de acerto.

 Decoradores:
   Medição e registro do tempo de execução de determinadas rotas.

Pré-requisitos
   Python 3.8 ou superior
   Flask
   SQLAlchemy
   OpenAI API Key
   
Uso
  Registro e Login:
    Acesse a página inicial e registre-se com um novo nome de usuário e senha.
    Faça login com as credenciais registradas.
    
Postagens:
  Faça upload de imagens na página de upload.
  Visualize e avalie as postagens.
  
Quiz de Musculação:
  Acesse a página do quiz para responder perguntas sobre musculação.
  Se acertar a pergunta, você será redirecionado para uma página de plano de treino.
  
Estrutura do Código
factories.py
  Padrão Strategy:
    QuestionStrategy: Interface abstrata para estratégias de geração de perguntas.
    BasicMuscleQuestionStrategy, AdvancedMuscleQuestionStrategy, OpenAIMuscleQuestionStrategy: Implementações concretas da interface QuestionStrategy.

  Padrão Factory Method:
    QuestionFactory: Classe abstrata para a fábrica de perguntas.
    MuscleQuestionFactory: Implementação concreta da fábrica, usando uma estratégia de geração de perguntas.
  
  Padrão Decorator:
    log_execution_time: Decorador para registrar o tempo de execução de funções.
    
app.py
  Configuração do Flask:
  Configuração do banco de dados, upload de arquivos, e chave de API OpenAI.
  Definição das rotas da aplicação.
  Integração das estratégias de geração de perguntas.
  templates
  
Templates HTML:
  auth.html: Template para login e registro de usuários.
  homePage.html: Template para a página principal com postagens e quiz.
  workout_plan.html: Template privativo para exibir o plano de treino (apenas se responder corretamente ao quiz).
