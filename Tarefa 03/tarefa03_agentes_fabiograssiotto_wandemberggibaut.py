from typing import Dict, List
from autogen import ConversableAgent, AssistantAgent
import sys
import os
import math

def fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]:
    # TODO
    # Esta função recebe o nome de um restaurante e retorna as avaliações desse restaurante.
    # A saída deve ser um dicionário, onde a chave é o nome do restaurante e o valor é uma lista de avaliações desse restaurante.
    # O "agente de busca de dados" deve ter acesso à assinatura desta função e deve ser capaz de sugeri-la como uma chamada de função.
    # Exemplo:
    # > fetch_restaurant_data("Estação Barão")
    # {"Estação Barão's": ["A comida do Estação Barão foi mediana, sem nada particularmente marcante.", ...]}

    # Dicionátio que armazena o nome do restaurante e suas avaliações
    restaurant_reviews = {}
    current_restaurant = None

    # Abre o arquivo restaurantes.txt e cria estrutura para armazenar os dados
    with open('restaurantes.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            # Divide a linha pelo primeiro ponto encontrado
            parts = line.split('.', 1)
            if len(parts) == 2:
                current_restaurant, review = parts
                current_restaurant = current_restaurant.strip()
                review = review.strip()
                if current_restaurant not in restaurant_reviews:
                    restaurant_reviews[current_restaurant] = []
                restaurant_reviews[current_restaurant].append(review)

    # Retorna a review do restaurante
    return {restaurant_name: restaurant_reviews.get(restaurant_name, [])}


def calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]:
    # TODO
    # Esta função recebe o nome de um restaurante, uma lista de notas da comida (de 1 a 5) e uma lista de notas do atendimento ao cliente (de 1 a 5).
    # A saída deve ser uma pontuação entre 0 e 10, calculada da seguinte forma:
    # SUM(sqrt(food_scores[i]**2 * customer_service_scores[i]) * 1/(N * sqrt(125)) * 10
    # A fórmula acima é uma média geométrica das notas, que penaliza mais a qualidade da comida do que o atendimento ao cliente.
    # Exemplo:
    # > calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    # {"Applebee's": 5.048}
    # OBSERVAÇÃO: Certifique-se de que a pontuação inclui PELO MENOS 3 casas decimais. Os testes públicos só aceitarão pontuações 
    # que tenham no mínimo 3 casas decimais.

    # Sanity check das notas passadas como parâmetro
    if len(food_scores) != len(customer_service_scores):
        raise ValueError("As listas de notas de comida e atendimento ao cliente devem ter o mesmo comprimento.")

    # Número de avaliações
    N = len(food_scores)

    # Calcula a pontuação geral usando a fórmula fornecida
    overall_score = sum([math.sqrt(food_scores[i]**2 * customer_service_scores[i]) for i in range(N)]) * (1 / (N * math.sqrt(125))) * 10

    print("soma: +", sum([math.sqrt(food_scores[i]**2 * customer_service_scores[i]) for i in range(N)]))
    print("N: ", N)
    print("overall_score: ", overall_score)


    # Retorna a pontuação com pelo menos 3 casas decimais
    return {restaurant_name: round(overall_score, 3)}

def setup_llm():

    config_list = [
        {
            'model': 'gpt-4o-mini',
            'api_key': os.environ.get("OPENAI_API_KEY")
        },
    ]
    # É importante manter a temperatura entre 0-0.2 para resultados mais determinísticos.
    llm_config = {"config_list": config_list, "temperature": 0.2}
    return llm_config
    

# Não modifique a assinatura da função "main".
def main(user_query: str):

    entrypoint_agent_system_message = "Você é o agente de entrada responsável por iniciar a conversa. Uma vez que você receba a resposta de um agente, você deve encaminhar a resposta obtida para o próximo agente na cadeia."
    data_fetch_agent_system_message =  """
            Você é um agente responsável por buscar avaliações de restaurantes.
            Você pode buscar avaliações de um restaurante específico chamando a função `fetch_restaurant_data(restaurant_name: str) -> Dict[str, List[str]]`.
            A função recebe o nome de um restaurante como parâmetro e retorna um dicionário onde a chave é o nome do restaurante e o valor é uma lista de avaliações para esse restaurante.
            Exemplo: fetch_restaurant_data("Estação Barão")
        """
    review_analysis_agent_system_message =  """"
            Você é um agente responsável por analisar as avaliações de um restaurante e converter adjetivos em escores.
            Analise as avaliações e converta os adjetivos em escores conforme a seguinte escala:
            1: horrível, nojento, terrível.
            2: ruim, desagradável, ofensivo.
            3: mediano, sem graça, irrelevante.
            4: bom, agradável, satisfatório.
            5: incrível, impressionante, surpreendente.
            Retorne apenas com dois conjuntos de listas de notas de comida e atendimento ao cliente, cada lista com 5 notas no máximo.
            As notas vazias retorne com zeros.

            Exemplo de saída

            'Notas de comida: [4]  
             Notas de atendimento: [3]'
        """
    score_agent_system_message =  """
            Você é um agente responsável pelo cálculo final da pontuação de um restaurante.
            Você pode calcular a pontuação geral de um restaurante chamando a função `calculate_overall_score(restaurant_name: str, food_scores: List[int], customer_service_scores: List[int]) -> Dict[str, float]`.
            A função recebe o nome do restaurante, uma lista de notas da comida (de 1 a 5) e uma lista de notas do atendimento ao cliente (de 1 a 5) como parâmetros e retorna um dicionário onde a chave é o nome do restaurante e o valor é a pontuação geral do restaurante.
            Exemplo: calculate_overall_score("Applebee's", [1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
            Retorne apenas com a pontuação geral do restaurante.
        """

    # Groq setup
    llm_config = setup_llm()

    # O agente principal de entrada/supervisor
    
    entrypoint_agent = ConversableAgent("entrypoint_agent", 
                                        system_message=entrypoint_agent_system_message, 
                                        llm_config=llm_config,
                                        max_consecutive_auto_reply=1,
                                        human_input_mode='NEVER')

    

    # Criar o agente data_fetch_agent que seja responsável por recuperar avaliações
    # e estar ligado à função fetch_restaurant_data
    data_fetch_agent = AssistantAgent("data_fetch_agent", 
                                        system_message=data_fetch_agent_system_message, 
                                        llm_config=llm_config,
                                        human_input_mode='NEVER')
    
    
    #data_fetch_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    # Criar um agente review_analysis_agent que analisa as avaliações e converte
    # adjetivos em escores conforme a seguinte escala (não modificar esta escala, pois
    # ela afeta o cálculo final da pontuação):
    # a. 1/5: horrível, nojento, terrível.
    # b. 2/5: ruim, desagradável, ofensivo.
    # c. 3/5: mediano, sem graça, irrelevante.
    # d. 4/5: bom, agradável, satisfatório.
    # e. 5/5: incrível, impressionante, surpreendente.
    review_analysis_agent = AssistantAgent("review_analysis_agent", 
                                            system_message=review_analysis_agent_system_message, 
                                            llm_config=llm_config,
                                            max_consecutive_auto_reply=1,
                                            is_termination_msg=lambda msg: "notas de comida" in msg["content"].lower(),
                                            human_input_mode='NEVER')

    # Criar um agente score_agent que seja responsável pelo cálculo final da
    # pontuação, vinculado à função calculate_overall_score.

    score_agent = AssistantAgent("score_agent", 
                                    system_message=score_agent_system_message, 
                                    llm_config=llm_config,
                                    human_input_mode='NEVER')

    data_fetch_agent.register_for_llm(name="fetch_restaurant_data", description="Obtém as avaliações de um restaurante específico.")(fetch_restaurant_data)
    entrypoint_agent.register_for_execution(name="fetch_restaurant_data")(fetch_restaurant_data)

    score_agent.register_for_llm(name="calculate_overall_score", description="Realiza o cálculo final da pontuação do restaurante.")(calculate_overall_score)
    entrypoint_agent.register_for_execution(name="calculate_overall_score")(calculate_overall_score)

    # Iniciar a conversa a partir do agente de entrada.
    chat_results = entrypoint_agent.initiate_chats(
    [{
            "recipient": data_fetch_agent,
            "message": user_query,
            "clear_history": True,
            "silent": False,
            "max_turns": 2,
            "summary_method": "last_msg",
        },
        {
            "recipient": review_analysis_agent,
            "message": "Quantifique as avaliações do restaurante requisitado.",
            "max_turns": 1,
            "summary_method": "last_msg",
        },
        {
            "recipient": score_agent,
            "message": "Calcule a pontuação geral com base nos valores de comida e atendimento. O valor numérico deve ser arredondado para 3 casas decimais.",
            "max_turns": 2,
            "summary_method": "last_msg",
        }
    ])
    print(chat_results[-1].summary)

# NÃO modifique o código abaixo.
if __name__ == "__main__":
    assert len(sys.argv) > 1, "Certifique-se de incluir uma consulta para algum restaurante ao executar a função main."
    main(sys.argv[1])
